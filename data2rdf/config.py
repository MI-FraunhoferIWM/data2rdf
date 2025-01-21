# The csv2rdf conversion requires a set of relations and classes to use for
# the annotation these are defined separately, so that they can be easily
# adapted.
from typing import List, Optional, Union

from pydantic import AnyUrl, ConfigDict, Field, model_validator
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """Data2RDF configuration"""

    qudt_units: Union[str, AnyUrl] = Field(
        "http://qudt.org/2.1/vocab/unit",
        description="URI to QUDT Unit ontology for unit conversion",
    )

    qudt_quantity_kinds: Union[str, AnyUrl] = Field(
        "http://qudt.org/vocab/quantitykind/",
        description="URI to QUDT quantity kind ontology for unit conversion",
    )

    language: str = Field("en", description="Language for the unit labels")

    base_iri: Union[str, AnyUrl] = Field(
        "https://www.example.org", description="Base IRI for individuals."
    )

    prefix_name: str = Field(
        "fileid",
        description="Prefix used referencing the `base_iri` in the context of the graph.",
    )

    separator: str = Field(
        "/", description="Separator between base IRI and suffix."
    )

    encoding: str = Field("utf-8", description="Encoding used while parsing.")

    data_download_uri: Union[str, AnyUrl] = Field(
        "https://www.example.org/download",
        description="General base iri for downloading the dataframe after uploading",
    )

    graph_identifier: Optional[Union[str, AnyUrl]] = Field(
        None, description="Identifier of the graph to be produced."
    )

    namespace_placeholder: Union[str, AnyUrl] = Field(
        "http://abox-namespace-placeholder.org/",
        description="Placeholder of the extra triples to be replaced with the `base_iri` during the pipeline run.",
    )

    remove_from_unit: List[str] = Field(
        ["[", "]", '"', " "],
        description="Characters which should be removed from the input value for the unit",
    )

    mapping_csv_separator: str = Field(
        ";",
        description="When the mapping file is a csv, the separator to be used for parsing",
    )

    remove_from_datafile: List[str] = Field(
        ['"', "\r", "\n"],
        description="""In plain text parsers, e.g. the CSV-parser,
        there might be the need to remove certain characters when parsing""",
    )

    suppress_file_description: bool = Field(
        False,
        description="""In ABox mode, the pipeline is producing an additional
        subgraph graph for describing the data file in its structure, mime type, etc.
        This will be suppressed if enabled.""",
    )

    exclude_ontology_title: bool = Field(
        False,
        description="In TBox mode, exclude the title of the ontology in the graph.",
    )

    model_config = ConfigDict(extra="ignore")

    @model_validator(mode="after")
    @classmethod
    def validate_config(cls, self: "Config") -> "Config":
        for key, value in self.model_fields.items():
            if isinstance(value, AnyUrl):
                setattr(self, key, str(value))
        return self
