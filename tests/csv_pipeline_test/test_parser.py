"""CSV Parser pytest"""

import json
import os

import pytest

test_folder = os.path.dirname(os.path.abspath(__file__))
working_folder = os.path.join(test_folder, "input")
output_folder = os.path.join(test_folder, "output")

mapping_folder = os.path.join(working_folder, "mapping")
raw_data = os.path.join(working_folder, "data", "DX56_D_FZ2_WR00_43.TXT")
expected = os.path.join(output_folder, "output_csv_parser.ttl")

parser_args = {"header_sep": "\t", "column_sep": "\t", "header_length": 20}

metadata = {
    "TestingFacility": "institute_1",
    "ProjectNumber": "123456",
    "ProjectName": "proj_name_1",
    "TimeStamp": "44335.4",
    "MachineData": "maschine_1",
    "ForceMeasuringDevice": "Kraftaufnehmer_1",
    "DisplacementTransducer": "Wegaufnehmer_1",
    "TestStandard": "ISO-XX",
    "Material": "Werkstoff_1",
    "SpecimenType": "Probentyp_1",
    "Tester": "abc",
    "SampleIdentifier-2": "Probentyp_2",
    "OriginalGaugeLength": 80,
    "ParallelLength": 120,
    "SpecimenThickness": 1.55,
    "SpecimenWidth": 20.04,
    "TestingRate": 0.1,
    "Preload": 2,
    "Temperature": 22,
    "Remark": "",
}

normal_config = {"graph_identifier": "https://www.example.org"}
bad_config = {"graph_identifier": "https://www.example.org", "foorbar": 123}


@pytest.mark.parametrize("config", [normal_config, bad_config])
def test_csv_parser_config(config) -> None:
    from rdflib import Graph

    from data2rdf.parsers import CSVParser

    parser = CSVParser(
        raw_data=raw_data,
        mapping=os.path.join(mapping_folder, "tensile_test_mapping.json"),
        **parser_args,
        config=config,
    )
    expected_graph = Graph()
    expected_graph.parse(expected)

    assert parser.graph.isomorphic(expected_graph)
    assert str(parser.graph.identifier) == config["graph_identifier"]


@pytest.mark.parametrize("extension", ["xlsx", "json", dict])
def test_parser_csv(extension) -> None:
    from rdflib import Graph

    from data2rdf.models import PropertyMapping, QuantityMapping
    from data2rdf.parsers import CSVParser

    if isinstance(extension, str):
        mapping = os.path.join(
            mapping_folder, f"tensile_test_mapping.{extension}"
        )

    else:
        path = os.path.join(mapping_folder, "tensile_test_mapping.json")
        with open(path, encoding="utf-8") as file:
            mapping = json.load(file)

    parser = CSVParser(raw_data=raw_data, mapping=mapping, **parser_args)

    assert len(parser.general_metadata) == 20
    for row in parser.general_metadata:
        assert isinstance(row, QuantityMapping) or isinstance(
            row, PropertyMapping
        )

    assert len(parser.time_series_metadata) == 6
    for row in parser.time_series_metadata:
        assert isinstance(row, QuantityMapping)

    assert len(parser.time_series) == 6
    for row in parser.time_series.values():
        assert len(row) == 5734
        assert isinstance(row, list)

    expected_graph = Graph()
    expected_graph.parse(expected)

    assert parser.graph.isomorphic(expected_graph)

    assert parser.plain_metadata == metadata
