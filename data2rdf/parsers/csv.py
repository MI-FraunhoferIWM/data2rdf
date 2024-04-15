"""CSV Parser for data2rdf"""

from io import StringIO
from typing import TYPE_CHECKING, Any

import pandas as pd
from pydantic import Field, model_validator

from data2rdf.models.mapping import (
    ClassConceptMapping,
    PropertyMapping,
    QuantityMapping,
)
from data2rdf.utils import make_prefix

from .base import DataParser
from .utils import _load_mapping_file, _strip_unit

if TYPE_CHECKING:
    from typing import Dict


class CSVParser(DataParser):
    """
    Parses the csv file
    """

    header_sep: str = Field(..., description="Header separator")
    column_sep: str = Field(..., description="Column separator")
    header_length: int = Field(..., description="Length of header")

    @property
    def media_type(cls) -> str:
        """IANA Media type definition of the resource to be parsed."""
        return "http://www.iana.org/assignments/media-types/text/csv"

    @property
    def json_ld(cls) -> "Dict[str, Any]":
        """Return dict for json-ld for the graph"""
        meta_table = {
            "@type": "csvw:Table",
            "rdfs:label": "Metadata",
            "csvw:row": [],
        }

        column_schema = {"@type": "csvw:Schema", "csvw:column": []}

        triples = {
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
            "csvw:table": [
                meta_table,
                {
                    "@type": "csvw:Table",
                    "rdfs:label": "Time series data",
                    "csvw:tableSchema": column_schema,
                },
            ],
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

        for idx, mapping in enumerate(cls.time_series_metadata):
            if not isinstance(mapping, QuantityMapping):
                raise TypeError(
                    f"Mapping must be of type {QuantityMapping}, not {type(mapping)}"
                )

            if cls.config.data_download_uri:
                download_url = {
                    "dcterms:identifier": {
                        "@type": "xsd:anyURI",
                        "@value": f"{cls.config.data_download_uri}/column-{idx}",
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

        return triples

    @model_validator(mode="after")
    @classmethod
    def run_parser(cls, self: "CSVParser") -> "CSVParser":
        """
        Parse metadata, time series metadata and time series
        """

        datafile: str = cls._load_data_file(self)
        mapping: "Dict[str, ClassConceptMapping]" = _load_mapping_file(
            self.mapping, self.config, ClassConceptMapping
        )

        time_series: pd.DataFrame = cls._parse_time_series(self).dropna()

        # iterate over general metadata
        header = ["key", "value", "unit"]
        self._general_metadata = []
        for l_count, line in enumerate(datafile):
            # remove unneeded characters
            line = line.strip("\n")
            line = line.replace('"', "")

            # merge with header keys
            row = line.split(self.header_sep)
            metadatum = dict(zip(header, row))

            # get the match from the mapping
            key = metadatum.get("key")
            mapping_match = mapping.get(key)

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
                "annotation": mapping_match.annotation or None,
            }
            if model_data.get("unit"):
                model = QuantityMapping(**model_data)
            else:
                model = PropertyMapping(**model_data)
            self._general_metadata.append(model)

            if l_count == self.header_length - 1:
                break

        # parse time series data and meta data
        self._time_series_metadata = []
        self._time_series = {}
        for key in time_series:
            # get matching mapping
            mapping_match = mapping.get(key)

            # get unit
            unit = mapping_match.unit or time_series[key].iloc[0] or None
            if unit:
                unit = _strip_unit(unit, self.config.remove_from_unit)

            # assign model
            model_data = {
                "key": key,
                "unit": unit,
                "iri": mapping_match.iri,
                "annotation": mapping_match.annotation or None,
            }
            self.time_series_metadata.append(QuantityMapping(**model_data))

            # assign time series data
            self._time_series[key] = time_series[key][1:].to_list()

    @classmethod
    def _load_data_file(cls, self: "CSVParser") -> StringIO:
        with open(self.raw_data, encoding=self.config.encoding) as file:
            return StringIO(file.read())

    @classmethod
    def _parse_time_series(cls, self: "CSVParser") -> pd.DataFrame:
        return pd.read_csv(
            self.raw_data,
            encoding=self.config.encoding,
            sep=self.column_sep,
            skiprows=self.header_length,
        )
