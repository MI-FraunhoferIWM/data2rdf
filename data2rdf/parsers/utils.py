"""Data2RDF parser utilities"""

import json
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from data2rdf import Config
from data2rdf.models.graph import ClassTypeGraph
from data2rdf.warnings import MappingMissmatchWarning

from data2rdf.models.mapping import (  # isort:skip
    RelationType,
)


if TYPE_CHECKING:
    from typing import Any, Dict, List, Union

    from data2rdf.models.mapping import TBoxBaseMapping
    from data2rdf.parsers.base import TBoxBaseParser


def load_mapping_file(
    mapping: "Union[str, List[Dict[str, Any]]]",
    config: "Config" = Config(),
    model_callable: "Any" = dict,
) -> "List[Any]":
    """
    Load a mapping file and transform its contents into a dictionary format.

    Parameters:
        mapping (Union[str, List[Dict[str, Any]]]): Path to the mapping file (either a string representing the file path or a list containing the mapping directly).
        config (Config, optional): Configuration settings for loading the file. Defaults to Config().
        model_callable (Any, optional): Callable object used to transform each row of the mapping file into the desired format. Defaults to dict.

    Returns:
        List[Any]: A list containing the loaded mapping data.

    Raises:
        TypeError: If the `mapping` parameter is not of type `str` or `dict`, or if the file type for mapping is not supported.

    Note:
        - For Excel files (.xlsx), the 'sameas' sheet is read from the Excel file.
        The contents are then transformed into a dictionary where each row corresponds to a key-value pair.
        - For CSV files (.csv) please take care of the correct separator to be set in the config under `mapping_csv_separator`.
        - For JSON files (.json), the entire file is loaded as a dictionary.
        - If `mapping` is already a dictionary, it is returned as is.

    """
    if not isinstance(mapping, (str, list)):
        raise TypeError(
            f"""Mapping file must be of type `{str}` or `{list}`,
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
            model = [row.to_dict() for n, row in mapping_df.iterrows()]

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
            model = [row.to_dict() for n, row in mapping_df.iterrows()]
        else:
            raise TypeError("File type for mapping not supported!")

        result = [model_callable(**row) for row in model]
    if isinstance(mapping, list):
        result = mapping
    return result


def _strip_unit(symbol: str, char_list: "List[str]") -> str:
    for char in char_list:
        symbol = symbol.strip(char)
    return symbol


def _make_tbox_classes(
    self: "TBoxBaseParser",
    df: "pd.DataFrame",
    mapping: "List[TBoxBaseMapping]",
) -> None:
    self._classes = []
    mapping = {model.key: model for model in mapping}
    if hasattr(self, "header_length"):
        skipped = df[self.header_length - 1 :]
    else:
        skipped = df
    for n, row in skipped.iterrows():
        annotations = []
        datatypes = []
        objects = []

        for key, model in mapping.items():
            try:
                value = row[key]
                if isinstance(value, float) and np.isnan(value):
                    value = self.fillna
                relation_mapping = {
                    "value": value,
                    "relation": model.relation,
                }
                if model.relation_type == RelationType.ANNOTATION_PROPERTY:
                    annotations.append(relation_mapping)
                if model.relation_type == RelationType.DATA_PROPERTY:
                    datatypes.append(relation_mapping)
                if model.relation_type == RelationType.OBJECT_PROPERTY:
                    objects.append(relation_mapping)
            except KeyError:
                raise MappingMissmatchWarning(
                    f"Column with name `{key}` does not exist in provided worksheet."
                )

        subgraph = ClassTypeGraph(
            rdfs_type=self.rdfs_type,
            suffix=row[self.suffix_location],
            annotation_properties=annotations,
            object_properties=objects,
            data_properties=datatypes,
            config=self.config,
        )
        self._classes.append(subgraph)


def _make_tbox_json_ld(cls: "TBoxBaseParser") -> "Dict[str, Any]":
    ontology_iri = cls.ontology_iri or cls.config.base_iri
    return {
        "@context": {
            "owl": "http://www.w3.org/2002/07/owl#",
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "dcterms": "http://purl.org/dc/terms/",
            "foaf": "http://xmlns.com/foaf/spec/",
        },
        "@graph": [model.json_ld for model in cls.classes]
        + [
            {
                "@id": str(ontology_iri),
                "@type": "owl:Ontology",
                "dcterms:title": cls.ontology_title,
                "owl:versionInfo": cls.version_info,
                "dcterms:creator": [
                    {"@type": "foaf:Person", "foaf:name": author}
                    for author in cls.authors
                ],
            },
        ],
    }
