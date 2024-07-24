"""Data2rdf excel parser"""

import warnings
from io import BytesIO
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import pandas as pd
from openpyxl import load_workbook
from pydantic import Field

from data2rdf.models.graph import PropertyGraph, QuantityGraph
from data2rdf.utils import make_prefix
from data2rdf.warnings import MappingMissmatchWarning

from .base import ABoxBaseParser, BaseFileParser, TBoxBaseParser
from .utils import _make_tbox_classes, _make_tbox_json_ld, _strip_unit

from data2rdf.models.mapping import (  # isort:skip
    ABoxExcelMapping,
    TBoxBaseMapping,
)


def _load_data_file(
    self: "Union[ExcelTBoxParser, ExcelABoxParser]",
) -> BytesIO:
    """Load excel file as bytes"""
    if isinstance(self.raw_data, str):
        with open(self.raw_data, mode="rb") as file:
            content = BytesIO(file.read())
    elif isinstance(self.raw_data, bytes):
        content = BytesIO(self.raw_data)
    else:
        raise TypeError(
            f"`raw_data` must be of type `str` or `btyes`, not `{type(self.raw_data)}`"
        )
    return content


class ExcelTBoxParser(TBoxBaseParser):
    """
    Parses a data file of type excel in b box mode
    """

    sheet: str = Field(..., description="Name of the sheet for the mapping.")

    header_length: int = Field(
        1, description="Length of the header of the excel sheet", ge=1
    )

    # OVERRIDE
    mapping: Union[str, List[TBoxBaseMapping]] = Field(
        ...,
        description="""File path to the mapping file to be parsed or
        a list with the mapping.""",
    )

    fillna: Optional[Any] = Field(
        "", description="Value to fill NaN values in the parsed dataframe."
    )

    # OVERRIDE
    @property
    def mapping_model(cls) -> TBoxBaseMapping:
        "TBox Mapping Model"
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
        self: "ExcelTBoxParser",
        datafile: BytesIO,
        mapping: "List[TBoxBaseMapping]",
    ) -> None:
        """Run excel parser in tbox mode"""
        df = pd.read_excel(datafile, sheet_name=self.sheet)
        _make_tbox_classes(self, df, mapping)

    # OVERRIDE
    @classmethod
    def _load_data_file(cls, self: "ExcelTBoxParser") -> BytesIO:
        """Load excel file"""
        return _load_data_file(self)


