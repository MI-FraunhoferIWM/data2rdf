"""Models for graph construction from semantic concepts"""

import warnings
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyUrl, BaseModel, Field, ValidationInfo, field_validator

from data2rdf.qudt.utils import _get_query_match
from data2rdf.utils import is_bool, is_float, is_integer, is_uri, make_prefix

from .base import BasicGraphModel, BasicSuffixModel


class ValueRelationMapping(BaseModel):
    """Mapping between a object/data/annotation property and a value resolved from a location in the data file"""

    value: Union[str, int, float, bool, AnyUrl] = Field(
        ...,
        description="""Value resolved from the data file.""",
    )
    relation: Union[str, AnyUrl] = Field(
        ...,
        description="""Object/Data/Annotation property for the value
        resolving from `key` of this model""",
    )


class ClassTypeGraph(BasicGraphModel):
    """Graph of a potential concept or class in the T Box."""

    suffix: str = Field(
        ...,
        description="""Value of the suffix of the
        ontological class to be used""",
    )
    rdfs_type: AnyUrl = Field(
        "owl:Class", description="rdfs:type for this concept"
    )
    annotation_properties: Optional[List[ValueRelationMapping]] = Field(
        None, description="Mappings for Annotations Properties"
    )
    object_properties: Optional[List[ValueRelationMapping]] = Field(
        None, description="Mappings for Object Properties"
    )
    data_properties: Optional[List[ValueRelationMapping]] = Field(
        None, description="Mappings for Data Properties"
    )

    @classmethod
    def value_json(cls, value) -> "Dict[str, Any]":
        """Return json with value definition"""
        if is_float(value):
            dtype = "xsd:float"
            value = float(value)
        elif is_integer(value):
            dtype = "xsd:integer"
            value = int(value)
        elif is_bool(value):
            dtype = "xsd:bool"
            value = bool(value)
        elif is_uri(value):
            dtype = "xsd:anyURI"
            value = str(value)
        elif isinstance(value, str):
            dtype = "xsd:string"
        else:
            raise TypeError(
                f"Datatype of value `{value}` ({type(value)}) cannot be mapped to xsd."
            )

        return {"@type": dtype, "@value": value}

    # OVERRIDE
    @property
    def json_ld(self) -> "Dict[str, Any]":
        annotations = {
            model.relation: self.value_json(model.value)
            for model in self.annotation_properties
        }
        datatypes = {
            model.relation: self.value_json(model.value)
            for model in self.data_properties
        }
        objects = {
            model.relation: str(model.value)
            for model in self.object_properties
        }
        return {
            "@context": {
                "owl": "http://www.w3.org/2002/07/owl#",
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "dcterms": "http://purl.org/dc/terms/",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
                f"{self.config.prefix_name}": make_prefix(self.config),
            },
            "@id": f"{self.config.prefix_name}:{self.suffix}",
            "@type": str(self.rdfs_type),
            **annotations,
            **datatypes,
            **objects,
        }


