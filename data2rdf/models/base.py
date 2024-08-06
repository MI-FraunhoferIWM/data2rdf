"""Basic data2rdf models"""

import json
from abc import abstractmethod
from typing import Any, Dict, Optional, Union

from pydantic import AnyUrl, BaseModel, Field, ValidationInfo, field_validator
from rdflib import Graph

from data2rdf.config import Config


class BaseConfigModel(BaseModel):
    """Basic model for holding the data2rdf config"""

    config: Config = Field(
        default_factory=Config, description="Configuration object"
    )

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
        None, description="Key/column/ of the concept in the file"
    )


class BasicGraphModel(BasicConceptMapping):
    """Basic model for merging data with mappings to become a graph"""

    @property
    @abstractmethod
    def json_ld(cls) -> Dict[str, Any]:
        """Return dict for json-ld of graph"""

    @property
    def graph(cls) -> Graph:
        """Return graph object based on json-ld"""
        graph = Graph(identifier=cls.config.graph_identifier)
        graph.parse(data=json.dumps(cls.json_ld), format="json-ld")
        return graph


class BasicSuffixModel(BaseConfigModel):
    """Pydantic BaseModel for suffix and type of a class instance"""

    iri: Union[str, AnyUrl] = Field(
        ..., description="Ontological class related to this concept"
    )
    suffix: Optional[str] = Field(
        None,
        description="""Optional suffix of the individual
        which will be constructed. If not set, the suffix of the iri
        of the ontological class will be taken""",
        validate_default=True,
    )

    @field_validator("suffix")
    @classmethod
    def validate_suffix(
        cls, value: Optional[str], info: ValidationInfo
    ) -> str:
        """Return suffix for individal"""

        iri = info.data["iri"]
        config = info.data["config"]
        return value or str(iri).split(config.separator)[-1]
