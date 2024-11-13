"""Data2RDF model utilities"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Dict


import ast


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


def detect_datatype(value) -> "Dict[str, Any]":
    """Return json with value definition"""
    if is_integer(value):
        dtype = "xsd:integer"
        value = int(value)
    elif is_float(value):
        dtype = "xsd:float"
        value = float(value)
    elif is_bool(value):
        dtype = "xsd:bool"
        value = bool(value)
    elif is_uri(value):
        dtype = "xsd:anyURI"
        value = str(value)
    elif isinstance(value, str):
        dtype = "xsd:string"
    else:
        raise TypeError(
            f"Datatype of value `{value}` ({type(value)}) cannot be mapped to xsd."
        )

    return {"@type": dtype, "@value": value}


def apply_datatype(value: "Any", datatype: str) -> "Dict[str, Any]":
    """
    Converts the input value to the specified datatype and returns a dictionary
    with the datatype and the converted value.

    Args:
        value (Any): The value to be converted.
        datatype (str): The target datatype as a string. Supported datatypes
                        are "integer", "float", "bool", "anyURI", and "string".

    Returns:
        Dict[str, Any]: A dictionary containing the datatype under the "@type" key
                        and the converted value under the "@value" key.

    Raises:
        TypeError: If the provided datatype is not supported.
    """
    if datatype == "integer":
        value = int(value)
    elif datatype == "float":
        value = float(value)
    elif datatype == "bool":
        value = bool(value)
    elif datatype == "anyURI":
        value = str(value)
    elif datatype == "string":
        value = str(value)
    else:
        raise TypeError(
            f"""Datatype of value `{value}` ({datatype}) currently not supported.
            Supported datatypes: integer, float, bool, anyURI, string"""
        )

    return {"@type": f"xsd:{datatype}", "@value": value}
