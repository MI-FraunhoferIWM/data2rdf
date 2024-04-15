from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Union

from pydantic import BaseModel, Field, PrivateAttr

from data2rdf.config import Config
from data2rdf.models.mapping import BasicConceptMapping

if TYPE_CHECKING:
    from typing import List

    from pydantic import AnyUrl


class DataParser(BaseModel):
    """
    generic parser abstract class with common parser attrubutes and functionalities
    """

    raw_data: str = Field(
        ..., description="File path to the data file to be parsed."
    )
    mapping: Union[str, BasicConceptMapping] = Field(
        ..., description="File path to the mapping file to be parsed."
    )
    config: Config = Field(
        default_factory=Config, description="Configuration object"
    )

    _general_metadata: Any = PrivateAttr()
    _time_series_metadata: Any = PrivateAttr()
    _time_series: Any = PrivateAttr()

    @property
    @abstractmethod
    def media_type(cls) -> "Union[str, AnyUrl]":
        """IANA Media type definition of the resources to be parsed."""

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
