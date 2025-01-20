"""JSON pipeline pytest"""

import json
import os

import pytest

from ..utils import dsms_schema, remove_ids, sort_entries

test_folder = os.path.dirname(os.path.abspath(__file__))
working_folder = os.path.join(test_folder, "input")
output_folder = os.path.join(test_folder, "output")

mapping_folder = os.path.join(working_folder, "mapping")
mapping_file = os.path.join(mapping_folder, "tensile_test_mapping.json")
raw_data_file = os.path.join(working_folder, "data", "sample_data.json")
expected = os.path.join(output_folder, "output_json_pipeline.ttl")


metadata = {
    "sections": [
        {
            "entries": [
                {
                    "label": "Remark",
                    "value": "foobar",
                    "relation_mapping": {
                        "class_iri": "https://w3id.org/steel/ProcessOntology/Remark"
                    },
                },
                {
                    "label": "WidthChange",
                    "measurement_unit": {
                        "iri": "http://qudt.org/vocab/unit/MilliM",
                        "label": "Millimetre",
                        "namespace": "http://qudt.org/vocab/unit",
                        "symbol": "mm",
                    },
                    "value": 1.0,
                    "relation_mapping": {
                        "class_iri": "https://w3id.org/steel/ProcessOntology/WidthChange"
                    },
                },
            ],
            "name": "General",
        },
    ],
}

series = {"PercentageElongation": [1.0, 2.0, 3.0], "Force": [2.0, 3.0, 4.0]}


@pytest.mark.parametrize(
    "mapping_format, data_format",
    [(dict, str), (str, str), (dict, dict), (str, dict)],
)
def test_pipeline_json(mapping_format, data_format) -> None:
    from rdflib import Graph

    from data2rdf import Data2RDF, Parser
    from data2rdf.models import PropertyGraph, QuantityGraph

    if mapping_format == str:
        mapping = mapping_file
    else:
        with open(mapping_file, encoding="utf-8") as file:
            mapping = json.load(file)

    if data_format == str:
        raw_data = raw_data_file
    else:
        with open(raw_data_file, encoding="utf-8") as file:
            raw_data = json.load(file)

    pipeline = Data2RDF(
        raw_data=raw_data,
        mapping=mapping,
        parser=Parser.json,
    )

    assert len(pipeline.general_metadata) == 2
    for row in pipeline.general_metadata:
        assert isinstance(row, QuantityGraph) or isinstance(row, PropertyGraph)

    assert len(pipeline.dataframe_metadata) == 2
    for row in pipeline.dataframe_metadata:
        assert isinstance(row, QuantityGraph)

    assert len(pipeline.dataframe.columns) == 2
    assert sorted(series) == sorted(pipeline.dataframe)
    for name, column in pipeline.dataframe.items():
        assert len(column) == 3

    expected_graph = Graph()
    expected_graph.parse(expected)

    assert pipeline.graph.isomorphic(expected_graph)

    assert remove_ids(pipeline.to_dict(schema=dsms_schema)) == sort_entries(
        metadata
    )


@pytest.mark.parametrize("extension", ["xlsx", "json", "csv", dict])
def test_json_pipeline_different_mapping_types(extension) -> None:
    from rdflib import Graph

    from data2rdf import (  # isort:skip
        Data2RDF,
        Parser,
        PropertyGraph,
        QuantityGraph,
    )

    if isinstance(extension, str):
        mapping = os.path.join(
            mapping_folder, f"tensile_test_mapping.{extension}"
        )

    else:
        path = os.path.join(mapping_folder, "tensile_test_mapping.json")
        with open(path, encoding="utf-8") as file:
            mapping = json.load(file)

    pipeline = Data2RDF(
        raw_data=raw_data_file,
        mapping=mapping,
        parser=Parser.json,
    )

    assert len(pipeline.general_metadata) == 2
    for row in pipeline.general_metadata:
        assert isinstance(row, QuantityGraph) or isinstance(row, PropertyGraph)

    assert len(pipeline.dataframe_metadata) == 2
    for row in pipeline.dataframe_metadata:
        assert isinstance(row, QuantityGraph)

    assert len(pipeline.dataframe.columns) == 2
    assert sorted(series) == sorted(pipeline.dataframe)
    for name, column in pipeline.dataframe.items():
        assert len(column) == 3

    expected_graph = Graph()
    expected_graph.parse(expected)

    assert pipeline.graph.isomorphic(expected_graph)

    assert remove_ids(pipeline.to_dict(schema=dsms_schema)) == sort_entries(
        metadata
    )
