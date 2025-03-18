"""Data2rdf excel parser"""

import json
import os
import warnings
from typing import Any, Dict, List, Optional, Union
from urllib.parse import quote, urljoin

import pandas as pd
from jsonpath_ng import parse
from pydantic import Field

from data2rdf.models.graph import PropertyGraph, QuantityGraph
from data2rdf.models.mapping import (
    CustomRelationPropertySubgraph,
    CustomRelationQuantitySubgraph,
)
from data2rdf.utils import make_prefix
from data2rdf.warnings import MappingMissmatchWarning

from .utils import _value_exists

from data2rdf.parsers.base import (  # isort:skip
    ABoxBaseParser,
    BaseFileParser,
    TBoxBaseParser,
)
from data2rdf.parsers.utils import (  # isort:skip
    _make_tbox_classes,
    _make_tbox_json_ld,
    _strip_unit,
    _check_jsonpath,
)

from data2rdf.models.mapping import (  # isort:skip
    ABoxBaseMapping,
    CustomRelation,
    TBoxBaseMapping,
)


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
    def json_ld(self) -> "Dict[str, Any]":
        """Return JSON-LD in TBox mode"""
        return _make_tbox_json_ld(self)

    # OVERRIDE
    @property
    def mapping_model(self) -> TBoxBaseMapping:
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
        """
        Runs the parser in TBox mode.

        Args:
            self: An instance of JsonTBoxParser.
            datafile: A list of dictionaries containing the data to be parsed.
            mapping: A dictionary containing the mapping of the data.

        Returns:
            None
        """

        df = pd.DataFrame(datafile)
        _make_tbox_classes(self, df, mapping)

    # OVERRIDE
    @classmethod
    def _load_data_file(cls, self: "JsonTBoxParser") -> "List[Dict[str, Any]]":
        return _load_data_file(self)


