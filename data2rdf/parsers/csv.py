"""CSV Parser for data2rdf"""

import os
import warnings
from io import StringIO
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import pandas as pd
from pydantic import Field

from data2rdf.models.graph import PropertyGraph, QuantityGraph
from data2rdf.utils import make_prefix
from data2rdf.warnings import MappingMissmatchWarning, ParserWarning

from .base import ABoxBaseParser, BaseFileParser, TBoxBaseParser
from .utils import _make_tbox_classes, _make_tbox_json_ld, _strip_unit

from data2rdf.models.mapping import (  # isort:skip
    ABoxBaseMapping,
    TBoxBaseMapping,
)


def _load_data_file(self: "Union[CSVTBoxParser, CSVABoxParser]") -> StringIO:
    """Load csv file"""
    if isinstance(self.raw_data, str):
        if os.path.isfile(self.raw_data):
            with open(self.raw_data, encoding=self.config.encoding) as file:
                content = StringIO(file.read())
        else:
            content = StringIO(self.raw_data)
    else:
        raise TypeError(
            f"`raw_data` must be of type `str`, not `{type(self.raw_data)}`"
        )
    return content


class CSVTBoxParser(TBoxBaseParser):
    """
    CSV file parser in tbox mode
    """

    # OVERRIDE
    mapping: Union[str, List[TBoxBaseMapping]] = Field(
        ...,
        description="""File path to the mapping file to be parsed or
        a list with the mapping.""",
    )
    column_sep: Optional[str] = Field(",", description="Data column separator")
    header_length: int = Field(
        1, description="Length of the header of the excel sheet", ge=1
    )

    fillna: Optional[Any] = Field(
        "", description="Value to fill NaN values in the parsed dataframe."
    )

    # OVERRIDE
    @property
    def mapping_model(cls) -> TBoxBaseMapping:
        """TBox Mapping Model for CSV Parser"""
        return TBoxBaseMapping

    # OVERRIDE
    @property
    def json_ld(cls) -> "Dict[str, Any]":
        """Make the json-ld if pipeline is in abox-mode"""
        return _make_tbox_json_ld(cls)

    # OVERRIDE
    @classmethod
    def _run_parser(
        cls,
        self: "CSVTBoxParser",
        datafile: StringIO,
        mapping: "List[TBoxBaseMapping]",
    ) -> None:
        """Run excel parser in tbox mode"""
        df = pd.read_csv(datafile, sep=self.column_sep)
        _make_tbox_classes(self, df, mapping)

    # OVERRIDE
    @classmethod
    def _load_data_file(cls, self: "CSVTBoxParser") -> StringIO:
        """Load CSV file"""
        return _load_data_file(self)


