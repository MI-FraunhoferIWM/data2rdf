"""Data2rdf excel parser"""

import warnings
from io import BytesIO
from typing import Any, Dict, Union
from urllib.parse import urljoin

from openpyxl import load_workbook
from pydantic import Field, model_validator

from data2rdf.models.mapping import (
    ExcelConceptMapping,
    PropertyMapping,
    QuantityMapping,
)
from data2rdf.utils import make_prefix
from data2rdf.warnings import MappingMissmatchWarning

from .base import DataParser
from .utils import _find_end_of_series, _strip_unit, load_mapping_file


class ExcelParser(DataParser):
    """
    Parses a data file of type excel
    """

    unit_from_macro: bool = Field(
        True,
        description="When disabled, units coming from excel macros are neglected.",
    )

    unit_macro_location: int = Field(
        -1,
        description="Index where the marco for the unit in an excel cell might be located.",
    )

    max_row_iteration: int = Field(
        1e12,
        description="""In Excel files, the parser is scanning for the end of the time series.
        In order to prevent a frozen process, this maximum row number is set.""",
    )

    # OVERRIDE
    mapping: Union[str, Dict[str, ExcelConceptMapping]] = Field(
        ...,
        description="""File path to the mapping file to be parsed or
        a dictionary with the mapping.""",
    )

    @property
    def media_type(cls) -> str:
        """IANA Media type definition of the resource to be parsed."""
        return "https://www.iana.org/assignments/media-types/application/vnd.ms-excel"

    @property
    def json_ld(cls) -> Dict[str, Any]:
        """Return dict for json-ld for the graph"""

        tables = []

        if cls.general_metadata:
            meta_table = {
                "@type": "csvw:Table",
                "rdfs:label": "Metadata",
                "csvw:row": [],
            }

            for mapping in cls.general_metadata:
                if isinstance(mapping, QuantityMapping):
                    row = {
                        "@type": "csvw:Row",
                        "csvw:titles": {
                            "@type": "xsd:string",
                            "@value": mapping.key,
                        },
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
    def run_parser(cls, self: "ExcelParser") -> "ExcelParser":
        """
        Parse metadata, time series metadata and time series
        """

        io: BytesIO = cls._load_data_file(self)

        datafile = load_workbook(filename=io, data_only=True)
        io.seek(0)
        macros = load_workbook(filename=io)
        mapping: "Dict[str, ExcelConceptMapping]" = load_mapping_file(
            self.mapping, self.config, ExcelConceptMapping
        )

        self._general_metadata = []
        self._time_series_metadata = []
        self._time_series = {}
        for key, datum in mapping.items():
            worksheet = datafile[datum.worksheet]

            suffix = str(datum.iri).split(self.config.separator)[-1]

            if datum.value_location and datum.time_series_start:
                raise RuntimeError(
                    """Both, `value_location` and `time_series_start
                       are set. Only one of them must be set."""
                )

            # find data for time series
            if datum.time_series_start:
                time_series_end = _find_end_of_series(
                    worksheet,
                    datum.time_series_start,
                    self.max_row_iteration,
                )

                column = worksheet[datum.time_series_start : time_series_end]
                if column:
                    self.time_series[suffix] = [
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

            if model_data.get("value") or suffix in self.time_series:
                if model_data.get("unit"):
                    model = QuantityMapping(**model_data)
                else:
                    model = PropertyMapping(**model_data)

                if model_data.get("value"):
                    self._general_metadata.append(model)
                else:
                    self._time_series_metadata.append(model)

        return self

    @classmethod
    def _load_data_file(cls, self: "DataParser") -> BytesIO:
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