class JsonABoxParser(ABoxBaseParser):
    """Parser for JSON in ABox mode"""

    # OVERRIDE
    mapping: Union[str, List[ABoxBaseMapping]] = Field(
        ...,
        description="""File path to the mapping file to be parsed or
        a list with the mapping.""",
    )

    expand_array: bool = Field(
        False,
        description="""When enabled, the jsonpath pointing to arrays in the data
        will be iterated so that the mapping will be applied to each element of the array.""",
    )

    # OVERRIDE
    @property
    def mapping_model(self) -> ABoxBaseMapping:
        "ABox mapping model"
        return ABoxBaseMapping

    # OVERRIDE
    @property
    def json_ld(self) -> Dict[str, Any]:
        """
        Returns the JSON-LD representation of the parser's data.

        This method generates the JSON-LD representation of the parser's data,
        including the context, id, type, and members. The members are generated
        based on the general metadata and dataframe metadata.

        The method returns a dictionary containing the JSON-LD representation.

        :return: A dictionary containing the JSON-LD representation.
        :rtype: Dict[str, Any]
        """
        if not self.config.suppress_file_description:
            members = []

            triples = {
                "@context": {
                    f"{self.config.prefix_name}": make_prefix(self.config),
                    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                    "xsd": "http://www.w3.org/2001/XMLSchema#",
                    "dcterms": "http://purl.org/dc/terms/",
                    "qudt": "http://qudt.org/schema/qudt/",
                    "foaf": "http://xmlns.com/foaf/spec/",
                    "prov": "<http://www.w3.org/ns/prov#>",
                },
                "@id": f"{self.config.prefix_name}:Dictionary",
                "@type": "prov:Dictionary",
                "prov:hadDictionaryMember": members,
            }

            for mapping in self.general_metadata:
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

            for idx, mapping in enumerate(self.dataframe_metadata):
                if not isinstance(mapping, QuantityGraph):
                    raise TypeError(
                        f"Mapping must be of type {QuantityGraph}, not {type(mapping)}"
                    )

                if self.config.data_download_uri:
                    download_url = {
                        "dcterms:identifier": {
                            "@type": "xsd:anyURI",
                            "@value": urljoin(
                                str(self.config.data_download_uri),
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
                "@graph": [model.json_ld for model in self.general_metadata]
                + [model.json_ld for model in self.dataframe_metadata]
            }

        return triples

    # OVERRIDE
    @classmethod
    def _load_data_file(cls, self: "JsonABoxParser") -> "Dict[str, Any]":
        """
        Class method for loading data file.

        Args:
            cls: The class of the parser.
            self: An instance of JsonABoxParser.

        Returns:
            Dict[str, Any]: The loaded data file.
        """
        return _load_data_file(self)

    # OVERRIDE
    @classmethod
    def _run_parser(
        cls,
        self: "JsonABoxParser",
        datafile: "Dict[str, Any]",
        mapping: "List[ABoxBaseMapping]",
    ) -> None:
        """
        Class method for parsing metadata, dataframe metadata,
        and dataframe from a given data file and mapping.

        Args:
            self: An instance of JsonABoxParser.
            datafile: A dictionary containing the data to be parsed.
            mapping: A list of ABoxJsonMapping objects defining the
                     mapping from the data to the ABox.

        Returns:
            None
        """
        self._general_metadata = []
        self._dataframe_metadata = []
        self._dataframe = {}
        for datum in mapping:
            subdataset = self._get_optional_subdataset(datafile, datum)

            if not datum.custom_relations:
                suffix = self._make_suffix_from_location(datum, subdataset)
                path = _check_jsonpath(datum.value_location)
                value_expression = parse(path)

                results = [
                    match.value for match in value_expression.find(subdataset)
                ]

                if len(results) == 0:
                    value = None
                    message = f"""Concept with key `{datum.key or path}`
                                    does not have a value at location `{path}`.
                                    Concept will be omitted in graph.
                                    """
                    warnings.warn(message, MappingMissmatchWarning)
                elif len(results) == 1:
                    value = results.pop()
                else:
                    value = results

                if isinstance(value, list) or _value_exists(value):
                    if datum.unit_location:
                        path_unit_location = _check_jsonpath(
                            datum.unit_location
                        )
                        unit_expression = parse(path_unit_location)

                        results = [
                            match.value
                            for match in unit_expression.find(subdataset)
                        ]

                        if len(results) == 0:
                            unit = None
                            message = f"""Concept with key `{datum.key or path_unit_location}`
                                            does not have a unit at location `{path_unit_location}`.
                                            Concept will be omitted in graph."""
                            warnings.warn(message, MappingMissmatchWarning)
                        elif len(results) == 1:
                            unit = results.pop()
                        else:
                            unit = None
                            message = f"""Concept with key `{datum.key or path_unit_location}`
                                        has multiple units at location `{path_unit_location}`.
                                        Concept will be omitted in graph."""
                            warnings.warn(message, MappingMissmatchWarning)

                    else:
                        unit = None

                    # decide which unit to take
                    unit = datum.unit or unit
                    if unit:
                        if not isinstance(unit, str):
                            raise TypeError(
                                f"""Unit `{unit}` for key `{datum.key}` is not a string.
                                Is it a bad mapping?"""
                            )
                        unit = _strip_unit(unit, self.config.remove_from_unit)

                    # make model
                    model_data = {
                        "key": datum.key or datum.value_location,
                        "iri": datum.iri,
                        "suffix": suffix,
                        "annotation": datum.annotation,
                        "config": self.config,
                    }
                    if datum.value_relation:
                        model_data["value_relation"] = datum.value_relation

                    # if we have a series and a unit and we are *not* expanding:
                    # * make a QuantityGraph with the unit
                    # * add the graph to the dataframe metadata
                    # * add the values of the series to the dataframe array
                    if (
                        isinstance(value, list)
                        and unit
                        and not self.expand_array
                    ):
                        model_data["unit"] = unit
                        if datum.unit_relation:
                            model_data["unit_relation"] = datum.unit_relation
                        model = QuantityGraph(**model_data)

                        self._dataframe[suffix] = value
                        self._dataframe_metadata.append(model)
                    # if we have a series in the form of a list and a unit and we are expanding:
                    # * iterate over the series
                    # * make a QuantityGraph with the unit and each iterated value
                    # * add the graph to the general metadata
                    elif (
                        isinstance(value, list) and unit and self.expand_array
                    ):
                        model_data["unit"] = unit
                        if datum.unit_relation:
                            model_data["unit_relation"] = datum.unit_relation
                        for val in value:
                            model = QuantityGraph(**model_data, value=val)
                            self._general_metadata.append(model)
                    # if we have a series and *no* unit and we are *not* expanding:
                    # * make a PropertyGraph
                    # * add the graph to the dataframe metadata
                    # * add the values of the series to the dataframe array
                    elif (
                        isinstance(value, list)
                        and not unit
                        and not self.expand_array
                    ):
                        model = PropertyGraph(
                            value_relation_type=datum.value_relation_type,
                            **model_data,
                        )
                        self._dataframe[suffix] = value
                        self._dataframe_metadata.append(model)
                    # if we have a series in the form of a list and *no* unit and we are expanding:
                    # * iterate over the series
                    # * make a PropertyGraph with each iterated value
                    # * add the graph to the general metadata
                    elif (
                        isinstance(value, list)
                        and not unit
                        and self.expand_array
                    ):
                        for val in value:
                            model = PropertyGraph(
                                value=val,
                                value_relation_type=datum.value_relation_type,
                                value_datatype=datum.value_datatype,
                                **model_data,
                            )
                            self._general_metadata.append(model)
                    # if we do *not* have a series but have a unit:
                    # * make a QuantityGraph with the unit and the value
                    # * add the graph to the general metadata
                    elif _value_exists(value) and unit:
                        model_data["value"] = value
                        model_data["unit"] = unit
                        if datum.unit_relation:
                            model_data["unit_relation"] = datum.unit_relation
                        model = QuantityGraph(**model_data)

                        self._general_metadata.append(model)
                    # if we do *not* have a series and *no* unit:
                    # * make a PropertyGraph with the value
                    # * add the graph to the general metadata
                    elif _value_exists(value) and not unit:
                        model = PropertyGraph(
                            value_relation_type=datum.value_relation_type,
                            value_datatype=datum.value_datatype,
                            value=value,
                            **model_data,
                        )
                        self._general_metadata.append(model)
                    else:
                        raise RuntimeError(
                            f"""Combination of data types not supported!
                            value: {value} ({type(value)})
                            unit: {unit}
                            expand array: {self.expand_array}"""
                        )

            else:
                for relation in datum.custom_relations:
                    if datum.source:
                        for sub in subdataset:
                            suffix = self._make_suffix_from_location(
                                datum, sub
                            )
                            self._make_custom_relation(
                                relation, sub, datum, suffix
                            )
                    else:
                        suffix = self._make_suffix_from_location(
                            datum, subdataset
                        )
                        self._make_custom_relation(
                            relation, subdataset, datum, suffix
                        )

        # set dataframe as pd dataframe
        self._dataframe = pd.DataFrame.from_dict(
            self._dataframe, orient="index"
        ).transpose()
        # check if drop na:
        if self.dropna:
            self._dataframe.dropna(how="all", inplace=True)

    def _get_optional_subdataset(
        self, datafile: Any, datum: ABoxBaseMapping
    ) -> Any:
        subdataset = None
        if datum.custom_relations and datum.source:
            path_source = _check_jsonpath(datum.source)
            value_expression = parse(path_source)
            results = [
                match.value for match in value_expression.find(datafile)
            ]
            if len(results) == 0:
                message = f"""Could not properly resolve location `{path_source}` for curstom relations."""
                warnings.warn(message, MappingMissmatchWarning)
            else:
                subdataset = results
        else:
            subdataset = datafile
        return subdataset or datafile

    def _make_custom_relation(
        self,
        relation: CustomRelation,
        subdataset: Any,
        datum: ABoxBaseMapping,
        suffix: str,
    ) -> None:
        path_object_location = _check_jsonpath(relation.object_location)
        value_expression = parse(path_object_location)

        results = [match.value for match in value_expression.find(subdataset)]

        if len(results) == 0:
            value = None
            message = f"""Concept with for iri `{datum.iri}`
                            does not have a value at location `{path_object_location}`.
                            Concept will be omitted in graph.
                            """
            warnings.warn(message, MappingMissmatchWarning)
        elif len(results) == 1:
            value = results.pop()
        else:
            value = results

        if isinstance(
            relation.object_data_type,
            (CustomRelationPropertySubgraph, CustomRelationQuantitySubgraph),
        ):
            if isinstance(value, list):
                for val in value:
                    self._make_subgraph(relation, datum, val, suffix)
            elif _value_exists(value):
                self._make_subgraph(relation, datum, value, suffix)
            else:
                message = f"""Concept with for iri `{datum.iri}`
                                does not have a value at location `{relation.object_location}`.
                                Concept will be omitted in graph.
                                """
                warnings.warn(message, MappingMissmatchWarning)

        else:
            if isinstance(value, list):
                for val in value:
                    self._make_property_graph(
                        val,
                        datum.iri,
                        suffix,
                        **relation.model_dump(exclude={"object_location"}),
                    )
            elif _value_exists(value):
                self._make_property_graph(
                    value,
                    datum.iri,
                    suffix,
                    **relation.model_dump(exclude={"object_location"}),
                )
            else:
                message = f"""Concept with for iri `{datum.iri}`
                                does not have a value at location `{relation.object_location}`.
                                Concept will be omitted in graph.
                                """
                warnings.warn(message, MappingMissmatchWarning)

    def _make_subgraph(
        self,
        relation: CustomRelation,
        datum: ABoxBaseMapping,
        value: Any,
        suffix: str,
    ) -> None:
        if relation.object_data_type.concatenate:
            iri = str(relation.object_data_type.iri)
            iri = iri if iri.endswith("/") else iri + "/"
            value = urljoin(iri, str(value))
            self._make_property_graph(
                value,
                datum.iri,
                suffix,
                relation=relation.relation,
                relation_type="object_property",
            )
        else:
            if isinstance(
                relation.object_data_type, CustomRelationPropertySubgraph
            ):
                Model = PropertyGraph
            else:
                Model = QuantityGraph
            model = Model(
                value=value, **relation.object_data_type.model_dump()
            )
            model.suffix += "_" + suffix
            self._make_property_graph(
                model,
                datum.iri,
                suffix,
                relation=relation.relation,
                relation_type="object_property",
            )

    def _make_property_graph(
        self,
        value: Any,
        iri: str,
        suffix: str,
        relation: Optional[str] = None,
        relation_type: Optional[str] = None,
        object_data_type: Optional[str] = None,
    ) -> None:
        model = PropertyGraph(
            value_relation=relation,
            value_relation_type=relation_type,
            value_datatype=object_data_type,
            value=value,
            iri=iri,
            suffix=suffix,
            config=self.config,
        )
        self._general_metadata.append(model)

    def _make_suffix_from_location(
        self, datum: ABoxBaseMapping, subdataset: Any
    ) -> str:
        if datum.suffix_from_location:
            path_suffix = _check_jsonpath(datum.suffix)
            value_expression = parse(path_suffix)
            results = [
                match.value for match in value_expression.find(subdataset)
            ]

            if len(results) == 0 or len(results) > 1:
                suffix = path_suffix
                message = f"""Could not properly resolve suffix location `{path_suffix}`
                                Will use the location itself as suffix.
                            """
                warnings.warn(message, MappingMissmatchWarning)
            else:
                suffix = results.pop()
        else:
            suffix = datum.suffix

        suffix = quote(suffix)

        return suffix


class JsonParser(BaseFileParser):
    """
    Parses a data file of type json
    """

    # OVERRIDE
    @property
    def media_type(self) -> str:
        """IANA Media type definition of the resource to be parsed."""
        return "https://www.iana.org/assignments/media-types/application/json"

    # OVERRIDE
    @property
    def _abox_parser(self) -> JsonABoxParser:
        """Pydantic Model for Joson ABox parser"""
        return JsonABoxParser

    # OVERRIDE
    @property
    def _tbox_parser(self) -> JsonTBoxParser:
        """Pydantic Model for Excel TBox parser"""
        return JsonTBoxParser
