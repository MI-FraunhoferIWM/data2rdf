"""Data2rdf excel parser"""

import json
import os
import warnings
from typing import Any, Dict, Union
from urllib.parse import urljoin

from jsonpath_ng import parse
from pydantic import Field, model_validator

from data2rdf.utils import make_prefix
from data2rdf.warnings import MappingMissmatchWarning

from .base import DataParser
from .utils import _strip_unit, load_mapping_file

from data2rdf.models.mapping import (  # isort: skip
    JsonConceptMapping,
    PropertyMapping,
    QuantityMapping,
)


class JsonParser(DataParser):
    """
    Parses a data file of type json
    """

    # OVERRIDE
    mapping: Union[str, Dict[str, JsonConceptMapping]] = Field(
        ...,
        description="""File path to the mapping file to be parsed or
        a dictionary with the mapping.""",
    )

    @property
    def media_type(cls) -> str:
        """IANA Media type definition of the resource to be parsed."""
        return "https://www.iana.org/assignments/media-types/application/json"

    @property
    def json_ld(cls) -> Dict[str, Any]:
        members = []

        triples = {
            "@context": {
                "fileid": make_prefix(cls.config),
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
                "dcterms": "http://purl.org/dc/terms/",
                "qudt": "http://qudt.org/schema/qudt/",
                "foaf": "http://xmlns.com/foaf/spec/",
                "prov": "<http://www.w3.org/ns/prov#>",
            },
            "@id": "fileid:Dictionary",
            "@type": "prov:Dictionary",
            "prov:hadDictionaryMember": members,
        }

        for mapping in cls.general_metadata:
            if isinstance(mapping, QuantityMapping):
                entity = {
                    "@type": "prov:KeyEntityPair",
                    "prov:pairKey": {
                        "@type": "xsd:string",
                        "@value": mapping.key,
                    },
                    "prov:pairEntity": {
                        "@type": "prov:Entity",
                        "qudt:quantity": mapping.json_ld,
                    },
                }
                members.append(entity)
            elif isinstance(mapping, PropertyMapping):
                entity = {
                    "@type": "prov:KeyEntityPair",
                    "prov:pairKey": {
                        "@type": "xsd:string",
                        "@value": mapping.key,
                    },
                    "prov:pairEntity": {
                        "@type": "prov:Entity",
                        "dcterms:hasPart": mapping.json_ld,
                    },
                }
                members.append(entity)
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
                        "@value": urljoin(
                            str(cls.config.data_download_uri), f"column-{idx}"
                        ),
                    }
                }
            else:
                download_url = {}

            entity = {
                "@type": "prov:KeyEntityPair",
                "prov:pairKey": {
                    "@type": "xsd:string",
                    "@value": mapping.key,
                },
                "prov:pairEntity": {
                    "@type": "prov:Entity",
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
                },
            }
            members.append(entity)

        return triples

    @model_validator(mode="after")
    @classmethod
    def run_parser(cls, self: "JsonParser") -> "JsonParser":
        """
        Parse metadata, time series metadata and time series
        """

        datafile: "Dict[str, Any]" = cls._parse_data(self)
        mapping: "Dict[str, JsonConceptMapping]" = load_mapping_file(
            self.mapping, self.config, JsonConceptMapping
        )

        self._general_metadata = []
        self._time_series_metadata = []
        self._time_series = {}
        numericals = (int, str, float, bool)
        for key, datum in mapping.items():
            value_expression = parse(datum.value_location)

            results = [
                match.value for match in value_expression.find(datafile)
            ]

            if len(results) == 0:
                value = None
                message = f"""Concept with key `{key}`
                                does not have a value at location `{datum.value_location}`.
                                Concept will be omitted in graph.
                                """
                warnings.warn(message, MappingMissmatchWarning)
            elif len(results) == 1:
                value = results.pop()
            else:
                value = results

            if value:
                # check if there is a unit somewhere in the sheet
                if datum.unit_location:
                    unit_expression = parse(datum.unit_location)

                    results = [
                        match.value for match in unit_expression.find(datafile)
                    ]

                    if len(results) == 0:
                        unit = None
                        message = f"""Concept with key `{key}`
                                        does not have a unit at location `{datum.unit_location}`.
                                        Concept will be omitted in graph."""
                        warnings.warn(message, MappingMissmatchWarning)
                    elif len(results) == 1:
                        unit = results.pop()
                    else:
                        unit = None
                        message = f"""Concept with key `{key}`
                                    has multiple units at location `{datum.unit_location}`.
                                    Concept will be omitted in graph."""
                        warnings.warn(message, MappingMissmatchWarning)

                else:
                    unit = None

                # decide which unit to take
                unit = datum.unit or unit
                if unit:
                    unit = _strip_unit(unit, self.config.remove_from_unit)

                # make model
                model_data = {
                    "key": datum.key,
                    "iri": datum.iri,
                    "suffix": datum.suffix,
                    "annotation": datum.annotation,
                    "config": self.config,
                }
                if not isinstance(value, numericals) and unit:
                    model_data["unit"] = unit
                    model = QuantityMapping(**model_data)

                    self._time_series[datum.suffix] = value
                    self._time_series_metadata.append(model)
                if not isinstance(value, numericals) and not unit:
                    message = f"""Series with with key `{key}`
                                must be a quantity does not have a unit.
                                Concept will be omitted in graph."""
                    warnings.warn(message, MappingMissmatchWarning)
                elif isinstance(value, numericals) and unit:
                    model_data["value"] = value
                    model_data["unit"] = unit
                    model = QuantityMapping(**model_data)

                    self._general_metadata.append(model)
                elif isinstance(value, numericals) and not unit:
                    model_data["value"] = str(value)
                    model = PropertyMapping(**model_data)

                    self._general_metadata.append(model)

        return self

    @classmethod
    def _parse_data(cls, self: "JsonParser") -> "Dict[str, Any]":
        if isinstance(self.raw_data, str):
            if os.path.isfile(self.raw_data):
                with open(
                    self.raw_data, encoding=self.config.encoding
                ) as file:
                    content = json.load(file)
            else:
                content = json.loads(self.raw_data)

        if isinstance(self.raw_data, dict):
            content = self.raw_data
        if not isinstance(self.raw_data, (str, dict)):
            raise TypeError(
                "Raw data must be of type `str` for a file path or a `dict` for a parsed json."
            )
        return content
