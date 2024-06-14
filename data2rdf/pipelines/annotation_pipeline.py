"""Main data2rdf Annotation pipeline"""

import json
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationInfo,
    field_validator,
    model_validator,
)
from rdflib import Graph

from data2rdf.config import Config
from data2rdf.parsers import Parser
from data2rdf.utils import make_prefix

if TYPE_CHECKING:
    from typing import List

    from data2rdf import BasicConceptMapping


class AnnotationPipeline(BaseModel):

    """
    Runs the complete data2rdf pipeline.

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
    - extra_triples (Optional[Union[str, Graph]]): File path or rdflib-object for a Graph with extra triples for the
    resulting pipeline graph.
    """

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

    extra_triples: Optional[Union[str, Graph]] = Field(
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

    @field_validator("extra_triples")
    @classmethod
    def validate_extra_triples(
        cls, value: Optional[Union[str, Graph]], info: ValidationInfo
    ) -> Graph:
        """Validate extra triples."""
        config = info.data.get("config")
        if isinstance(value, str):
            with open(value, encoding=config.encoding) as file:
                extra_triples = file.read()
        elif isinstance(value, Graph):
            extra_triples = value.serialize()
        elif isinstance(value, type(None)):
            extra_triples = None
        else:
            raise TypeError(
                f"`extra_triples` must be of type {str}, {Graph} or {type(None)}, not {type(value)}."
            )
        if extra_triples:
            extra_triples = extra_triples.replace(
                config.namespace_placeholder, str(config.base_iri)
            )
            graph = Graph(identifier=config.graph_identifier)
            graph.parse(data=extra_triples)
        return value

    @model_validator(mode="after")
    @classmethod
    def run_pipeline(cls, self: "AnnotationPipeline") -> "AnnotationPipeline":
        """Run pipeline."""
        self.parser = self.parser(
            raw_data=self.raw_data,
            mapping=self.mapping,
            config=self.config,
            **self.parser_args,
        )

        return self

    @property
    def json_ld(cls) -> Dict[str, Any]:
        """Return dict of json-ld for graph"""
        return {
            "@context": {
                "fileid": make_prefix(cls.config),
                "csvw": "http://www.w3.org/ns/csvw#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "dcat": "http://www.w3.org/ns/dcat#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
                "dcterms": "http://purl.org/dc/terms/",
                "qudt": "http://qudt.org/schema/qudt/",
                "csvw": "http://www.w3.org/ns/csvw#",
                "foaf": "http://xmlns.com/foaf/spec/",
            },
            "@id": "fileid:dataset",
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
            "dcterms:hasPart": cls.parser.json_ld,
        }

    @property
    def graph(cls) -> Graph:
        """Return graph object"""
        graph = Graph(identifier=cls.config.graph_identifier)
        graph.parse(data=json.dumps(cls.json_ld), format="json-ld")
        if cls.extra_triples:
            with open(cls.extra_triples, encoding=cls.config.encoding) as file:
                content = file.read()
            data = content.replace(
                str(cls.config.namespace_placeholder), make_prefix(cls.config)
            )
            extra_triples = Graph(identifier=cls.config.graph_identifier)
            extra_triples.parse(data=data)
            graph += extra_triples
        return graph

    @property
    def plain_metadata(cls) -> Dict[str, Any]:
        """Metadata as flat json - without units and iris.
        Useful e.g. for the custom properties of the DSMS."""
        return cls.parser.plain_metadata

    @property
    def general_metadata(cls) -> "List[BasicConceptMapping]":
        """Return list object with general metadata"""
        return cls.parser.general_metadata

    @property
    def time_series_metadata(cls) -> "List[BasicConceptMapping]":
        """Return list object with general metadata"""
        return cls.parser.time_series_metadata

    @property
    def time_series(cls) -> "List[BasicConceptMapping]":
        """Return list object with general metadata"""
        return cls.parser.time_series
