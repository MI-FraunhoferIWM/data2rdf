"""General data2rdf utils"""

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Dict

    from rdflib import Graph

    from data2rdf.config import Config


def get_as_jsonld(graph: "Graph", context: bool = False) -> "Dict[str, Any]":
    serialized = graph.serialize(format="json-ld")
    loaded = json.loads(serialized)
    if context and "@context" in loaded:
        jsonld = loaded.pop("@context")
    elif not context and "@context" in loaded:
        loaded.pop("@context")
        jsonld = loaded
    else:
        jsonld = loaded
    return jsonld


def is_integer(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def make_prefix(config: "Config") -> str:
    if not str(config.base_iri).endswith(config.separator):
        prefix = str(config.base_iri) + config.separator
    else:
        prefix = str(config.base_iri)
    return prefix
