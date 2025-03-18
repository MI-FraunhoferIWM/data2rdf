"""Models for graph construction from semantic concepts"""

import warnings
from typing import Any, Dict, List, Optional, Union

from data2rdf.qudt.utils import _get_qudt_label_and_symbol, _get_query_match
from data2rdf.utils import make_prefix, split_namespace
from data2rdf.warnings import ParserWarning

from data2rdf.models.utils import (  # isort:skip
    apply_datatype,
    detect_datatype,
    is_float,
    is_integer,
)

from data2rdf.models.base import (  # isort:skip
    BasicGraphModel,
    BasicSuffixModel,
    RelationType,
    BaseConfigModel,
)

from pydantic import (  # isort:skip
    AnyUrl,
    AliasChoices,
    BaseModel,
    Field,
    ValidationInfo,
    field_validator,
    model_validator,
)


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
    datatype: Optional[str] = Field(
        None, description="XSD Datatype of the value"
    )


class ClassTypeGraph(BasicGraphModel):
    """Graph of a potential concept or class in the T Box."""

    suffix: str = Field(
        ...,
        description="""Value of the suffix of the
        ontological class to be used""",
    )
    rdfs_type: str = Field(
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

    rdfs_properties: Optional[List[ValueRelationMapping]] = Field(
        None, description="Mappings for rdfs:Properties"
    )

    # OVERRIDE
    @property
    def json_ld(self) -> "Dict[str, Any]":
        annotations = {
            model.relation: (
                apply_datatype(model)
                if model.datatype
                else detect_datatype(str(model.value))
            )
            for model in self.annotation_properties
        }
        datatypes = {
            model.relation: (
                apply_datatype(model.value, model.datatype)
                if model.datatype
                else detect_datatype(str(model.value))
            )
            for model in self.data_properties
        }
        properties = {
            model.relation: (
                apply_datatype(model)
                if model.datatype
                else detect_datatype(str(model.value))
            )
            for model in self.rdfs_properties
        }
        objects = {
            model.relation: {"@id": model.value}
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
            **properties,
        }


class MeasurementUnit(BaseConfigModel):
    iri: Union[str, AnyUrl] = Field(
        ...,
        description="Ontological IRI related to the measurement unit",
    )
    label: Optional[str] = Field(
        None,
        description="Label of the measurement unit",
    )
    symbol: Optional[str] = Field(
        None,
        description="Symbol of the measurement unit",
    )
    namespace: Optional[str] = Field(
        None,
        description="Namespace of the measurement unit",
    )

    @model_validator(mode="after")
    @classmethod
    def validate_measurement_unit(cls, self) -> "MeasurementUnit":
        unit = _get_qudt_label_and_symbol(
            self.iri, self.config.qudt_units, self.config.language
        )
        if not self.label and "label" in unit:
            self.label = unit["label"]
        if not self.symbol and "symbol" in unit:
            self.symbol = unit["symbol"]
        if not self.namespace:
            self.namespace = split_namespace(self.iri)
        return self


class QuantityGraph(BasicGraphModel, BasicSuffixModel):
    """Quantity with or without a discrete value and a unit
    E.g. a quantity with a single value and unit _or_
    a quantity describing a column of a dataframe or table with a unit."""

    unit: Optional[Union[str, AnyUrl]] = Field(
        None, description="QUDT Symbol or any other IRI for the unit mapping"
    )
    value: Optional[Union[int, float, str]] = Field(
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

    measurement_unit: Optional[MeasurementUnit] = Field(
        None,
        description="Detailed QUDT Measurement Unit specification",
        alias=AliasChoices(
            "measurement_unit", "measurementunit", "measurementUnit"
        ),
    )

    @field_validator("value", mode="after")
    @classmethod
    def validate_value(
        cls, value: Union[int, float, str]
    ) -> Union[int, float]:
        if isinstance(value, str) and is_integer(value):
            value = int(value)
        elif isinstance(value, str) and is_float(value):
            value = float(value)
        elif isinstance(value, str):
            warnings.warn(
                f"Cannot type case value from str into float or int: {value}",
                ParserWarning,
            )
        return value

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

    @model_validator(mode="after")
    @classmethod
    def validate_quantity_graph(cls, self) -> "QuantityGraph":
        if not self.measurement_unit and self.unit:
            self.measurement_unit = MeasurementUnit(iri=self.unit)
        if self.measurement_unit and not self.unit:
            self.unit = self.measurement_unit.iri
        return self

    @property
    def json_ld(self) -> Dict[str, Any]:
        """Return dict of json-ld for graph"""
        return {
            "@context": {
                f"{self.config.prefix_name}": make_prefix(self.config),
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
                "qudt": "http://qudt.org/schema/qudt/",
            },
            "@id": f"{self.config.prefix_name}:{self.suffix}",
            "@type": (
                [str(iri) for iri in self.iri]
                if isinstance(self.iri, list)
                else str(self.iri)
            ),
            **self.unit_json,
            **self.value_json,
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
            value = {self.value_relation: detect_datatype(str(self.value))}
        else:
            value = {}
        return value


class PropertyGraph(BasicGraphModel, BasicSuffixModel):
    """Mapping for an individual with arbitrary property. E.g. the
    name of a tester or a testing facility. The value must not have a
    discrete value but can also be a reference to a column in a table or
    dataframe."""

    value: Optional[
        Union[str, int, float, bool, AnyUrl, "PropertyGraph", "QuantityGraph"]
    ] = Field(None, description="Value of the property")
    annotation: Optional[Union[str, AnyUrl]] = Field(
        None, description="Base IRI with which the value shall be concatenated"
    )
    value_relation: Optional[Union[str, AnyUrl]] = Field(
        "rdfs:label",
        description="""Data or annotation property
        for mapping the data value to the individual.""",
        alias=AliasChoices("relation", "value_relation", "valuerelation"),
    )
    value_relation_type: Optional[RelationType] = Field(
        None,
        description="Type of the semantic relation used in the mappings",
        alias=AliasChoices(
            "value_relation_type",
            "value_relationtype",
            "relation_type",
            "relationtype",
        ),
    )
    value_datatype: Optional[str] = Field(
        None,
        description="In case of an annotation or data property, this field indicates the XSD Datatype of the value",
        alias=AliasChoices(
            "value_datatype", "value_data_type", "datatype", "data_type"
        ),
    )

    @field_validator("annotation")
    @classmethod
    def validate_annotation(cls, value: AnyUrl) -> AnyUrl:
        """Make sure that there are not blank spaces in the IRI"""
        if value:
            value = AnyUrl(str(value).strip())
        return value

    @model_validator(mode="after")
    @classmethod
    def validate_value(cls, self: "PropertyGraph") -> "PropertyGraph":
        """
        Validate value of a property graph.

        In case the value is a property graph or a quantity graph, make sure that
        the config is set correctly.
        """
        if isinstance(self.value, (PropertyGraph, QuantityGraph)):
            self.value.config = self.config
        return self

    @model_validator(mode="after")
    @classmethod
    def validate_property_graph(cls, self: "PropertyGraph") -> "PropertyGraph":
        """Validate property graph in order to generate annotations"""
        if self.annotation:
            if str(self.annotation).endswith(self.config.separator):
                self.annotation = str(self.annotation) + self.value
            else:
                self.annotation = (
                    str(self.annotation) + self.config.separator + self.value
                )
        return self

    @property
    def json_ld(self) -> Dict[str, Any]:
        """Return dict of json-ld for graph"""
        return {
            "@context": {
                f"{self.config.prefix_name}": make_prefix(self.config),
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
            },
            "@id": f"{self.config.prefix_name}:{self.suffix}",
            **self.value_json,
            **self.types_json,
        }

    @property
    def value_json(self) -> "Optional[Dict[str, str]]":
        if not isinstance(self.value, type(None)):
            if self.value_relation_type != RelationType.OBJECT_PROPERTY:
                if not self.value_datatype:
                    spec = detect_datatype(str(self.value))
                else:
                    spec = apply_datatype(self.value, self.value_datatype)
                response = {self.value_relation: spec}
            else:
                if isinstance(self.value, (PropertyGraph, QuantityGraph)):
                    response = {self.value_relation: self.value.json_ld}
                else:
                    response = {self.value_relation: {"@id": str(self.value)}}
        else:
            response = {}
        return response

    @property
    def types_json(self) -> "Dict[str, Any]":
        """Dict of json-ld for class types of the individual"""
        if self.annotation:
            types = {
                "@type": [
                    (
                        [str(iri) for iri in self.iri]
                        if isinstance(self.iri, list)
                        else str(self.iri)
                    ),
                    self.annotation,
                ]
            }
        else:
            types = {
                "@type": [
                    (
                        [str(iri) for iri in self.iri]
                        if isinstance(self.iri, list)
                        else str(self.iri)
                    )
                ]
            }
        return types
