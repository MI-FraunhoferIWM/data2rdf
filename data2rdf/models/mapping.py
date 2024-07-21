"""Mapping models for data2rdf"""

from typing import List, Optional, Union

from pydantic import AnyUrl, BaseModel, Field, field_validator

from .base import BaseConfigModel, BasicConceptMapping


class KeyRelationMapping(BaseModel):
    """Mapping between a object/data/annotation property and a value under a location in the data file"""

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


class TBoxBaseMapping(BaseConfigModel):
    """Basic class for mapping during T Box modelling"""

    iri: AnyUrl = Field("owl:Class", description="rdfs:type for this concept")
    suffix_location: str = Field(
        ...,
        description="""Key to the locaton in the data file where the suffix of the
        ontological class to be used""",
    )
    annotation_properties: Optional[List[KeyRelationMapping]] = Field(
        None, description="Mappings for Annotations Properties"
    )
    object_properties: Optional[List[KeyRelationMapping]] = Field(
        None, description="Mappings for Object Properties"
    )
    data_properties: Optional[List[KeyRelationMapping]] = Field(
        None, description="Mappings for Data Properties"
    )


class TBoxExcelMapping(TBoxBaseMapping):
    """A special model for mapping from excel files to semantic concepts in the TBox"""

    worksheet: Optional[str] = Field(
        None,
        description="Name of the worksheet where the entity is located in the excel file",
    )


class ABoxBaseMapping(BasicConceptMapping):
    """Base class for mapping during A Box modelling"""

    unit: Optional[Union[str, AnyUrl]] = Field(
        None, description="Symbol or QUDT IRI for the mapping"
    )
    annotation: Optional[Union[str, AnyUrl]] = Field(
        None, description="Base IRI with which the value shall be concatenated"
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


class ABoxJsonMapping(ABoxBaseMapping):
    """A special model for mapping from json files to semantic concepts in the ABox"""

    value_location: str = Field(
        ..., description="Json path for the value of the quantity or property"
    )
    unit_location: Optional[str] = Field(
        None, description="Json path to the unit of the property"
    )


class ABoxExcelMapping(ABoxBaseMapping):
    """A special model for mapping from excel files to semantic concepts in the ABox"""

    value_location: Optional[str] = Field(
        None, description="Cell location for the value of the quantity"
    )
    unit_location: Optional[str] = Field(
        None, description="Cell location for the unit of the quantity"
    )
    time_series_start: Optional[str] = Field(
        None,
        description="Cell location for the start of the time series quantity",
    )
    worksheet: Optional[str] = Field(
        None,
        description="Name of the worksheet where the entity is located in the excel file",
    )
