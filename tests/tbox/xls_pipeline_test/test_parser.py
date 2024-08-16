"""CSV Parser tbox pytest"""

import json
import os

import pytest

test_folder = os.path.dirname(os.path.abspath(__file__))
working_folder = os.path.join(test_folder, "input")
output_folder = os.path.join(test_folder, "output")

mapping_folder = os.path.join(working_folder, "mapping")
raw_data = os.path.join(working_folder, "data", "classes.xlsx")
expected = os.path.join(output_folder, "output_excel_parser.ttl")


@pytest.mark.parametrize("extension", ["xlsx", "json", "csv", dict])
def test_parser_excel_tbox(extension) -> None:
    from rdflib import Graph

    from data2rdf.parsers import ExcelParser

    if isinstance(extension, str):
        mapping = os.path.join(mapping_folder, f"mapping.{extension}")
    else:
        path = os.path.join(mapping_folder, "mapping.json")
        with open(path, encoding="utf-8") as file:
            mapping = json.load(file)

    parser = ExcelParser(
        mode="tbox",
        raw_data=raw_data,
        mapping=mapping,
        parser_args={
            "sheet": "Sheet1",
            "suffix_location": "Ontological concept ID",
            "ontology_title": "Test Ontology",
            "authors": ["Jane Doe"],
            "version_info": "1.0.0",
        },
        config={
            "base_iri": "https://w3id.org/dimat",
        },
    )

    expected_graph = Graph()
    expected_graph.parse(expected)

    assert parser.graph.isomorphic(expected_graph)


@pytest.mark.parametrize("input_kind", ["path", "content"])
def test_parser_excel_inputs_tbox(input_kind) -> None:
    from rdflib import Graph

    from data2rdf.parsers import ExcelParser

    mapping = os.path.join(mapping_folder, "mapping.json")

    if input_kind == "path":
        input_obj = raw_data
    elif input_kind == "content":
        with open(raw_data, "rb") as file:
            input_obj = file.read()

    parser = ExcelParser(
        mode="tbox",
        raw_data=input_obj,
        mapping=mapping,
        parser_args={
            "sheet": "Sheet1",
            "suffix_location": "Ontological concept ID",
            "ontology_title": "Test Ontology",
            "authors": ["Jane Doe"],
            "version_info": "1.0.0",
        },
        config={
            "base_iri": "https://w3id.org/dimat",
        },
    )

    expected_graph = Graph()
    expected_graph.parse(expected)

    assert parser.graph.isomorphic(expected_graph)