class CSVABoxParser(ABoxBaseParser):
    """
    CSV file parser in abox mode
    """

    metadata_sep: Optional[str] = Field(
        None, description="Metadata column separator"
    )
    metadata_length: int = Field(..., description="Length of the metadata")
    time_series_sep: Optional[str] = Field(
        None, description="Column separator of the time series header"
    )
    time_series_header_length: int = Field(
        2, description="Length of header of the time series"
    )
    # OVERRIDE
    mapping: Union[str, List[ABoxBaseMapping]] = Field(
        ...,
        description="""File path to the mapping file to be parsed or
        a list with the mapping.""",
    )

    # OVERRIDE
    @property
    def mapping_model(cls) -> ABoxBaseMapping:
        """ABox Mapping Model for CSV Parser"""
        return ABoxBaseMapping

    # OVERRIDE
    @property
    def json_ld(cls) -> "Dict[str, Any]":
        """Return dict for json-ld for the graph in abox mode"""

        if not cls.config.suppress_file_description:
            tables = []

            if cls.general_metadata:
                meta_table = {
                    "@type": "csvw:Table",
                    "rdfs:label": "Metadata",
                    "csvw:row": [],
                }

                for n, mapping in enumerate(cls.general_metadata):
                    if isinstance(mapping, QuantityGraph):
                        row = {
                            "@type": "csvw:Row",
                            "csvw:titles": {
                                "@type": "xsd:string",
                                "@value": mapping.key,
                            },
                            "csvw:rownum": {
                                "@type": "xsd:integer",
                                "@value": n,
                            },
                            "qudt:quantity": mapping.json_ld,
                        }
                        meta_table["csvw:row"].append(row)
                    elif isinstance(mapping, PropertyGraph):
                        row = {
                            "@type": "csvw:Row",
                            "csvw:titles": {
                                "@type": "xsd:string",
                                "@value": mapping.key,
                            },
                            "csvw:rownum": {
                                "@type": "xsd:integer",
                                "@value": n,
                            },
                            "csvw:describes": mapping.json_ld,
                        }
                        meta_table["csvw:row"].append(row)
                    else:
                        raise TypeError(
                            f"Mapping must be of type {QuantityGraph} or {PropertyGraph}, not {type(mapping)}"
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
                    if isinstance(mapping, QuantityGraph):
                        entity = {"qudt:quantity": mapping.json_ld}
                    elif isinstance(mapping, PropertyGraph):
                        entity = {"dcterms:subject": mapping.json_ld}
                    else:
                        raise TypeError(
                            f"Mapping must be of type {QuantityGraph} or {PropertyGraph}, not {type(mapping)}"
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
                        **entity,
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

            json_ld = {
                "@context": {
                    f"{cls.config.prefix_name}": make_prefix(cls.config),
                    "csvw": "http://www.w3.org/ns/csvw#",
                    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                    "dcat": "http://www.w3.org/ns/dcat#",
                    "xsd": "http://www.w3.org/2001/XMLSchema#",
                    "dcterms": "http://purl.org/dc/terms/",
                    "qudt": "http://qudt.org/schema/qudt/",
                    "csvw": "http://www.w3.org/ns/csvw#",
                    "foaf": "http://xmlns.com/foaf/spec/",
                },
                "@id": f"{cls.config.prefix_name}:tableGroup",
                "@type": "csvw:TableGroup",
                **csvw_tables,
            }
        else:
            json_ld = {
                "@graph": [model.json_ld for model in cls.general_metadata]
                + [model.json_ld for model in cls.time_series_metadata]
            }
        return json_ld

    # OVERRIDE
    @classmethod
    def _run_parser(
        cls,
        self: "CSVParser",
        datafile: StringIO,
        mapping: "List[ABoxBaseMapping]",
    ) -> None:
        """
        Parse metadata, time series metadata and time series
        """

        mapping = {model.key: model for model in mapping}

        time_series: Union[pd.DataFrame, List[None]] = cls._parse_time_series(
            self, datafile
        )
        if self.dropna:
            time_series.dropna(inplace=True)
        datafile.seek(0)

        # iterate over general metadata
        header = ["key", "value", "unit"]
        self._general_metadata = []
        if self.metadata_length > 0:
            if not self.metadata_sep:
                raise ValueError(
                    "`metadata_length` is > 0 but `metadata_sep` is not set"
                )
            for l_count, line in enumerate(datafile.readlines()):
                # remove unneeded characters
                for char in self.config.remove_from_datafile:
                    line = line.replace(char, "")

                # merge with header keys
                row = line.split(self.metadata_sep)
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
                    if mapping_match.value_relation:
                        model_data[
                            "value_relation"
                        ] = mapping_match.value_relation
                    if model_data.get("unit"):
                        if mapping_match.unit_relation:
                            model_data[
                                "unit_relation"
                            ] = mapping_match.unit_relation
                        model = QuantityGraph(**model_data)
                    else:
                        model = PropertyGraph(**model_data)
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
                model = QuantityGraph(
                    key=key,
                    unit=unit,
                    iri=mapping_match.iri,
                    suffix=mapping_match.suffix,
                    annotation=mapping_match.annotation or None,
                    config=self.config,
                )
                if mapping_match.unit_relation:
                    model.unit_relation = mapping_match.unit_relation

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
        # set time series as pd dataframe
        self._time_series = pd.DataFrame.from_dict(
            self._time_series, orient="index"
        ).transpose()
        # check if drop na:
        if self.dropna:
            self._time_series.dropna(how="all", inplace=True)

    # OVERRIDE
    @classmethod
    def _load_data_file(cls, self: "CSVABoxParser") -> StringIO:
        """Load csv file"""
        return _load_data_file(self)

    @classmethod
    def _parse_time_series(
        cls, self: "CSVParser", datafile: "StringIO"
    ) -> Union[pd.DataFrame, List[None]]:
        if self.time_series_sep:
            response = pd.read_csv(
                datafile,
                encoding=self.config.encoding,
                sep=self.time_series_sep,
                skiprows=self.metadata_length,
            )
        else:
            warnings.warn(
                "`time_series_sep` is not set. Any potential time series in the data file will be skipped.",
                ParserWarning,
            )
            response = []
        return response


class CSVParser(BaseFileParser):
    """Parser for CSV/TSV files"""

    # OVERRIDE
    @property
    def _abox_parser(self) -> CSVABoxParser:
        """Pydantic Model for CSV ABox parser"""
        return CSVABoxParser

    # OVERRIDE
    @property
    def _tbox_parser(self) -> CSVTBoxParser:
        """Pydantic Model for CSV TBox parser"""
        return CSVTBoxParser

    # OVERRIDE
    @property
    def media_type(self) -> str:
        """IANA Media type definition of the resource to be parsed."""
        return "http://www.iana.org/assignments/media-types/text/csv"
