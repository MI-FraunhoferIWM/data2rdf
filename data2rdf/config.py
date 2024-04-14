# The csv2rdf conversion requires a set of relations and classes to use for
# the annotation these are defined separately, so that they can be easily
# adapted.
from pydantic import AnyUrl, Field
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
        "https://www.example.org/download/",
        description="General base iri for downloading the time series after uploading",
    )