class QuantityGraph(BasicGraphModel, BasicSuffixModel):
    """Quantity with or without a discrete value and a unit
    E.g. a quantity with a single value and unit _or_
    a quantity describing a column of a time series or table with a unit."""

    unit: Optional[Union[str, AnyUrl]] = Field(
        ..., description="QUDT Symbol or any other IRI for the unit mapping"
    )
    value: Optional[Union[int, float]] = Field(
        None, description="Value of the quantity"
    )

    unit_relation: Optional[Union[str, AnyUrl]] = Field(
        "qudt:hasUnit",
        description="""Object property for mapping the IRI
         of the unit to the individual.""",
    )

    value_relation: Optional[Union[str, AnyUrl]] = Field(
        "qudt:value",
        description="""Data property
        for mapping the data value to the individual.""",
    )

    @field_validator("unit", mode="after")
    @classmethod
    def validate_unit(
        cls, value: Union[str, AnyUrl], info: ValidationInfo
    ) -> Optional[AnyUrl]:
        config = info.data.get("config")
        if isinstance(value, str):
            if not (value.startswith("https:") or value.startswith("http:")):
                match = _get_query_match(value, config.qudt_units)
                if len(match) == 0:
                    warnings.warn(
                        f"No QUDT Mapping found for unit with symbol `{value}`."
                    )
                    value = None
                elif len(match) > 1:
                    warnings.warn(
                        f"Multiple QUDT Mappings found for unit with symbol `{value}`."
                    )
                    value = match.pop()
                else:
                    value = match.pop()
        elif isinstance(value, AnyUrl):
            value = str(value)
        return value

    @property
    def json_ld(cls) -> Dict[str, Any]:
        """Return dict of json-ld for graph"""
        return {
            "@context": {
                f"{cls.config.prefix_name}": make_prefix(cls.config),
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
                "qudt": "http://qudt.org/schema/qudt/",
            },
            "@id": f"{cls.config.prefix_name}:{cls.suffix}",
            "@type": str(cls.iri),
            **cls.unit_json,
            **cls.value_json,
        }

    @property
    def unit_json(self) -> "Dict[str, Any]":
        """Return json with unit definition"""
        if self.unit:
            value = {
                self.unit_relation: {
                    "@value": self.unit,
                    "@type": "xsd:anyURI",
                }
            }
        else:
            value = {}
        return value

    @property
    def value_json(self) -> "Dict[str, Any]":
        """Return json with value definition"""
        if self.value:
            if is_float(self.value):
                dtype = "xsd:float"
                value = float(self.value)
            elif is_integer(self.value):
                dtype = "xsd:integer"
                value = int(self.value)
            elif is_bool(self.value):
                dtype = "xsd:bool"
                value = bool(self.value)
            elif is_uri(self.value):
                dtype = "xsd:anyURI"
                value = str(self.value)
            else:
                raise ValueError(
                    f"""Datatype not recognized for key
                    `{self.key}` with value:
                    `{self.value}`"""
                )
            value = {self.value_relation: {"@type": dtype, "@value": value}}
        else:
            value = {}
        return value


class PropertyGraph(BasicGraphModel, BasicSuffixModel):
    """Mapping for a non-quantitative property. E.g. the
    name of a tester or a testing facility. The value must not have a
    discrete value but can also be a reference to a column in a table or
    time series."""

    value: Optional[str] = Field(
        None, description="Non-quantitative Value of the property"
    )
    annotation: Optional[AnyUrl] = Field(
        None, description="Base IRI with which the value shall be concatenated"
    )
    value_relation: Optional[Union[str, AnyUrl]] = Field(
        "rdfs:label",
        description="""Data or annotation property
        for mapping the data value to the individual.""",
    )

    @property
    def json_ld(cls) -> Dict[str, Any]:
        """Return dict of json-ld for graph"""
        return {
            "@context": {
                f"{cls.config.prefix_name}": make_prefix(cls.config),
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
            },
            "@id": f"{cls.config.prefix_name}:{cls.suffix}",
            **cls.value_json,
            **cls.types_json,
        }

    @property
    def value_json(cls) -> "Optional[Dict[str, str]]":
        if not isinstance(cls.value, type(None)):
            response = {cls.value_relation: cls.value}
        else:
            response = {}
        return response

    @property
    def types_json(cls) -> "Dict[str, Any]":
        """Dict of json-ld for class types of the individual"""
        if cls.annotation:
            if str(cls.annotation).endswith(cls.config.separator):
                annotation = str(cls.annotation) + cls.value
            else:
                annotation = (
                    str(cls.annotation) + cls.config.separator + cls.value
                )
            types = {
                "@type": [
                    str(cls.iri),
                    annotation,
                ]
            }
        else:
            types = {"@type": str(cls.iri)}
        return types
