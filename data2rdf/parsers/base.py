"""Data2RDF base model for parsers"""

import json
from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Union

from rdflib import Graph

from data2rdf.config import Config
from data2rdf.modes import PipelineMode

from .utils import load_mapping_file

from pydantic import (  # isort:skip
    BaseModel,
    Field,
    PrivateAttr,
    field_validator,
    model_validator,
    AnyUrl,
)


if TYPE_CHECKING:
    from typing import List

    import pandas as pd

    from data2rdf import BasicConceptMapping


class BaseParser(BaseModel):
    """Basic Parser for any data file and mode"""

    raw_data: Union[str, bytes, Dict[str, Any]] = Field(
        ...,
        description="""
        In case of a csv: `str` with the file path or the content of the file itself.
        In case of a json file: `dict` for the content of the file of `str` for the file content or file path.
        In case of an excel file: `btyes` for the content or `str` for the file path""",
    )
    mapping: Union[str, Dict[str, Any]] = Field(
        ...,
        description="""File path to the mapping file to be parsed or
        a dictionary with the mapping.""",
    )

    dropna: bool = Field(
        False,
        description="Drop all rows where ONLY NaN and None occur in the time series.",
    )

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


class TBoxBaseParser(BaseParser):
    """Basic Parser for TBox mode"""

    @property
    @abstractmethod
    def json_ld(self) -> Dict[str, Any]:
        """Return dict for json-ld for the graph"""

    @property
    @abstractmethod
    def mapping_model(cls) -> "BaseParser":
        """Pydantic model for validating mapping.
        Must be a subclass of `ABoxBaseParser` or `TBoxBaseParser`.
        """

    @classmethod
    @abstractmethod
    def _run_parser(
        cls, self, datafile: Any, mapping: "Dict[str, BaseParser]"
    ) -> None:
        """Class method for running parser. The `datafile` argument is the
        object returned by the `_load_data_file` method and the `mapping` is
        a dictionary of the keys/columns from the data file mapped to instances
        of the `mapping_model` property of this class."""

    @classmethod
    @abstractmethod
    def _load_data_file(cls, self: "BaseParser") -> "Dict[str, Any]":
        """Class method for loading data file"""

    @property
    def graph(cls) -> "Graph":
        """Return RDF Graph from the parsed data."""
        graph = Graph(identifier=cls.config.graph_identifier)
        graph.parse(data=json.dumps(cls.json_ld), format="json-ld")
        return graph

    @model_validator(mode="after")
    @classmethod
    def run_parser(cls, self: "BaseParser") -> "BaseParser":
        """Run parser"""

        datafile: Any = cls._load_data_file(self)
        mapping: "Dict[str, BaseParser]" = load_mapping_file(
            self.mapping, self.config, self.mapping_model
        )
        cls._run_parser(self, datafile, mapping)
        return self


class ABoxBaseParser(TBoxBaseParser):
    """Basic Parser for ABox mode"""

    _general_metadata: Any = PrivateAttr()
    _time_series_metadata: Any = PrivateAttr()
    _time_series: Any = PrivateAttr()

    @property
    def general_metadata(self) -> "List[BasicConceptMapping]":
        """Return list object with general metadata"""
        return self._general_metadata

    @property
    def time_series_metadata(self) -> "List[BasicConceptMapping]":
        """Return list object with general metadata"""
        return self._time_series_metadata

    @property
    def time_series(self) -> "pd.DataFrame":
        """Return times series found in the data as pd.DataFrame"""
        return self._time_series

    @property
    def plain_metadata(self) -> "Dict[str, Any]":
        """Metadata as flat json - without units and iris.
        Useful e.g. for the custom properties of the DSMS."""
        return {
            str(metadatum.iri).split(self.config.separator)[
                -1
            ]: metadatum.value
            for metadatum in self.general_metadata
        }


class BaseFileParser(BaseParser):
    """Base model for data files which can be run in abox
    or tbox mode. The respective `ABoxBaseParser` and
    `TBoxBaseParser` must be set as properties for this model.
    The childclasses of this `BaseFileParser` will be directly used by the main
    `Data2RDF` class later."""

    mode: PipelineMode = Field(
        PipelineMode.abox, description="Run parser in ABox or TBox mode."
    )

    parser_args: Dict[str, Any] = Field(
        {},
        description="A dict with specific arguments for the parser. Is passed to the parser as kwargs.",
    )

    _abox: Any = PrivateAttr()
    _tbox: Any = PrivateAttr()

    @property
    @abstractmethod
    def media_type(self) -> "Union[str, AnyUrl]":
        """IANA Media type definition of the resources to be parsed."""

    @property
    @abstractmethod
    def _abox_parser(self) -> "ABoxBaseParser":
        """Childclass of `ABoxBaseParser` for the specific `BaseFileParser`."""

    @property
    @abstractmethod
    def _tbox_parser(self) -> "TBoxBaseParser":
        """Childclass of `TBoxBaseParser` for the specific `BaseFileParser`."""

    @property
    def abox(self) -> "ABoxBaseParser":
        """Return instance of the `abox_parser` after model validation"""
        return self._abox

    @property
    def tbox(self) -> "TBoxBaseParser":
        """Return instance of the `tbox_parser` after model validation"""
        return self._abox

    @model_validator(mode="after")
    @classmethod
    def execute_parser(cls, self: "BaseFileParser") -> "BaseFileParser":
        arguments = {
            "mapping": self.mapping,
            "raw_data": self.raw_data,
            "config": self.config,
            **self.parser_args,
        }
        if self.mode == PipelineMode.abox:
            self._abox = self._abox_parser(**arguments)
        elif self.mode == PipelineMode.tbox:
            self._tbox = self._tbox_parser(**arguments)
        else:
            raise TypeError(f"Operating mode not understood: {self.mode}")
        return self

    @property
    def plain_metadata(cls) -> Dict[str, Any]:
        """Metadata as flat json - without units and iris.
        Useful e.g. for the custom properties of the DSMS."""
        if cls.mode == PipelineMode.abox:
            return cls.abox.plain_metadata
        else:
            raise NotImplementedError(
                "`plain_metadata` is not available in `tbox`-mode."
            )

    @property
    def general_metadata(cls) -> "List[BasicConceptMapping]":
        """Return list object with general metadata"""
        if cls.mode == PipelineMode.abox:
            return cls.abox.general_metadata
        else:
            raise NotImplementedError(
                "`general_metadata` is not available in `tbox`-mode."
            )

    @property
    def time_series_metadata(cls) -> "List[BasicConceptMapping]":
        """Return time series metadata"""
        if cls.mode == PipelineMode.abox:
            return cls.abox.time_series_metadata
        else:
            raise NotImplementedError(
                "`time_series_metadata` is not available in `tbox`-mode."
            )

    @property
    def time_series(cls) -> "Dict[str, Any]":
        """Return time series"""
        if cls.mode == PipelineMode.abox:
            return cls.abox.time_series
        else:
            raise NotImplementedError(
                "`time_series` is not available in `tbox`-mode."
            )

    @property
    def graph(self) -> Graph:
        """Return RDFlib Graph"""
        if self.mode == PipelineMode.abox:
            return self.abox.graph
        else:
            return self.tbox.graph

    @property
    def json_ld(self) -> "Dict[str, Any]":
        """Return JSON LD representation of graph"""
        if self.mode == PipelineMode.abox:
            return self.abox.json_ld
        else:
            return self.tbox.json_ld
