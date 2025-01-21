"""Mapping models for data2rdf"""


from typing import List, Optional, Union

from pydantic import (
    AliasChoices,
    AnyUrl,
    BaseModel,
    Field,
    field_validator,
    model_validator,
)

from .base import BasicConceptMapping, BasicSuffixModel, RelationType


class TBoxBaseMapping(BasicConceptMapping):
    """Mapping between a object/data/annotation property and
    a value under a location in the data file. This"""

    # OVERRIDE
    key: str = Field(
        ...,
        description="""Key/Column/Location of the value in the data file.
        The value can be a float/int/str or URI""",
    )
    relation: Union[str, AnyUrl] = Field(
        ...,
        description="""Object/Data/Annotation property for the value
        resolving from `key` of this model""",
    )
    relation_type: RelationType = Field(
        ..., description="Type of the semantic relation used in the mappings"
    )

    datatype: Optional[str] = Field(
        None,
        description="XSD Datatype of the targed value",
        alias=AliasChoices("datatype", "data_type"),
    )


class PropertySubgraphBaseModel(BasicSuffixModel):
    concatenate: Optional[bool] = Field(
        False,
        description="Concatenate the value and the iri",
        alias=AliasChoices("concatenate", "concat"),
    )


class CustomRelationPropertySubgraph(PropertySubgraphBaseModel):
    value_relation: Optional[str] = Field(
        "rdfs:label",
        description="""Object/Data/Annotation property for the value
        resolving from `key` of this model""",
    )


class CustomRelationQuantitySubgraph(PropertySubgraphBaseModel):
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
    unit: Optional[Union[str, AnyUrl]] = Field(
        None, description="Symbol or QUDT IRI for the mapping"
    )


class CustomRelation(BaseModel):
    """Custom relation model"""

    relation: Union[str, AnyUrl] = Field(
        ...,
        description="""Object/Data/Annotation property for the value
        resolving from `key` of this model""",
    )
    object_location: Optional[str] = Field(
        ...,
        description="Cell number or Jsonpath to the value of the quantity or property",
    )
    object_data_type: Optional[
        Union[
            str, CustomRelationPropertySubgraph, CustomRelationQuantitySubgraph
        ]
    ] = Field(
        None,
        description="XSD Data type of the object or PropertyGraph-mapping or QuantityGraph-mapping",
        alias=AliasChoices(
            "object_datatype", "object_data_type", "object_type"
        ),
    )
    relation_type: Optional[RelationType] = Field(
        None, description="Type of the semantic relation used in the mappings"
    )


class ABoxBaseMapping(BasicConceptMapping, BasicSuffixModel):
    """Base class for mapping during A Box modelling"""

    unit: Optional[Union[str, AnyUrl]] = Field(
        None, description="Symbol or QUDT IRI for the mapping"
    )
    annotation: Optional[Union[str, AnyUrl]] = Field(
        None, description="Base IRI with which the value shall be concatenated"
    )
    custom_relations: Optional[List[CustomRelation]] = Field(
        None,
        description="""In case if `value_location`, `unit_location` ,
        `value_relation` and `unit_relation` is not used, a user can also
        specify the properties of the individual produced in this custom relation
        fields.""",
    )

    source: Optional[str] = Field(
        None,
        description="""In case if the json parser is used and the `custom_relations` are set:
                                  Source and iterate over mupltiple objects from a given jsonpath, e.g. "$.data[*]".
                                  The mapping will be applied to all the iterated objects.""",
    )

    value_location: Optional[str] = Field(
        None,
        description="Cell number or Jsonpath to the value of the quantity or property",
    )
    unit_location: Optional[str] = Field(
        None, description="cell number or Jsonpath to the unit of the property"
    )
    value_relation: Optional[Union[str, AnyUrl]] = Field(
        None,
        description="""Data or annotation property
        for mapping the data value to the individual.""",
    )
    value_relation_type: Optional[RelationType] = Field(
        None, description="Type of the semantic relation used in the mappings"
    )
    value_datatype: Optional[str] = Field(
        None, description="XSD Datatype of the targed value"
    )
    unit_relation: Optional[Union[str, AnyUrl]] = Field(
        None,
        description="""Object property for mapping the IRI
         of the unit to the individual, in case the concept
         is a quantity and has a unit""",
    )
    suffix_from_location: bool = Field(
        False,
        description="When enabled, the suffix will be taken from the location, e.g. a cell number",
    )

    @field_validator("annotation", mode="after")
    @classmethod
    def validate_annotation(
        cls, value: Optional[Union[str, AnyUrl]]
    ) -> Optional[AnyUrl]:
        if not (isinstance(value, str) and len(value) == 0) or isinstance(
            value, AnyUrl
        ):
            return value

    @model_validator(mode="after")
    @classmethod
    def validate_model(cls, self: "ABoxBaseMapping") -> "ABoxBaseMapping":
        """Validate model"""
        if (
            self.value_location
            or self.unit_location
            or self.value_relation
            or self.unit_relation
        ) and self.custom_relations:
            raise ValueError(
                "value_location, unit_location, value_relation and unit_relation are mutually exclusive with custom_relations"
            )
        return self


class ABoxExcelMapping(ABoxBaseMapping):
    """A special model for mapping from excel files to semantic concepts in the ABox"""

    dataframe_start: Optional[str] = Field(
        None,
        description="Cell location for the start of the dataframe quantity",
        alias=AliasChoices("dataframe_start", "time_series_start"),
    )
    worksheet: Optional[str] = Field(
        None,
        description="Name of the worksheet where the entity is located in the excel file",
    )
