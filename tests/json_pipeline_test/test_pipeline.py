"""JSON pipeline pytest"""

import json
import os

import pytest

test_folder = os.path.dirname(os.path.abspath(__file__))
working_folder = os.path.join(test_folder, "input")
output_folder = os.path.join(test_folder, "output")

mapping_folder = os.path.join(working_folder, "mapping")
mapping_file = os.path.join(mapping_folder, "tensile_test_mapping.json")
raw_data_file = os.path.join(working_folder, "data", "sample_data.json")
expected = os.path.join(output_folder, "output_json_pipeline.ttl")


metadata = {
    "Remark": "foobar",
    "WidthChange": 1.0,
}

series = {"PercentageElongation": [1.0, 2.0, 3.0], "Force": [2.0, 3.0, 4.0]}


@pytest.mark.parametrize(
    "mapping_format, data_format",
    [(dict, str), (str, str), (dict, dict), (str, dict)],
)
def test_pipeline_json(mapping_format, data_format) -> None:
    from rdflib import Graph

    from data2rdf import AnnotationPipeline, Parser
    from data2rdf.models import PropertyMapping, QuantityMapping

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

    pipeline = AnnotationPipeline(
        raw_data=raw_data,
        mapping=mapping,
        parser=Parser.json,
    )

    assert len(pipeline.general_metadata) == 2
    for row in pipeline.general_metadata:
        assert isinstance(row, QuantityMapping) or isinstance(
            row, PropertyMapping
        )

    assert len(pipeline.time_series_metadata) == 2
    for row in pipeline.time_series_metadata:
        assert isinstance(row, QuantityMapping)

    assert len(pipeline.time_series) == 2
    assert sorted(series) == sorted(pipeline.time_series)
    for row in pipeline.time_series.values():
        assert len(row) == 3
        assert isinstance(row, list)

    expected_graph = Graph()
    expected_graph.parse(expected)

    assert pipeline.graph.isomorphic(expected_graph)

    assert pipeline.plain_metadata == metadata


@pytest.mark.parametrize("extension", ["xlsx", "json", "csv", dict])
def test_json_pipeline_different_mapping_types(extension) -> None:
    from rdflib import Graph

    from data2rdf import (  # isort:skip
        AnnotationPipeline,
        Parser,
        PropertyMapping,
        QuantityMapping,
    )

    if isinstance(extension, str):
        mapping = os.path.join(
            mapping_folder, f"tensile_test_mapping.{extension}"
        )

    else:
        path = os.path.join(mapping_folder, "tensile_test_mapping.json")
        with open(path, encoding="utf-8") as file:
            mapping = json.load(file)

    pipeline = AnnotationPipeline(
        raw_data=raw_data_file,
        mapping=mapping,
        parser=Parser.json,
    )

    assert len(pipeline.general_metadata) == 2
    for row in pipeline.general_metadata:
        assert isinstance(row, QuantityMapping) or isinstance(
            row, PropertyMapping
        )

    assert len(pipeline.time_series_metadata) == 2
    for row in pipeline.time_series_metadata:
        assert isinstance(row, QuantityMapping)

    assert len(pipeline.time_series) == 2
    assert sorted(series) == sorted(pipeline.time_series)
    for row in pipeline.time_series.values():
        assert len(row) == 3
        assert isinstance(row, list)

    expected_graph = Graph()
    expected_graph.parse(expected)

    assert pipeline.graph.isomorphic(expected_graph)

    assert pipeline.plain_metadata == metadata
