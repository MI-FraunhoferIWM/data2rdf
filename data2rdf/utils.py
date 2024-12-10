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


def split_namespace(iri: str) -> tuple[str, str]:
    """
    Split the given iri into a namespace and a localname.

    Args:
        iri: The iri to split.

    Returns:
        A tuple of the namespace and the localname.
    """
    if "#" in iri:
        return iri.split("#")[0]
    else:
        return "/".join(iri.split("/")[:-1])
