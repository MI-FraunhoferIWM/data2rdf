"""General data2rdf utils"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from data2rdf.config import Config


def make_prefix(config: "Config") -> str:
    if not str(config.base_iri).endswith(config.separator):
        prefix = str(config.base_iri) + config.separator
    else:
        prefix = str(config.base_iri)
    return prefix
