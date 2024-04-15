from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Union

from pydantic import BaseModel, Field, PrivateAttr

from data2rdf import ClassConceptMapping, Config

if TYPE_CHECKING:
    from typing import List

    from pydantic import AnyUrl
    from rdflib import Graph

    from data2rdf import BasicConceptMapping


class DataParser(BaseModel):
    """
    generic parser abstract class with common parser attrubutes and functionalities
    """

    raw_data: str = Field(
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
    def plain_metadata(cls) -> "Dict[str, Any]":
        """Metadata as flat json - without units and iris.
        Useful e.g. for the custom properties of the DSMS."""

    @property
    @abstractmethod
    def graph(cls) -> "Graph":
        """Return RDF Graph from the parsed data."""
