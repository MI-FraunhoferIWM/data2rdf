"""Data2rdf excel parser"""

from typing import Any, Dict, Union

from openpyxl import load_workbook
from pydantic import Field, model_validator

from data2rdf.models.mapping import (
    ExcelConceptMapping,
    PropertyMapping,
    QuantityMapping,
)
from data2rdf.utils import make_prefix

from .base import DataParser
from .utils import _load_mapping_file, _strip_unit


class ExcelParser(DataParser):
    """
    Parses a data file of type CSV
    """

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
    def run_parser(cls, self: "ExcelParser") -> "ExcelParser":
        """
        Parse metadata, time series metadata and time series
        """

        datafile = load_workbook(filename=self.raw_data, data_only=True)
        macros = load_workbook(filename=self.raw_data)
        mapping: "Dict[str, ExcelConceptMapping]" = _load_mapping_file(
            self.mapping, self.config, ExcelConceptMapping
        )

        self._general_metadata = []
        self._time_series_metadata = []
        self._time_series = {}
        for key, datum in mapping.items():
            worksheet = datafile[datum.worksheet]

            # check if mapping is time series
            if datum.time_series_start and datum.time_series_end:
                self.time_series[key] = [
                    cell[0].value
                    for cell in worksheet[
                        datum.time_series_start : datum.time_series_end
                    ]
                ]

            # check if there is a macro for the unit of the entity
            if datum.value_location:
                macro_worksheet = macros[datum.worksheet]
                macro_value_cell = macro_worksheet[
                    datum.value_location
                ].number_format.split()
                if len(macro_value_cell) != 1:
                    macro_unit = macro_value_cell[
                        self.config.unit_macro_location
                    ]
                else:
                    macro_unit = None
            else:
                macro_unit = None

            # check if there is a unit somewhere in the sheet
            if datum.unit_location:
                unit_location = worksheet[datum.unit_location].value
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
                "annotation": datum.annotation or None,
            }

            if datum.value_location:
                value = worksheet[datum.value_location].value
                if model_data.get("unit"):
                    model_data["value"] = value
                else:
                    model_data["value"] = str(value)

            if model_data.get("unit"):
                model = QuantityMapping(**model_data)
            else:
                model = PropertyMapping(**model_data)

            if model_data.get("value"):
                self._general_metadata.append(model)
            else:
                self._time_series_metadata.append(model)

        return self
