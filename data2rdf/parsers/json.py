"""Data2rdf excel parser"""

import json
import os
import warnings
from typing import Any, Dict, List, Union
from urllib.parse import urljoin

import pandas as pd
from jsonpath_ng import parse
from pydantic import Field

from data2rdf.models.graph import PropertyGraph, QuantityGraph
from data2rdf.models.mapping import ABoxJsonMapping, TBoxBaseMapping
from data2rdf.utils import make_prefix
from data2rdf.warnings import MappingMissmatchWarning

from .base import ABoxBaseParser, BaseFileParser, TBoxBaseParser
from .utils import _make_tbox_classes, _make_tbox_json_ld, _strip_unit


def _load_data_file(
    self: "Union[JsonABoxParser, JsonTBoxParser]",
) -> "List[Dict[str, Any]]":
    """Load json file"""
    if isinstance(self.raw_data, str):
        if os.path.isfile(self.raw_data):
            with open(self.raw_data, encoding=self.config.encoding) as file:
                content = json.load(file)
        else:
            content = json.loads(self.raw_data)

    if isinstance(self.raw_data, (list, dict)):
        content = self.raw_data
    if not isinstance(self.raw_data, (str, dict, list)):
        raise TypeError(
            "Raw data must be of type `str` for a file path or a `dict` for a parsed json."
        )
    return content


class JsonTBoxParser(TBoxBaseParser):
    """Parser for JSON in TBox mode"""

    # OVERRIDE
    mapping: Union[str, List[TBoxBaseMapping]] = Field(
        ...,
        description="""File path to the mapping file to be parsed or
        a list with the mapping.""",
    )

    # OVERRIDE
    @property
    def json_ld(cls) -> "Dict[str, Any]":
        """Return JSON-LD in TBox mode"""
        return _make_tbox_json_ld(cls)

    # OVERRIDE
    @property
    def mapping_model(cls) -> TBoxBaseMapping:
        "TBox mapping model"
        return TBoxBaseMapping

    # OVERRIDE
    @classmethod
    def _run_parser(
        cls,
        self: "JsonTBoxParser",
        datafile: "List[Dict[str, Any]]",
        mapping: "Dict[str, TBoxBaseMapping]",
    ) -> None:
        """Run parser in TBox mode"""
        df = pd.DataFrame(datafile)
        _make_tbox_classes(self, df, mapping)

    # OVERRIDE
    @classmethod
    def _load_data_file(cls, self: "JsonTBoxParser") -> "List[Dict[str, Any]]":
        return _load_data_file(self)


