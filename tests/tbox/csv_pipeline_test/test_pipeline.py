"""CSV Pipeline tbox pytest"""

import json
import os

import pytest

test_folder = os.path.dirname(os.path.abspath(__file__))
working_folder = os.path.join(test_folder, "input")
output_folder = os.path.join(test_folder, "output")

mapping_folder = os.path.join(working_folder, "mapping")
raw_data = os.path.join(working_folder, "data", "classes.csv")
expected = os.path.join(output_folder, "output_csv_parser.ttl")


@pytest.mark.parametrize("extension", ["xlsx", "json", "csv", dict])
def test_csv_pipeline_tbox(extension) -> None:
    from rdflib import Graph

    from data2rdf.warnings import MappingMissmatchWarning

    from data2rdf import Data2RDF, Parser  # isort:skip

    if isinstance(extension, str):
        mapping = os.path.join(mapping_folder, f"mapping.{extension}")

    else:
        path = os.path.join(mapping_folder, "mapping.json")
        with open(path, encoding="utf-8") as file:
            mapping = json.load(file)

    with pytest.warns(
        MappingMissmatchWarning, match="Data for key"
    ) as warnings:
        pipeline = Data2RDF(
            mode="tbox",
            raw_data=raw_data,
            mapping=mapping,
            parser=Parser.csv,
            parser_args={
                "column_sep": ";",
                "suffix_location": "Ontological concept ID",
                "ontology_title": "Test Ontology",
                "authors": ["Jane Doe"],
                "version_info": "1.0.0",
            },
            config={
                "base_iri": "https://w3id.org/dimat",
            },
        )

    missmatches = [
        warning
        for warning in warnings
        if warning.category == MappingMissmatchWarning
    ]
    assert len(missmatches) == 1

    expected_graph = Graph()
    expected_graph.parse(expected)

    assert pipeline.graph.isomorphic(expected_graph)


@pytest.mark.parametrize("input_kind", ["path", "content"])
def test_csv_pipeline_inputs_tbox(input_kind) -> None:
    from rdflib import Graph

    from data2rdf.warnings import MappingMissmatchWarning

    from data2rdf import (  # isort:skip
        Data2RDF,
        Parser,
    )

    if input_kind == "path":
        input_obj = raw_data
    elif input_kind == "content":
        with open(raw_data, encoding="utf-8") as file:
            input_obj = file.read()

    with pytest.warns(
        MappingMissmatchWarning, match="Data for key"
    ) as warnings:
        pipeline = Data2RDF(
            mode="tbox",
            raw_data=input_obj,
            mapping=os.path.join(mapping_folder, "mapping.json"),
            parser=Parser.csv,
            parser_args={
                "column_sep": ";",
                "suffix_location": "Ontological concept ID",
                "ontology_title": "Test Ontology",
                "authors": ["Jane Doe"],
                "version_info": "1.0.0",
            },
            config={
                "base_iri": "https://w3id.org/dimat",
            },
        )

    missmatches = [
        warning
        for warning in warnings
        if warning.category == MappingMissmatchWarning
    ]
    assert len(missmatches) == 1

    expected_graph = Graph()
    expected_graph.parse(expected)

    assert pipeline.graph.isomorphic(expected_graph)
