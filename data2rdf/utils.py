"""General data2rdf utils"""

import ast
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from data2rdf.config import Config


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


def is_bool(s):
    try:
        ast.literal_eval(s)
        return True
    except Exception:
        return False


def is_uri(s):
    try:
        if str(s).startswith("http://") or str(s).startswith("https://"):
            return True
    except Exception:
        return False


def make_prefix(config: "Config") -> str:
    if not str(config.base_iri).endswith(config.separator):
        prefix = str(config.base_iri) + config.separator
    else:
        prefix = str(config.base_iri)
    return prefix
