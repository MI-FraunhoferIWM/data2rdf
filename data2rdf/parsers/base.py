"""Data2RDF base model for parsers"""

import json
import warnings
from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Union

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
    import pandas as pd

    from data2rdf import BasicConceptMapping


class BaseParser(BaseModel):
    """Basic Parser for any data file and mode"""

    raw_data: Union[str, bytes, Dict[str, Any], List[Dict[str, Any]]] = Field(
        ...,
        description="""
        In case of a csv: `str` with the file path or the content of the file itself.
        In case of a json file: `dict` for the content of the file of `str` for the file content or file path.
        In case of an excel file: `btyes` for the content or `str` for the file path""",
    )
    mapping: Union[str, List[Any]] = Field(
        ...,
        description="""File path to the mapping file to be parsed or
        a list with the mapping.""",
    )

    dropna: bool = Field(
        False,
        description="Drop all rows where ONLY NaN and None occur in the dataframe.",
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


class AnyBoxBaseParser(BaseParser):
    """Basic parser for A Box or T Box producing an RDF"""

    @property
    @abstractmethod
    def json_ld(self) -> Dict[str, Any]:
        """Return dict for json-ld for the graph"""

    @property
    @abstractmethod
    def mapping_model(self) -> "BaseParser":
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
    def graph(self) -> "Graph":
        """Return RDF Graph from the parsed data."""
        graph = Graph(identifier=self.config.graph_identifier)
        graph.parse(data=json.dumps(self.json_ld), format="json-ld")
        return graph

    @model_validator(mode="after")
    @classmethod
    def run_parser(cls, self: "BaseParser") -> "BaseParser":
        """
        Runs the parser for the given data file and mapping.

        This function is a class method that takes in a `self` parameter, which is an instance of the `BaseParser` class.
        It loads the data file using the `_load_data_file` method and loads the mapping file using the `load_mapping_file` function.
        It then runs the parser using the `_run_parser` method and returns the parsed `BaseParser` instance.

        Args:
            self (BaseParser): The instance of the `BaseParser` class.

        Returns:
            BaseParser: The parsed `BaseParser` instance.
        """

        datafile: Any = cls._load_data_file(self)
        mapping: "Dict[str, BaseParser]" = load_mapping_file(
            self.mapping, self.config, self.mapping_model
        )
        cls._run_parser(self, datafile, mapping)
        return self


class TBoxBaseParser(AnyBoxBaseParser):
    """Basic Parser for TBox mode"""

    suffix_location: str = Field(
        ...,
        description="""Key/column name/reference to the locaton in the data file
        where the suffix of the ontological class to be created.""",
    )

    rdfs_type_location: Optional[str] = Field(
        None,
        description="""Key/column name/reference to location in the data file
        where the rdfs:type for the concepts is defined.""",
    )

    version_info: Optional[str] = Field(
        None, description="Version of the ontology"
    )

    ontology_iri: Optional[Union[str, AnyUrl]] = Field(
        None, description="General IRI of the ontology."
    )

    ontology_title: Optional[str] = Field(
        None, description="Title of the ontology"
    )

    authors: Optional[List[str]] = Field(
        None, description="Name of the authors contributing to the ontology."
    )

    fillna: Optional[Any] = Field(
        "", description="Value to fill NaN values in the parsed dataframe."
    )

    _classes: Any = PrivateAttr()

    @property
    def classes(self) -> "List[BasicConceptMapping]":
        """Return list object with class models"""
        return self._classes


class ABoxBaseParser(AnyBoxBaseParser):
    """Basic Parser for ABox mode"""

    _general_metadata: Any = PrivateAttr()
    _dataframe_metadata: Any = PrivateAttr()
    _dataframe: Any = PrivateAttr()

    @property
    def general_metadata(self) -> "List[BasicConceptMapping]":
        """Return list object with general metadata"""
        return self._general_metadata

    @property
    def dataframe_metadata(self) -> "List[BasicConceptMapping]":
        """Return list object with general metadata"""
        return self._dataframe_metadata

    @property
    def dataframe(self) -> "pd.DataFrame":
        """Return times series found in the data as pd.DataFrame"""
        return self._dataframe

    @property
    def plain_metadata(self) -> List[Dict[str, Any]]:
        message = """
        `plain_metadata` is deprecated and will be removed in a future version.
        Use the `to_dict()` instead."""
        warnings.warn(message, DeprecationWarning)
        return self.to_dict()

    def to_dict(
        self, schema: Callable = None
    ) -> "Union[Dict[str, Any], List[Dict[str, Any]]]":
        """
        Return general metadata as a list of dictionaries.

        The list contains dictionaries, where the key is the label of the metadata,
        and the value is a dictionary with the keys 'label' and 'value'. If the
        metadata has a measurement unit associated with it, the dictionary will
        also contain the key 'measurement_unit' with the value of the measurement
        unit.

        If the schema parameter is provided, it will be used to transform the
        metadata list. The schema should be a callable which takes the list of
        metadata dictionaries and returns the transformed metadata.

        If no schema is provided, the function will return a dictionary where the
        keys are the labels of the metadata, and the values are the dictionaries
        from the list.

        :param schema: A callable which takes a list of dictionaries and returns
            the transformed metadata.
        :return: A dictionary or list of dictionaries with the metadata.
        """
        metadata = []
        for metadatum in self.general_metadata:
            prop = {
                "label": metadatum.suffix,
                "value": metadatum.value,
                "relation_mapping": {
                    "class_iri": str(metadatum.iri),
                },
            }
            if hasattr(metadatum, "measurement_unit"):
                prop[
                    "measurement_unit"
                ] = metadatum.measurement_unit.model_dump(exclude={"config"})
            metadata.append(prop)
        if not isinstance(schema, type(None)):
            metadata = schema(metadata)
        else:
            metadata = {datum.get("label"): datum for datum in metadata}
        return metadata


class BaseFileParser(BaseParser):
    """Base model for data files which can be run in abox
    or tbox mode. The respective `ABoxBaseParser` and
    `TBoxBaseParser` must be set as properties for this model.
    The childclasses of this `BaseFileParser` will be directly used by the main
    `Data2RDF` class later."""

    mode: PipelineMode = Field(
        PipelineMode.ABOX, description="Run parser in ABox or TBox mode."
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
        return self._tbox

    @model_validator(mode="after")
    @classmethod
    def execute_parser(cls, self: "BaseFileParser") -> "BaseFileParser":
        """
        Validates the parser model and executes the parser based on the specified mode.

        Args:
            self: An instance of the BaseFileParser class.

        Returns:
            An instance of the BaseFileParser class with the parser executed.
        """
        arguments = {
            "mapping": self.mapping,
            "raw_data": self.raw_data,
            "config": self.config,
            **self.parser_args,
        }
        if self.mode == PipelineMode.ABOX:
            self._abox = self._abox_parser(**arguments)
        elif self.mode == PipelineMode.TBOX:
            self._tbox = self._tbox_parser(**arguments)
        else:
            raise TypeError(f"Operating mode not understood: {self.mode}")
        return self

    @property
    def plain_metadata(self) -> Dict[str, Any]:
        """Metadata as flat json - without units and iris.
        Useful e.g. for the custom properties of the DSMS."""
        if self.mode == PipelineMode.ABOX:
            return self.abox.plain_metadata
        else:
            raise NotImplementedError(
                "`plain_metadata` is not available in `tbox`-mode."
            )

    def to_dict(self, schema: Callable = None) -> "List[Dict[str, Any]]":
        """Return list of general metadata as DSMS custom properties"""
        if self.mode == PipelineMode.ABOX:
            return self.abox.to_dict(schema=schema)
        else:
            raise NotImplementedError(
                "`to_dict()` is not available in `tbox`-mode."
            )

    @property
    def general_metadata(self) -> "List[BasicConceptMapping]":
        """Return list object with general metadata"""
        if self.mode == PipelineMode.ABOX:
            return self.abox.general_metadata
        else:
            raise NotImplementedError(
                "`general_metadata` is not available in `tbox`-mode."
            )

    @property
    def dataframe_metadata(self) -> "List[BasicConceptMapping]":
        """Return dataframe metadata"""
        if self.mode == PipelineMode.ABOX:
            return self.abox.dataframe_metadata
        else:
            raise NotImplementedError(
                "`dataframe_metadata` is not available in `tbox`-mode."
            )

    @property
    def dataframe(self) -> "Dict[str, Any]":
        """Return dataframe"""
        if self.mode == PipelineMode.ABOX:
            return self.abox.dataframe
        else:
            raise NotImplementedError(
                "`dataframe` is not available in `tbox`-mode."
            )

    @property
    def graph(self) -> Graph:
        """Return RDFlib Graph"""
        if self.mode == PipelineMode.ABOX:
            return self.abox.graph
        else:
            return self.tbox.graph

    @property
    def json_ld(self) -> "Dict[str, Any]":
        """Return JSON LD representation of graph"""
        if self.mode == PipelineMode.ABOX:
            return self.abox.json_ld
        else:
            return self.tbox.json_ld
