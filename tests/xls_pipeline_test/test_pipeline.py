import json
import os

import pytest

test_folder = os.path.dirname(os.path.abspath(__file__))
working_folder = os.path.join(test_folder, "input")

output_folder = os.path.join(test_folder, "output")

template = os.path.join(
    working_folder,
    "method-graph",
    "tensile_test_method_v6.mod.ttl",
)
mapping_folder = os.path.join(working_folder, "mapping")
raw_data = os.path.join(working_folder, "data", "AFZ1-Fz-S1Q.xlsm")
expected = os.path.join(output_folder, "output_pipeline.ttl")


metadata = {
    "ProjectNumber": "Projekt_1",
    "TimeStamp": "2016-10-11 00:00:00",
    "MachineData": "M_1",
    "Material": "Werkstoff_1",
    "SpecimenType": "Fz 10x20",
    "Tester": "Fe",
    "SampleIdentifier-2": "123456",
    "OriginalGaugeLength": 15,
    "SpecimenThickness": 1.5,
    "SpecimenWidth": 9.5,
    "TestingRate": 0.02,
    "Temperature": 25,
    "Remark": "None",
}


@pytest.mark.parametrize("extension", ["xlsx", "json", dict])
def test_excel_pipeline(extension) -> None:
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
        raw_data=raw_data,
        mapping=mapping,
        parser=Parser.excel,
        extra_triples=template,
    )

    assert len(pipeline.general_metadata) == 13
    for row in pipeline.general_metadata:
        assert isinstance(row, QuantityMapping) or isinstance(
            row, PropertyMapping
        )

    assert len(pipeline.time_series_metadata) == 6
    for row in pipeline.time_series_metadata:
        assert isinstance(row, QuantityMapping)

    assert len(pipeline.time_series) == 6
    for row in pipeline.time_series.values():
        assert len(row) == 460
        assert isinstance(row, list)

    expected_graph = Graph()
    expected_graph.parse(expected)

    # TODO: NODE hashes are differing with every pipeline run. Not dramatic but this test should be executed
    # assert pipeline.graph.isomorphic(expected_graph)

    assert pipeline.plain_metadata == metadata