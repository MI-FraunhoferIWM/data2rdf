"""Basic data2rdf models"""

import json
from abc import abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import (
    AnyUrl,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)
from rdflib import Graph

from data2rdf.config import Config


class RelationType(str, Enum):
    """Relation Type of TBox modellings"""

    ANNOTATION_PROPERTY = "annotation_property"
    DATA_PROPERTY = "data_property"
    OBJECT_PROPERTY = "object_property"
    PROPERTY = "property"


class BaseConfigModel(BaseModel):
    """Basic model for holding the data2rdf config"""

    config: Config = Field(
        default_factory=Config, description="Configuration object"
    )
    model_config = ConfigDict(exclude={"config"})

    def __str__(self) -> str:
        """Pretty print the model"""
        values = ",\n".join(
            [
                f"\t{key}={value}"
                for key, value in self.__dict__.items()
                if key not in self.model_config.get("exclude")
            ]
        )
        return f"{self.__class__.__name__}(\n{values})"

    def __repr__(self) -> str:
        """Pretty print the model"""
        return str(self)

    @field_validator("config")
    @classmethod
    def validate_config(cls, value: Union[Dict[str, Any], Config]) -> Config:
        """Validate configuration"""
        if isinstance(value, dict):
            value = Config(**value)
        return value


class BasicConceptMapping(BaseConfigModel):
    """Basic mapping for a concept in a file"""

    key: Optional[str] = Field(
        None, description="Key/column of the concept in the file"
    )


class BasicGraphModel(BasicConceptMapping):
    """Basic model for merging data with mappings to become a graph"""

    @property
    @abstractmethod
    def json_ld(self) -> Dict[str, Any]:
        """Return dict for json-ld of graph"""

    @property
    def graph(self) -> Graph:
        """Return graph object based on json-ld"""
        graph = Graph(identifier=self.config.graph_identifier)
        graph.parse(data=json.dumps(self.json_ld), format="json-ld")
        return graph


class BasicSuffixModel(BaseConfigModel):
    """Pydantic BaseModel for suffix and type of a class instance"""

    iri: Union[str, AnyUrl, List[Union[str, AnyUrl]]] = Field(
        ..., description="Ontological class related to this concept"
    )
    suffix: Optional[str] = Field(
        None,
        description="""Optional suffix of the individual
        which will be constructed. If not set, the suffix of the iri
        of the ontological class will be taken""",
        validate_default=True,
    )

    @field_validator("iri")
    @classmethod
    def validate_iri(cls, value: Union[AnyUrl, List[AnyUrl]]) -> AnyUrl:
        """Make sure that there are not blank spaces in the IRI"""
        if not isinstance(value, list):
            value = AnyUrl(str(value).strip())
        else:
            value = [AnyUrl(str(iterable).strip()) for iterable in value]
        return value

    @model_validator(mode="after")
    @classmethod
    def validate_suffix(
        cls,
        self: "BasicSuffixModel",
    ) -> "BasicSuffixModel":
        """Return suffix for individal"""

        if isinstance(self.iri, list) and self.suffix is None:
            raise TypeError("If the iri is a list, the suffix must be set ")

        self.suffix = (
            self.suffix or str(self.iri).split(self.config.separator)[-1]
        )
        return self
