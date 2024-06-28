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
}

columns = [
    "TestTime",
    "StandardForce",
    "Extension",
    "PercentageElongation",
    "AbsoluteCrossheadTravel",
    "WidthChange",
]


normal_config = {"graph_identifier": "https://www.example.org"}
bad_config = {"graph_identifier": "https://www.example.org", "foorbar": 123}


def test_xlsx_parser_no_match_in_metadata_from_mapping() -> None:
    from rdflib import Graph

    from data2rdf.models import PropertyMapping, QuantityMapping
    from data2rdf.parsers import ExcelParser
    from data2rdf.warnings import MappingMissmatchWarning

    with pytest.warns(
        MappingMissmatchWarning, match="Concept with key"
    ) as warnings:
        parser = ExcelParser(
            raw_data=raw_data,
            mapping=os.path.join(
                mapping_folder, "bad_metadata_tensile_test_mapping.json"
            ),
        )
    missmatches = [
        warning
        for warning in warnings
        if warning.category == MappingMissmatchWarning
    ]
    assert len(missmatches) == 3

    expected_graph = Graph()
    expected_graph.parse(expected)

    assert len(parser.general_metadata) == 11
    for row in parser.general_metadata:
        assert isinstance(row, QuantityMapping) or isinstance(
            row, PropertyMapping
        )

    assert len(parser.time_series_metadata) == 6
    for row in parser.time_series_metadata:
        assert isinstance(row, QuantityMapping)

    assert len(parser.time_series) == 6
    assert sorted(list(parser.time_series.keys())) == sorted(columns)
    for row in parser.time_series.values():
        assert len(row) == 460
        assert isinstance(row, list)


def test_xlsx_parser_no_match_in_timeseries_from_mapping() -> None:
    from rdflib import Graph

    from data2rdf.models import PropertyMapping, QuantityMapping
    from data2rdf.parsers import ExcelParser
    from data2rdf.warnings import MappingMissmatchWarning

    with pytest.warns(
        MappingMissmatchWarning, match="Concept with key"
    ) as warnings:
        parser = ExcelParser(
            raw_data=raw_data,
            mapping=os.path.join(
                mapping_folder, "bad_timeseries_tensile_test_mapping.json"
            ),
        )

    missmatches = [
        warning
        for warning in warnings
        if warning.category == MappingMissmatchWarning
    ]
    assert len(missmatches) == 3

    expected_graph = Graph()
    expected_graph.parse(expected)

    assert len(parser.general_metadata) == 12
    for row in parser.general_metadata:
        assert isinstance(row, QuantityMapping) or isinstance(
            row, PropertyMapping
        )

    assert len(parser.time_series_metadata) == 5
    for row in parser.time_series_metadata:
        assert isinstance(row, QuantityMapping)

    assert len(parser.time_series) == 5
    for key, row in parser.time_series.items():
        assert key in columns
        assert len(row) == 460
        assert isinstance(row, list)

    assert parser.plain_metadata == metadata


@pytest.mark.parametrize("config", [normal_config, bad_config])
def test_csv_parser_config(config) -> None:
    from rdflib import Graph

    from data2rdf.parsers import ExcelParser
    from data2rdf.warnings import MappingMissmatchWarning

    with pytest.warns(
        MappingMissmatchWarning, match="Concept with key"
    ) as warnings:
        parser = ExcelParser(
            raw_data=raw_data,
            mapping=os.path.join(mapping_folder, "tensile_test_mapping.json"),
            config=config,
        )

    missmatches = [
        warning
        for warning in warnings
        if warning.category == MappingMissmatchWarning
    ]
    assert len(missmatches) == 1

    expected_graph = Graph()
    expected_graph.parse(expected)

    assert parser.graph.isomorphic(expected_graph)
    assert str(parser.graph.identifier) == config["graph_identifier"]
    assert parser.plain_metadata == metadata
    assert sorted(list(parser.time_series.keys())) == sorted(columns)


@pytest.mark.parametrize("extension", ["xlsx", "json", "csv", dict])
def test_parser_excel(extension) -> None:
    from rdflib import Graph

    from data2rdf.models import PropertyMapping, QuantityMapping
    from data2rdf.parsers import ExcelParser
    from data2rdf.warnings import MappingMissmatchWarning

    if isinstance(extension, str):
        mapping = os.path.join(
            mapping_folder, f"tensile_test_mapping.{extension}"
        )

    else:
        path = os.path.join(mapping_folder, "tensile_test_mapping.json")
        with open(path, encoding="utf-8") as file:
            mapping = json.load(file)

    with pytest.warns(
        MappingMissmatchWarning, match="Concept with key `Bemerkungen`"
    ) as warnings:
        parser = ExcelParser(raw_data=raw_data, mapping=mapping)

    missmatches = [
        warning
        for warning in warnings
        if warning.category == MappingMissmatchWarning
    ]
    assert len(missmatches) == 1

    assert len(parser.general_metadata) == 12
    for row in parser.general_metadata:
        assert isinstance(row, QuantityMapping) or isinstance(
            row, PropertyMapping
        )

    assert len(parser.time_series_metadata) == 6
    for row in parser.time_series_metadata:
        assert isinstance(row, QuantityMapping)

    assert len(parser.time_series) == 6
    assert sorted(list(parser.time_series.keys())) == sorted(columns)
    for row in parser.time_series.values():
        assert len(row) == 460
        assert isinstance(row, list)

    expected_graph = Graph()
    expected_graph.parse(expected)

    assert parser.graph.isomorphic(expected_graph)

    assert parser.plain_metadata == metadata


@pytest.mark.parametrize("input_kind", ["path", "content"])
def test_parser_excel_inputs(input_kind) -> None:
    from rdflib import Graph

    from data2rdf.models import PropertyMapping, QuantityMapping
    from data2rdf.parsers import ExcelParser
    from data2rdf.warnings import MappingMissmatchWarning

    if input_kind == "path":
        input_obj = raw_data
    elif input_kind == "content":
        with open(raw_data, "rb") as file:
            input_obj = file.read()

    with pytest.warns(
        MappingMissmatchWarning, match="Concept with key `Bemerkungen`"
    ) as warnings:
        parser = ExcelParser(
            raw_data=input_obj,
            mapping=os.path.join(mapping_folder, "tensile_test_mapping.json"),
        )
    missmatches = [
        warning
        for warning in warnings
        if warning.category == MappingMissmatchWarning
    ]
    assert len(missmatches) == 1

    assert len(parser.general_metadata) == 12
    for row in parser.general_metadata:
        assert isinstance(row, QuantityMapping) or isinstance(
            row, PropertyMapping
        )

    assert len(parser.time_series_metadata) == 6
    for row in parser.time_series_metadata:
        assert isinstance(row, QuantityMapping)

    assert len(parser.time_series) == 6
    assert sorted(list(parser.time_series.keys())) == sorted(columns)
    for row in parser.time_series.values():
        assert len(row) == 460
        assert isinstance(row, list)

    expected_graph = Graph()
    expected_graph.parse(expected)

    assert parser.graph.isomorphic(expected_graph)

    assert parser.plain_metadata == metadata
