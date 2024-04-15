"""Data2RDF parser utilities"""

import json
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from typing import Any, Dict, List, Union

    from data2rdf import Config


def _load_mapping_file(
    mapping: "Union[str, Dict[str, Any]]",
    config: "Config",
    pydantic_model: "Any",
) -> "Dict[str, Any]":
    if not isinstance(mapping, (str, dict)):
        raise TypeError(
            f"""Mapping file must be of type `{str}` or `{dict}`,
            not `{type(mapping)}`."""
        )
    if isinstance(mapping, str):
        if mapping.endswith("xlsx"):
            mapping_df = pd.read_excel(
                mapping,
                sheet_name="sameas",
                engine="openpyxl",
            )
            mapping_df.fillna("", inplace=True)
            mapping_df = mapping_df.apply(lambda s: s.str.replace('"', ""))
            model = {
                row["key"]: row.to_dict() for n, row in mapping_df.iterrows()
            }
        elif mapping.endswith("json"):
            with open(mapping, encoding=config.encoding) as file:
                model = json.load(file)
        else:
            raise TypeError("File type for mapping not supported!")

        result = {key: pydantic_model(**row) for key, row in model.items()}
    if isinstance(mapping, dict):
        result = mapping
    return result


def _strip_unit(symbol: str, char_list: "List[str]") -> str:
    for char in char_list:
        symbol = symbol.strip(char)
    return symbol
