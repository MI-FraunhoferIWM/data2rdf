"""Mapping models for data2rdf"""

from enum import Enum
from typing import Optional, Union

from pydantic import AnyUrl, Field, field_validator

from .base import BasicConceptMapping, BasicSuffixModel


class RelationType(str, Enum):
    """Relation Type of TBox modellings"""

    ANNOTATION_PROPERTY = "annotation_property"
    DATA_PROPERTY = "data_property"
    OBJECT_PROPERTY = "object_property"


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


class ABoxBaseMapping(BasicConceptMapping, BasicSuffixModel):
    """Base class for mapping during A Box modelling"""

    unit: Optional[Union[str, AnyUrl]] = Field(
        None, description="Symbol or QUDT IRI for the mapping"
    )
    annotation: Optional[Union[str, AnyUrl]] = Field(
        None, description="Base IRI with which the value shall be concatenated"
    )
    value_relation: Optional[Union[str, AnyUrl]] = Field(
        None,
        description="""Data or annotation property
        for mapping the data value to the individual.""",
    )

    unit_relation: Optional[Union[str, AnyUrl]] = Field(
        None,
        description="""Object property for mapping the IRI
         of the unit to the individual, in case the concept
         is a quantity and has a unit""",
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
