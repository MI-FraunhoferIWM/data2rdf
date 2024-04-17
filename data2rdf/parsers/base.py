"""Data2RDF base model for parsers"""

import json
from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Union

from pydantic import BaseModel, Field, PrivateAttr, field_validator
from rdflib import Graph

from data2rdf import ClassConceptMapping, Config

if TYPE_CHECKING:
    from typing import List

    from pydantic import AnyUrl

    from data2rdf import BasicConceptMapping


class DataParser(BaseModel):
    """
    generic parser abstract class with common parser attrubutes and functionalities
    """

    raw_data: Union[str, Dict[str, Any]] = Field(
        ..., description="File path to the data file to be parsed."
    )
    mapping: Union[str, Dict[str, ClassConceptMapping]] = Field(
        ...,
        description="""File path to the mapping file to be parsed or
        a dictionary with the mapping.""",
    )
    config: Config = Field(
        default_factory=Config, description="Configuration object"
    )

    _general_metadata: Any = PrivateAttr()
    _time_series_metadata: Any = PrivateAttr()
    _time_series: Any = PrivateAttr()

    @property
    def graph(cls) -> "Graph":
        """Return RDF Graph from the parsed data."""
        graph = Graph(identifier=cls.config.graph_identifier)
        graph.parse(data=json.dumps(cls.json_ld), format="json-ld")
        return graph

    @property
    def general_metadata(cls) -> "List[BasicConceptMapping]":
        """Return list object with general metadata"""
        return cls._general_metadata

    @property
    def time_series_metadata(cls) -> "List[BasicConceptMapping]":
        """Return list object with general metadata"""
        return cls._time_series_metadata

    @property
    def time_series(cls) -> "List[BasicConceptMapping]":
        """Return list object with general metadata"""
        return cls._time_series

    @property
    def plain_metadata(cls) -> "Dict[str, Any]":
        """Metadata as flat json - without units and iris.
        Useful e.g. for the custom properties of the DSMS."""
        return {
            str(metadatum.iri).split(cls.config.separator)[-1]: metadatum.value
            for metadatum in cls.general_metadata
        }

    @field_validator("config")
    @classmethod
    def validate_config(cls, value: Union[Dict[str, Any], Config]) -> Config:
        """Validate configuration"""
        if isinstance(value, dict):
            value = Config(**value)
        return value

    @classmethod
    @abstractmethod
    def run_parser(cls, self) -> "DataParser":
        """Model validator with mode = 'after' to run the parser."""

    @property
    @abstractmethod
    def media_type(cls) -> "Union[str, AnyUrl]":
        """IANA Media type definition of the resources to be parsed."""

    @property
    @abstractmethod
    def json_ld(cls) -> Dict[str, Any]:
        """Return dict for json ld for graph"""
