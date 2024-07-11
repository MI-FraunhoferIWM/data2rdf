"""Data2RDF parser utilities"""

import json
from typing import TYPE_CHECKING

import pandas as pd

from data2rdf import Config

if TYPE_CHECKING:
    from typing import Any, Dict, List, Union


def load_mapping_file(
    mapping: "Union[str, Dict[str, Any]]",
    config: "Config" = Config(),
    model_callable: "Any" = dict,
) -> "Dict[str, Any]":
    """
    Load a mapping file and transform its contents into a dictionary format.

    Parameters:
        mapping (Union[str, Dict[str, Any]]): Path to the mapping file (either a string representing the file path or a dictionary containing the mapping directly).
        config (Config, optional): Configuration settings for loading the file. Defaults to Config().
        model_callable (Any, optional): Callable object used to transform each row of the mapping file into the desired format. Defaults to dict.

    Returns:
        Dict[str, Any]: A dictionary containing the loaded mapping data.

    Raises:
        TypeError: If the `mapping` parameter is not of type `str` or `dict`, or if the file type for mapping is not supported.

    Note:
        - For Excel files (.xlsx), the 'sameas' sheet is read from the Excel file.
        The contents are then transformed into a dictionary where each row corresponds to a key-value pair.
        - For CSV files (.csv) please take care of the correct separator to be set in the config under `mapping_csv_separator`.
        - For JSON files (.json), the entire file is loaded as a dictionary.
        - If `mapping` is already a dictionary, it is returned as is.

    """
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
        elif mapping.endswith("csv"):
            mapping_df = pd.read_csv(
                mapping,
                sep=config.mapping_csv_separator,
                encoding=config.encoding,
            )
            mapping_df.fillna("", inplace=True)
            mapping_df = mapping_df.apply(lambda s: s.str.replace('"', ""))
            model = {
                row["key"]: row.to_dict() for n, row in mapping_df.iterrows()
            }
        else:
            raise TypeError("File type for mapping not supported!")

        result = {key: model_callable(**row) for key, row in model.items()}
    if isinstance(mapping, dict):
        result = mapping
    return result


def _strip_unit(symbol: str, char_list: "List[str]") -> str:
    for char in char_list:
        symbol = symbol.strip(char)
    return symbol
