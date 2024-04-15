"""CSV Parser pytest"""

import json
import os

import pytest

test_folder = os.path.dirname(os.path.abspath(__file__))
working_folder = os.path.join(test_folder, "input")
output_folder = os.path.join(test_folder, "output")

mapping_folder = os.path.join(working_folder, "mapping")
raw_data = os.path.join(working_folder, "data", "AFZ1-Fz-S1Q.xlsm")
expected = os.path.join(output_folder, "output_excel_parser.ttl")

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
def test_parser(extension) -> None:
    from rdflib import Graph

    from data2rdf.models.mapping import PropertyMapping, QuantityMapping
    from data2rdf.parsers.excel import ExcelParser

    if isinstance(extension, str):
        mapping = os.path.join(
            mapping_folder, f"tensile_test_mapping.{extension}"
        )

    else:
        path = os.path.join(mapping_folder, "tensile_test_mapping.json")
        with open(path, encoding="utf-8") as file:
            mapping = json.load(file)

    parser = ExcelParser(raw_data=raw_data, mapping=mapping)

    assert len(parser.general_metadata) == 13
    for row in parser.general_metadata:
        assert isinstance(row, QuantityMapping) or isinstance(
            row, PropertyMapping
        )

    assert len(parser.time_series_metadata) == 6
    for row in parser.time_series_metadata:
        assert isinstance(row, QuantityMapping)

    assert len(parser.time_series) == 6
    for row in parser.time_series.values():
        assert len(row) == 460
        assert isinstance(row, list)

    expected_graph = Graph()
    expected_graph.parse(expected)
    assert parser.graph.isomorphic(expected_graph)

    assert parser.plain_metadata == metadata