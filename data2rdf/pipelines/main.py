"""Data2RDF ABox pipeline"""

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from rdflib import Graph

from data2rdf.config import Config
from data2rdf.modes import PipelineMode
from data2rdf.parsers import Parser
from data2rdf.utils import make_prefix

from pydantic import (  # isort:skip
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


if TYPE_CHECKING:
    from data2rdf import BasicConceptMapping


class Data2RDF(BaseModel):

    """
    Data2rdf pipeline.

    Parameters:
    - raw_data (Union[str, bytes, Dict[str, Any]]):
        In case of a csv: `str` with the file path or the content of the file itself.
        In case of a json file: `dict` for the content of the file of `str` for the file content or file path.
        In case of an excel file: `btyes` for the content or `str` for the file path
    - mapping (Union[str, Dict[str, Any]]): File path to the mapping file to be parsed or a dictionary with the mapping.
    - parser (Parser): Parser to be used depending on the type of raw data file.
    - parser_args (Dict[str, Any]): A dictionary with specific arguments for the parser. These are passed to the parser
    as keyword arguments.
    - config (Union[Dict[str, Any], Config]): Configuration object. Defaults to a new instance of Config.
    - additional_triples (Optional[Union[str, Graph]]): File path or rdflib-object for a Graph with extra triples for the
    resulting pipeline graph.
    """

    mode: PipelineMode = Field(
        PipelineMode.ABOX,
        description="""With data2rdf, you are able to model in two modes:
        the ABox (for data instances) or the TBox (for the class hierarchy/taxonomy)""",
    )

    raw_data: Union[str, bytes, Dict[str, Any], List[Dict[str, Any]]] = Field(
        ...,
        description="""
        In case of a csv: `str` with the file path or the content of the file itself.
        In case of a json file: `dict` or `list` for the content of the file of `str` for the file content or file path.
        In case of an excel file: `btyes` for the content or `str` for the file path""",
    )
    mapping: Union[str, List[Any]] = Field(
        ...,
        description="""File path to the mapping file to be parsed or
        a dictionary with the mapping.""",
    )

    parser: Parser = Field(
        ...,
        description="Parser to be used depending on the type of raw data file. ",
    )

    parser_args: Dict[str, Any] = Field(
        {},
        description="A dict with specific arguments for the parser. Is passed to the parser as kwargs.",
    )

    config: Union[Dict[str, Any], Config] = Field(
        default_factory=Config, description="Configuration object"
    )

    additional_triples: Optional[Union[str, Graph]] = Field(
        None,
        description="Filepath or rdflib-object for a Graph with extra triples for the resulting pipeline graph.",
    )

    model_config = ConfigDict(
        arbitrary_types_allowed=True, use_enum_values=True
    )

    @field_validator("config")
    @classmethod
    def validate_config(cls, value: Union[Dict[str, Any], Config]) -> Config:
        """Validate configuration"""
        if isinstance(value, dict):
            value = Config(**value)
        return value

    def _validate_additional_triples(
        self,
        value: Union[str, Graph],
    ) -> Graph:
        """Validate extra triples."""
        if isinstance(value, str):
            potential_path = Path(value)
            if potential_path.is_file():
                with open(value, encoding=self.config.encoding) as file:
                    additional_triples = file.read()
            else:
                additional_triples = value
        elif isinstance(value, Graph):
            additional_triples = value.serialize()
        else:
            raise TypeError(
                f"`additional_triples` must be of type {str}, {Graph} or {type(None)}, not {type(value)}."
            )

        additional_triples = additional_triples.replace(
            self.config.namespace_placeholder,
            make_prefix(self.config),
        )
        graph = Graph(identifier=self.config.graph_identifier)
        graph.parse(data=additional_triples)

        return graph

    @model_validator(mode="after")
    @classmethod
    def run_pipeline(cls, self: "Data2RDF") -> "Data2RDF":
        """Run pipeline."""
        self.parser = self.parser(
            raw_data=self.raw_data,
            mapping=self.mapping,
            config=self.config,
            mode=self.mode,
            parser_args=self.parser_args,
        )

        return self

    @property
    def json_ld(cls) -> Dict[str, Any]:
        """
        Returns a dictionary of JSON-LD for the graph based on the pipeline mode.

        If the pipeline mode is ABOX, it returns a dictionary containing the context,
        id, type, and distribution information of the dataset. If the
        `suppress_file_description` config is False, it also includes the file
        description. Otherwise, it returns the JSON-LD of the ABox parser.

        If the pipeline mode is TBOX, it returns the JSON-LD of the TBox parser.

        Args:
            None

        Returns:
            Dict[str, Any]: A dictionary of JSON-LD for the graph.
        """

        if cls.mode == PipelineMode.ABOX:
            if not cls.config.suppress_file_description:
                model = {
                    "@context": {
                        f"{cls.config.prefix_name}": make_prefix(cls.config),
                        "csvw": "http://www.w3.org/ns/csvw#",
                        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                        "dcat": "http://www.w3.org/ns/dcat#",
                        "xsd": "http://www.w3.org/2001/XMLSchema#",
                        "dcterms": "http://purl.org/dc/terms/",
                        "qudt": "http://qudt.org/schema/qudt/",
                        "csvw": "http://www.w3.org/ns/csvw#",
                        "foaf": "http://xmlns.com/foaf/spec/",
                    },
                    "@id": f"{cls.config.prefix_name}:dataset",
                    "@type": "dcat:Dataset",
                    "dcat:distribution": {
                        "@type": "dcat:Distribution",
                        "dcat:mediaType": {
                            "@type": "xsd:anyURI",
                            "@value": cls.parser.media_type,
                        },
                        "dcat:accessURL": {
                            "@type": "xsd:anyURI",
                            "@value": str(cls.config.data_download_uri),
                        },
                    },
                    "dcterms:hasPart": cls.parser.abox.json_ld,
                }
            else:
                model = cls.parser.abox.json_ld
        elif cls.mode == PipelineMode.TBOX:
            model = cls.parser.tbox.json_ld
        else:
            raise TypeError("Pipeline mode not understood")
        return model

    @property
    def graph(cls) -> Graph:
        """
        Returns a graph object based on the pipeline's JSON-LD data.

        The graph object is created with the identifier specified through the pipeline.
        It is then populated with the JSON-LD data from the pipeline, and if additional
        triples are provided, they are validated and added to the graph.

        Returns:
            Graph: A graph object containing the pipeline's data.
        """

        graph = Graph(identifier=cls.config.graph_identifier)
        graph.parse(data=json.dumps(cls.json_ld), format="json-ld")
        if cls.additional_triples:
            graph += cls._validate_additional_triples(cls.additional_triples)
        return graph

    @property
    def plain_metadata(cls) -> Dict[str, Any]:
        """Metadata as flat json - without units and iris.
        Useful e.g. for the custom properties of the DSMS."""
        if cls.mode == PipelineMode.ABOX:
            return cls.parser.abox.plain_metadata
        else:
            raise NotImplementedError(
                "`plain_metadata` is not available in `tbox`-mode."
            )

    @property
    def general_metadata(cls) -> "List[BasicConceptMapping]":
        """Return list object with general metadata"""
        if cls.mode == PipelineMode.ABOX:
            return cls.parser.abox.general_metadata
        else:
            raise NotImplementedError(
                "`general_metadata` is not available in `tbox`-mode."
            )

    @property
    def time_series_metadata(cls) -> "List[BasicConceptMapping]":
        """Return list object with time series metadata"""
        if cls.mode == PipelineMode.ABOX:
            return cls.parser.abox.time_series_metadata
        else:
            raise NotImplementedError(
                "`time_series_metadata` is not available in `tbox`-mode."
            )

    @property
    def time_series(cls) -> "Dict[str, Any]":
        """Return time series"""
        if cls.mode == PipelineMode.ABOX:
            return cls.parser.abox.time_series
        else:
            raise NotImplementedError(
                "`time_series` is not available in `tbox`-mode."
            )