class ExcelABoxParser(ABoxBaseParser):
    """
    Parses a data file of type excel in a box mode
    """

    unit_from_macro: bool = Field(
        False,
        description="When enabled, units coming from excel macros will be taken into account.",
    )

    unit_macro_location: int = Field(
        -1,
        description="Index where the marco for the unit in an excel cell might be located.",
    )

    # OVERRIDE
    mapping: Union[str, List[ABoxExcelMapping]] = Field(
        ...,
        description="""File path to the mapping file to be parsed or
        a list with the mapping.""",
    )

    # OVERRIDE
    @property
    def mapping_model(cls) -> ABoxExcelMapping:
        "Mapping Model"
        return ABoxExcelMapping

    # OVERRIDE
    @property
    def json_ld(cls) -> Dict[str, Any]:
        """Make the json-ld if pipeline is in abox-mode"""

        if not cls.config.suppress_file_description:
            tables = []

            if cls.general_metadata:
                meta_table = {
                    "@type": "csvw:Table",
                    "rdfs:label": "Metadata",
                    "csvw:row": [],
                }

                for mapping in cls.general_metadata:
                    if isinstance(mapping, QuantityGraph):
                        row = {
                            "@type": "csvw:Row",
                            "csvw:titles": {
                                "@type": "xsd:string",
                                "@value": mapping.key,
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
        self: "ExcelABoxParser",
        datafile: BytesIO,
        mapping: "List[ABoxExcelMapping]",
    ) -> None:
        """
        Parse metadata, time series metadata and time series
        """

        mapping = {model.key: model for model in mapping}

        workbook = load_workbook(filename=datafile, data_only=True)
        datafile.seek(0)
        macros = load_workbook(filename=datafile)
        datafile.seek(0)

        self._general_metadata = []
        self._time_series_metadata = []
        self._time_series = {}
        for key, datum in mapping.items():
            worksheet = workbook[datum.worksheet]

            if datum.value_location and datum.time_series_start:
                raise RuntimeError(
                    """Both, `value_location` and `time_series_start
                       are set. Only one of them must be set."""
                )

            # find data for time series
            if datum.time_series_start:
                column_name = datum.time_series_start.rstrip("0123456789")
                time_series_end = f"{column_name}{worksheet.max_row}"

                column = worksheet[datum.time_series_start : time_series_end]
                if column:
                    self._time_series[datum.suffix] = [
                        cell[0].value for cell in column
                    ]
                else:
                    message = f"""Concept with key `{key}`
                                  does not have a time series from `{datum.time_series_start}`
                                  until `{time_series_end}` .
                                  Concept will be omitted in graph.
                                  """
                    warnings.warn(message, MappingMissmatchWarning)

            # check if there is a macro for the unit of the entity
            if self.unit_from_macro and datum.value_location:
                macro_worksheet = macros[datum.worksheet]
                macro_value_cell = macro_worksheet[
                    datum.value_location
                ].number_format.split()
                if len(macro_value_cell) != 1:
                    macro_unit = macro_value_cell[self.unit_macro_location]
                else:
                    macro_unit = None
            else:
                macro_unit = None

            # check if there is a unit somewhere in the sheet
            if datum.unit_location:
                unit_location = worksheet[datum.unit_location].value
                if not unit_location:
                    message = f"""Concept with key `{key}`
                                  does not have a unit at location `{datum.unit_location}`.
                                  This mapping for the unit will be omitted in graph.
                                  """
                    warnings.warn(message, MappingMissmatchWarning)
            else:
                unit_location = None

            # decide which unit to take
            unit = datum.unit or unit_location or macro_unit
            if unit:
                unit = _strip_unit(unit, self.config.remove_from_unit)

            # make model
            model_data = {
                "key": datum.key,
                "unit": unit,
                "iri": datum.iri,
                "suffix": datum.suffix,
                "annotation": datum.annotation,
                "config": self.config,
            }

            if datum.value_location and not datum.time_series_start:
                value = worksheet[datum.value_location].value
                if model_data.get("unit") and value:
                    model_data["value"] = value
                elif not model_data.get("unit") and value:
                    model_data["value"] = str(value)
                else:
                    message = f"""Concept with key `{key}`
                                  does not have a value at location `{datum.value_location}`.
                                  Concept will be omitted in graph.
                                  """
                    warnings.warn(message, MappingMissmatchWarning)

            if model_data.get("value") or datum.suffix in self.time_series:
                if datum.value_relation:
                    model_data["value_relation"] = datum.value_relation
                if model_data.get("unit"):
                    if datum.unit_relation:
                        model_data["unit_relation"] = datum.unit_relation
                    model = QuantityGraph(**model_data)
                else:
                    model = PropertyGraph(**model_data)

                if model_data.get("value"):
                    self._general_metadata.append(model)
                else:
                    self._time_series_metadata.append(model)

        # set time series as pd dataframe
        self._time_series = pd.DataFrame.from_dict(
            self._time_series, orient="index"
        ).transpose()
        # check if drop na:
        if self.dropna:
            self._time_series.dropna(how="all", inplace=True)

    # OVERRIDE
    @classmethod
    def _load_data_file(cls, self: "ExcelABoxParser") -> BytesIO:
        """Load excel file"""
        return _load_data_file(self)


class ExcelParser(BaseFileParser):
    """Parser for excel files"""

    # OVERRIDE
    @property
    def _abox_parser(cls) -> ExcelABoxParser:
        """Pydantic Model for Excel ABox parser"""
        return ExcelABoxParser

    # OVERRIDE
    @property
    def _tbox_parser(cls) -> ExcelTBoxParser:
        """Pydantic Model for Excel TBox parser"""
        return ExcelTBoxParser

    # OVERRIDE
    @property
    def media_type(cls) -> str:
        """IANA Media type definition of the resource to be parsed."""
        return "https://www.iana.org/assignments/media-types/application/vnd.ms-excel"
