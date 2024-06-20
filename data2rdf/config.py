# The csv2rdf conversion requires a set of relations and classes to use for
# the annotation these are defined separately, so that they can be easily
# adapted.
from typing import List, Optional, Union

from pydantic import AnyUrl, ConfigDict, Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """Data2RDF configuration"""

    qudt_units: AnyUrl = Field(
        "http://qudt.org/2.1/vocab/unit",
        description="URI to QUDT Unit ontology for unit conversion",
    )

    qudt_quantity_kinds: AnyUrl = Field(
        "http://qudt.org/vocab/quantitykind/",
        description="URI to QUDT quantity kind ontology for unit conversion",
    )

    base_iri: AnyUrl = Field(
        "https://www.example.org/", description="Base IRI for individuals."
    )

    separator: str = Field(
        "/", description="Separator between base IRI and suffix."
    )

    encoding: str = Field("utf-8", description="Encoding used while parsing.")

    data_download_uri: AnyUrl = Field(
        "https://www.example.org/download",
        description="General base iri for downloading the time series after uploading",
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

    model_config = ConfigDict(extra="ignore")