class JsonABoxParser(ABoxBaseParser):
    """Parser for JSON in ABox mode"""

    # OVERRIDE
    mapping: Union[str, List[ABoxJsonMapping]] = Field(
        ...,
        description="""File path to the mapping file to be parsed or
        a list with the mapping.""",
    )

    # OVERRIDE
    @property
    def mapping_model(cls) -> ABoxJsonMapping:
        "ABox mapping model"
        return ABoxJsonMapping

    # OVERRIDE
    @property
    def json_ld(cls) -> Dict[str, Any]:
        if not cls.config.suppress_file_description:
            members = []

            triples = {
                "@context": {
                    f"{cls.config.prefix_name}": make_prefix(cls.config),
                    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                    "xsd": "http://www.w3.org/2001/XMLSchema#",
                    "dcterms": "http://purl.org/dc/terms/",
                    "qudt": "http://qudt.org/schema/qudt/",
                    "foaf": "http://xmlns.com/foaf/spec/",
                    "prov": "<http://www.w3.org/ns/prov#>",
                },
                "@id": f"{cls.config.prefix_name}:Dictionary",
                "@type": "prov:Dictionary",
                "prov:hadDictionaryMember": members,
            }

            for mapping in cls.general_metadata:
                if isinstance(mapping, QuantityGraph):
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
                elif isinstance(mapping, PropertyGraph):
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
                        f"Mapping must be of type {QuantityGraph} or {PropertyGraph}, not {type(mapping)}"
                    )

            for idx, mapping in enumerate(cls.time_series_metadata):
                if not isinstance(mapping, QuantityGraph):
                    raise TypeError(
                        f"Mapping must be of type {QuantityGraph}, not {type(mapping)}"
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
        else:
            triples = {
                "@graph": [model.json_ld for model in cls.general_metadata]
                + [model.json_ld for model in cls.time_series_metadata]
            }

        return triples

    # OVERRIDE
    @classmethod
    def _load_data_file(cls, self: "JsonABoxParser") -> "Dict[str, Any]":
        return _load_data_file(self)

    # OVERRIDE
    @classmethod
    def _run_parser(
        cls,
        self: "JsonABoxParser",
        datafile: "Dict[str, Any]",
        mapping: "List[ABoxJsonMapping]",
    ) -> None:
        """
        Parse metadata, time series metadata and time series
        """

        self._general_metadata = []
        self._time_series_metadata = []
        self._time_series = {}
        numericals = (int, str, float, bool)
        for datum in mapping:
            value_expression = parse(datum.value_location)

            results = [
                match.value for match in value_expression.find(datafile)
            ]

            if len(results) == 0:
                value = None
                message = f"""Concept with key `{datum.key or datum.value_location}`
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
                        message = f"""Concept with key `{datum.key or datum.value_location}`
                                        does not have a unit at location `{datum.unit_location}`.
                                        Concept will be omitted in graph."""
                        warnings.warn(message, MappingMissmatchWarning)
                    elif len(results) == 1:
                        unit = results.pop()
                    else:
                        unit = None
                        message = f"""Concept with key `{datum.key or datum.value_location}`
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
                    "key": datum.key or datum.value_location,
                    "iri": datum.iri,
                    "suffix": datum.suffix,
                    "annotation": datum.annotation,
                    "config": self.config,
                }
                if datum.value_relation:
                    model_data["value_relation"] = datum.value_relation

                if not isinstance(value, numericals) and unit:
                    model_data["unit"] = unit
                    if datum.unit_relation:
                        model_data["unit_relation"] = datum.unit_relation
                    model = QuantityGraph(**model_data)

                    self._time_series[datum.suffix] = value
                    self._time_series_metadata.append(model)
                if not isinstance(value, numericals) and not unit:
                    message = f"""Series with with key `{datum.key or datum.value_locationy}`
                                must be a quantity does not have a unit.
                                Concept will be omitted in graph."""
                    warnings.warn(message, MappingMissmatchWarning)
                elif isinstance(value, numericals) and unit:
                    model_data["value"] = value
                    model_data["unit"] = unit
                    if datum.unit_relation:
                        model_data["unit_relation"] = datum.unit_relation
                    model = QuantityGraph(**model_data)

                    self._general_metadata.append(model)
                elif isinstance(value, numericals) and not unit:
                    model_data["value"] = str(value)
                    model = PropertyGraph(**model_data)

                    self._general_metadata.append(model)
        # set time series as pd dataframe
        self._time_series = pd.DataFrame.from_dict(
            self._time_series, orient="index"
        ).transpose()
        # check if drop na:
        if self.dropna:
            self._time_series.dropna(how="all", inplace=True)


class JsonParser(BaseFileParser):
    """
    Parses a data file of type json
    """

    # OVERRIDE
    @property
    def media_type(cls) -> str:
        """IANA Media type definition of the resource to be parsed."""
        return "https://www.iana.org/assignments/media-types/application/json"

    # OVERRIDE
    @property
    def _abox_parser(cls) -> JsonABoxParser:
        """Pydantic Model for Joson ABox parser"""
        return JsonABoxParser

    # OVERRIDE
    @property
    def _tbox_parser(cls) -> JsonTBoxParser:
        """Pydantic Model for Excel TBox parser"""
        return JsonTBoxParser
