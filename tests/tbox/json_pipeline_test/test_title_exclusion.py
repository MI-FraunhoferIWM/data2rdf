"""JSON Pipeline tbox pytest without title"""

import json
import os

import pytest

test_folder = os.path.dirname(os.path.abspath(__file__))
working_folder = os.path.join(test_folder, "input")
output_folder = os.path.join(test_folder, "output")

mapping_folder = os.path.join(working_folder, "mapping")
raw_data = os.path.join(working_folder, "data", "classes.json")
expected = os.path.join(output_folder, "output_json_parser_wo_title.ttl")


def test_json_pipeline_tbox_wo_title() -> None:
    from rdflib import Graph

    from data2rdf.warnings import MappingMissmatchWarning

    from data2rdf import Data2RDF, Parser  # isort:skip

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
            parser=Parser.json,
            parser_args={
                "suffix_location": "Ontological concept ID",
            },
            config={
                "base_iri": "https://w3id.org/dimat",
                "exclude_ontology_title": True,
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
