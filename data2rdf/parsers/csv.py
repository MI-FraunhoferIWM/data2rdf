"""CSV Parser for data2rdf"""

import os
import warnings
from io import StringIO
from typing import TYPE_CHECKING, Any
from urllib.parse import urljoin

import pandas as pd
from pydantic import Field, model_validator

from data2rdf.models.mapping import (
    ClassConceptMapping,
    PropertyMapping,
    QuantityMapping,
)
from data2rdf.utils import make_prefix
from data2rdf.warnings import MappingMissmatchWarning

from .base import DataParser
from .utils import _strip_unit, load_mapping_file

if TYPE_CHECKING:
    from typing import Dict


class CSVParser(DataParser):
    """
    Parses the csv file
    """

    header_sep: str = Field(..., description="Header separator")
    column_sep: str = Field(..., description="Column separator")
    metadata_length: int = Field(
        ..., description="Length of header with the metadata"
    )
    time_series_header_length: int = Field(
        2, description="Length of header of the time series"
    )

    @property
    def media_type(cls) -> str:
        """IANA Media type definition of the resource to be parsed."""
        return "http://www.iana.org/assignments/media-types/text/csv"

    @property
    def json_ld(cls) -> "Dict[str, Any]":
        """Return dict for json-ld for the graph"""

        tables = []

        if cls.general_metadata:
            meta_table = {
                "@type": "csvw:Table",
                "rdfs:label": "Metadata",
                "csvw:row": [],
            }

            for n, mapping in enumerate(cls.general_metadata):
                if isinstance(mapping, QuantityMapping):
                    row = {
                        "@type": "csvw:Row",
                        "csvw:titles": {
                            "@type": "xsd:string",
                            "@value": mapping.key,
                        },
                        "csvw:rownum": {"@type": "xsd:integer", "@value": n},
                        "qudt:quantity": mapping.json_ld,
                    }
                    meta_table["csvw:row"].append(row)
                elif isinstance(mapping, PropertyMapping):
                    row = {
                        "@type": "csvw:Row",
                        "csvw:titles": {
                            "@type": "xsd:string",
                            "@value": mapping.key,
                        },
                        "csvw:rownum": {"@type": "xsd:integer", "@value": n},
                        "csvw:describes": mapping.json_ld,
                    }
                    meta_table["csvw:row"].append(row)
                else:
                    raise TypeError(
                        f"Mapping must be of type {QuantityMapping} or {PropertyMapping}, not {type(mapping)}"
                    )
            tables += [meta_table]

        if cls.time_series_metadata:
            column_schema = {"@type": "csvw:Schema", "csvw:column": []}
            tables += [
                {
                    "@type": "csvw:Table",
                    "rdfs:label": "Time series data",
                    "csvw:tableSchema": column_schema,
                }
            ]
            for idx, mapping in enumerate(cls.time_series_metadata):
                if not isinstance(mapping, QuantityMapping):
                    raise TypeError(
                        f"Mapping must be of type {QuantityMapping}, not {type(mapping)}"
                    )

                if cls.config.data_download_uri:
                    download_url = {
                        "dcterms:identifier": {
                            "@type": "xsd:anyURI",
                            "@value": urljoin(
                                str(cls.config.data_download_uri),
                                f"column-{idx}",
                            ),
                        }
                    }
                else:
                    download_url = {}

                column = {
                    "@type": "csvw:Column",
                    "csvw:titles": {
                        "@type": "xsd:string",
                        "@value": mapping.key,
                    },
                    "qudt:quantity": mapping.json_ld,
                    "foaf:page": {
                        "@type": "foaf:Document",
                        "dcterms:format": {
                            "@type": "xsd:anyURI",
                            "@value": "https://www.iana.org/assignments/media-types/application/json",
                        },
                        "dcterms:type": {
                            "@type": "xsd:anyURI",
                            "@value": "http://purl.org/dc/terms/Dataset",
                        },
                        **download_url,
                    },
                }
                column_schema["csvw:column"].append(column)

        # flatten list if only one value exists
        if len(tables) == 1:
            tables = tables.pop()
        # make relation to csvw:table property
        if tables:
            csvw_tables = {"csvw:table": tables}
        else:
            csvw_tables = {}

        return {
            "@context": {
                "fileid": make_prefix(cls.config),
                "csvw": "http://www.w3.org/ns/csvw#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "dcat": "http://www.w3.org/ns/dcat#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
                "dcterms": "http://purl.org/dc/terms/",
                "qudt": "http://qudt.org/schema/qudt/",
                "csvw": "http://www.w3.org/ns/csvw#",
                "foaf": "http://xmlns.com/foaf/spec/",
            },
            "@id": "fileid:tableGroup",
            "@type": "csvw:TableGroup",
            **csvw_tables,
        }

    @model_validator(mode="after")
    @classmethod
    def run_parser(cls, self: "CSVParser") -> "CSVParser":
        """
        Parse metadata, time series metadata and time series
        """

        datafile: StringIO = cls._load_data_file(self)
        mapping: "Dict[str, ClassConceptMapping]" = load_mapping_file(
            self.mapping, self.config, ClassConceptMapping
        )
        time_series: pd.DataFrame = cls._parse_time_series(
            self, datafile
        ).dropna()
        datafile.seek(0)

        # iterate over general metadata
        header = ["key", "value", "unit"]
        self._general_metadata = []
        if self.metadata_length > 0:
            for l_count, line in enumerate(datafile.readlines()):
                # remove unneeded characters
                for char in self.config.remove_from_datafile:
                    line = line.replace(char, "")

                # merge with header keys
                row = line.split(self.header_sep)
                metadatum = dict(zip(header, row))

                # get the match from the mapping
                key = metadatum.get("key")
                mapping_match = mapping.get(key)

                # only map the data if a match is found
                if mapping_match:
                    # get unit
                    unit = mapping_match.unit or metadatum.get("unit") or None
                    if unit:
                        unit = _strip_unit(unit, self.config.remove_from_unit)

                    # instanciate model
                    model_data = {
                        "key": key,
                        "value": metadatum.get("value"),
                        "unit": unit,
                        "iri": mapping_match.iri,
                        "suffix": mapping_match.suffix,
                        "annotation": mapping_match.annotation or None,
                        "config": self.config,
                    }
                    if model_data.get("unit"):
                        model = QuantityMapping(**model_data)
                    else:
                        model = PropertyMapping(**model_data)
                    self._general_metadata.append(model)
                else:
                    warnings.warn(
                        f"No match found in mapping for key `{key}`",
                        MappingMissmatchWarning,
                    )

                if l_count == self.metadata_length - 1:
                    break

        # parse time series data and meta data
        self._time_series_metadata = []
        self._time_series = {}

        for key in time_series:
            # get matching mapping
            mapping_match = mapping.get(key)

            if mapping_match:
                # get unit
                unit = (
                    mapping_match.unit
                    or (
                        time_series[key].iloc[0]
                        if self.time_series_header_length == 2
                        else None
                    )
                    or None
                )

                if unit:
                    unit = _strip_unit(unit, self.config.remove_from_unit)

                # assign model
                model = QuantityMapping(
                    key=key,
                    unit=unit,
                    iri=mapping_match.iri,
                    suffix=mapping_match.suffix,
                    annotation=mapping_match.annotation or None,
                    config=self.config,
                )

                # append model
                self.time_series_metadata.append(model)

                # assign time series data
                self._time_series[model.suffix] = time_series[key][
                    self.time_series_header_length - 1 :
                ].to_list()

            else:
                warnings.warn(
                    f"No match found in mapping for key `{key}`",
                    MappingMissmatchWarning,
                )

    @classmethod
    def _load_data_file(cls, self: "DataParser") -> StringIO:
        if isinstance(self.raw_data, str):
            if os.path.isfile(self.raw_data):
                with open(
                    self.raw_data, encoding=self.config.encoding
                ) as file:
                    content = StringIO(file.read())
            else:
                content = StringIO(self.raw_data)
        else:
            raise TypeError(
                f"`raw_data` must be of type `str`, not `{type(self.raw_data)}`"
            )
        return content

    @classmethod
    def _parse_time_series(
        cls, self: "CSVParser", datafile: "StringIO"
    ) -> pd.DataFrame:
        return pd.read_csv(
            datafile,
            encoding=self.config.encoding,
            sep=self.column_sep,
            skiprows=self.metadata_length,
        )
