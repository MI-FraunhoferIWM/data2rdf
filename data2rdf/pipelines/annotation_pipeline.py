"""Main data2rdf Annotation pipeline"""

import json
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from pydantic import BaseModel, Field, ValidationInfo, field_validator, model_validator
from rdflib import Graph

from data2rdf.config import Config
from data2rdf.models.mapping import ClassConceptMapping
from data2rdf.parsers import Parser
from data2rdf.utils import get_as_jsonld, make_prefix

if TYPE_CHECKING:
    from typing import List

    from data2rdf import BasicConceptMapping


class AnnotationPipeline(BaseModel):

    """
    Runs the complete data2rdf pipeline.
    """

    raw_data: str = Field(
        ..., description="File path to the data file to be parsed."
    )
    mapping: Union[str, ClassConceptMapping] = Field(
        ..., description="File path to the mapping file to be parsed."
    )

    parser: Parser = Field(
        ...,
        description="Parser to be used depending on the type of raw data file.",
    )

    parser_args: Dict[str, Any] = Field(
        {},
        description="A dict with specific arguments for the parser. Is passed to the parser as kwargs.",
    )

    config: Config = Field(
        default_factory=Config, description="Configuration object"
    )

    extra_triples: Optional[Union[str, Graph]] = Field(
        None,
        description="Filepath or rdflib-object for a Graph with extra triples for the resulting pipeline graph.",
    )

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
        else:
            raise TypeError(
                f"`extra_triples` must be of type {str} or {Graph}, not {type(value)}."
            )
        extra_triples = extra_triples.replace(
            config.namespace_placeholder, config.base_iri
        )
        graph = Graph(identifier=cls.config.graph_identifier)
        graph.parse(data=extra_triples)
        return value

    @model_validator(mode="after")
    @classmethod
    def run_pipeline(cls, self: "AnnotationPipeline") -> "AnnotationPipeline":
        """Run pipeline."""
        self.parser = self.parser(
            raw_data=self.raw_data, mapping=self.mapping, config=self.config
        )

        return self

    @property
    def graph(cls) -> Graph:
        """Return graph object"""

        model = {
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
            "dcterms:hasPart": get_as_jsonld(cls.parser.graph),
        }
        if cls.extra_triples:
            model.update(**get_as_jsonld(cls.parser.graph))

        graph = Graph(identifier=cls.config.graph_identifier)
        graph.parse(data=json.dumps(model), format="json-ld")
        return graph

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
