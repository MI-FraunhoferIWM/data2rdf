"""CSV Parser pytest"""

import json
import os

import pytest

from ..utils import as_non_dsms_schema, dsms_schema, remove_ids, sort_entries

test_folder = os.path.dirname(os.path.abspath(__file__))
working_folder = os.path.join(test_folder, "input")
output_folder = os.path.join(test_folder, "output")

mapping_folder = os.path.join(working_folder, "mapping")
raw_data = os.path.join(working_folder, "data", "DX56_D_FZ2_WR00_43.TXT")
expected = os.path.join(output_folder, "output_csv_parser.ttl")

parser_args = {
    "metadata_sep": "\t",
    "dataframe_sep": "\t",
    "metadata_length": 20,
}

metadata = {
    "sections": [
        {
            "entries": [
                {
                    "label": "TestingFacility",
                    "value": "institute_1",
                    "relation_mapping": {
                        "class_iri": "https://w3id.org/steel/ProcessOntology/TestingFacility"
                    },
                },
                {
                    "label": "ProjectNumber",
                    "value": "123456",
                    "relation_mapping": {
                        "class_iri": "https://w3id.org/steel/ProcessOntology/ProjectNumber"
                    },
                },
                {
                    "label": "ProjectName",
                    "value": "proj_name_1",
                    "relation_mapping": {
                        "class_iri": "https://w3id.org/steel/ProcessOntology/ProjectName"
                    },
                },
                {
                    "label": "TimeStamp",
                    "value": "44335.4",
                    "relation_mapping": {
                        "class_iri": "https://w3id.org/steel/ProcessOntology/TimeStamp"
                    },
                },
                {
                    "label": "MachineData",
                    "value": "maschine_1",
                    "relation_mapping": {
                        "class_iri": "https://w3id.org/steel/ProcessOntology/MachineData"
                    },
                },
                {
                    "label": "ForceMeasuringDevice",
                    "value": "Kraftaufnehmer_1",
                    "relation_mapping": {
                        "class_iri": "https://w3id.org/steel/ProcessOntology/ForceMeasuringDevice"
                    },
                },
                {
                    "label": "DisplacementTransducer",
                    "value": "Wegaufnehmer_1",
                    "relation_mapping": {
                        "class_iri": "https://w3id.org/steel/ProcessOntology/DisplacementTransducer"
                    },
                },
                {
                    "label": "TestStandard",
                    "value": "ISO-XX",
                    "relation_mapping": {
                        "class_iri": "https://w3id.org/steel/ProcessOntology/TestStandard"
                    },
                },
                {
                    "label": "Material",
                    "value": "Werkstoff_1",
                    "relation_mapping": {
                        "class_iri": "https://w3id.org/steel/ProcessOntology/Material"
                    },
                },
                {
                    "label": "SpecimenType",
                    "value": "Probentyp_1",
                    "relation_mapping": {
                        "class_iri": "https://w3id.org/steel/ProcessOntology/SpecimenType"
                    },
                },
                {
                    "label": "Tester",
                    "value": "abc",
                    "relation_mapping": {
                        "class_iri": "https://w3id.org/steel/ProcessOntology/Tester"
                    },
                },
                {
                    "label": "SampleIdentifier-2",
                    "value": "Probentyp_2",
                    "relation_mapping": {
                        "class_iri": "https://w3id.org/steel/ProcessOntology/SampleIdentifier-2"
                    },
                },
                {
                    "label": "OriginalGaugeLength",
                    "measurement_unit": {
                        "iri": "http://qudt.org/vocab/unit/MilliM",
                        "label": "Millimetre",
                        "namespace": "http://qudt.org/vocab/unit",
                        "symbol": "mm",
                    },
                    "value": 80,
                    "relation_mapping": {
                        "class_iri": "https://w3id.org/steel/ProcessOntology/OriginalGaugeLength"
                    },
                },
                {
                    "label": "ParallelLength",
                    "measurement_unit": {
                        "iri": "http://qudt.org/vocab/unit/MilliM",
                        "label": "Millimetre",
                        "namespace": "http://qudt.org/vocab/unit",
                        "symbol": "mm",
                    },
                    "value": 120,
                    "relation_mapping": {
                        "class_iri": "https://w3id.org/steel/ProcessOntology/ParallelLength"
                    },
                },
                {
                    "label": "SpecimenThickness",
                    "measurement_unit": {
                        "iri": "http://qudt.org/vocab/unit/MilliM",
                        "label": "Millimetre",
                        "namespace": "http://qudt.org/vocab/unit",
                        "symbol": "mm",
                    },
                    "value": 1.55,
                    "relation_mapping": {
                        "class_iri": "https://w3id.org/steel/ProcessOntology/SpecimenThickness"
                    },
                },
                {
                    "label": "SpecimenWidth",
                    "measurement_unit": {
                        "iri": "http://qudt.org/vocab/unit/MilliM",
                        "label": "Millimetre",
                        "namespace": "http://qudt.org/vocab/unit",
                        "symbol": "mm",
                    },
                    "value": 20.04,
                    "relation_mapping": {
                        "class_iri": "https://w3id.org/steel/ProcessOntology/SpecimenWidth"
                    },
                },
                {
                    "label": "TestingRate",
                    "measurement_unit": {
                        "iri": "http://qudt.org/vocab/unit/MilliM-PER-SEC",
                        "label": "Millimetre per Second",
                        "namespace": "http://qudt.org/vocab/unit",
                        "symbol": "mm/s",
                    },
                    "value": 0.1,
                    "relation_mapping": {
                        "class_iri": "https://w3id.org/steel/ProcessOntology/TestingRate"
                    },
                },
                {
                    "label": "Preload",
                    "measurement_unit": {
                        "iri": "http://qudt.org/vocab/unit/MegaPA",
                        "label": "Megapascal",
                        "namespace": "http://qudt.org/vocab/unit",
                        "symbol": "MPa",
                    },
                    "value": 2,
                    "relation_mapping": {
                        "class_iri": "https://w3id.org/steel/ProcessOntology/Preload"
                    },
                },
                {
                    "label": "Temperature",
                    "measurement_unit": {
                        "iri": "http://qudt.org/vocab/unit/DEG_C",
                        "label": "degree Celsius",
                        "namespace": "http://qudt.org/vocab/unit",
                        "symbol": "°C",
                    },
                    "value": 22,
                    "relation_mapping": {
                        "class_iri": "https://w3id.org/steel/ProcessOntology/Temperature"
                    },
                },
                {
                    "label": "Remark",
                    "value": "",
                    "relation_mapping": {
                        "class_iri": "https://w3id.org/steel/ProcessOntology/Remark"
                    },
                },
            ],
            "name": "General",
        },
    ],
}

columns = [
    "TestTime",
    "StandardForce",
    "Extension",
    "Elongation",
    "AbsoluteCrossheadTravel",
    "WidthChange",
]

normal_config = {"graph_identifier": "https://www.example.org"}
bad_config = {"graph_identifier": "https://www.example.org", "foorbar": 123}


def test_csv_parser_bad_mapping() -> None:
    from rdflib import Graph

    from data2rdf.models import PropertyGraph, QuantityGraph
    from data2rdf.parsers import CSVParser

    parser = CSVParser(
        raw_data=raw_data,
        mapping=os.path.join(mapping_folder, "bad_tensile_test_mapping.json"),
        parser_args=parser_args,
    )
    expected_graph = Graph()
    expected_graph.parse(expected)

    assert len(parser.general_metadata) == 20
    for row in parser.general_metadata:
        assert isinstance(row, QuantityGraph) or isinstance(row, PropertyGraph)

    assert len(parser.dataframe_metadata) == 6
    for row in parser.dataframe_metadata:
        assert isinstance(row, QuantityGraph)

    assert len(parser.dataframe.columns) == 6
    assert sorted(list(parser.dataframe.columns)) == sorted(columns)
    for name, column in parser.dataframe.items():
        assert len(column) == 5734

    assert parser.graph.isomorphic(expected_graph)


def test_csv_parser_no_match_in_mapping() -> None:
    from rdflib import Graph

    from data2rdf.models import PropertyGraph, QuantityGraph
    from data2rdf.parsers import CSVParser
    from data2rdf.warnings import MappingMissmatchWarning

    with pytest.warns(
        MappingMissmatchWarning, match="No match found"
    ) as warnings:
        parser = CSVParser(
            raw_data=os.path.join(
                working_folder, "data", "BAD_DX56_D_FZ2_WR00_43.TXT"
            ),
            mapping=os.path.join(mapping_folder, "tensile_test_mapping.json"),
            parser_args={
                "metadata_sep": "\t",
                "dataframe_sep": "\t",
                "metadata_length": 21,
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

    assert len(parser.general_metadata) == 20
    for row in parser.general_metadata:
        assert isinstance(row, QuantityGraph) or isinstance(row, PropertyGraph)

    assert len(parser.dataframe_metadata) == 6
    for row in parser.dataframe_metadata:
        assert isinstance(row, QuantityGraph)

    assert len(parser.dataframe.columns) == 6
    assert sorted(list(parser.dataframe.columns)) == sorted(columns)
    for name, column in parser.dataframe.items():
        assert len(column) == 5734

    assert parser.graph.isomorphic(expected_graph)


@pytest.mark.parametrize("config", [normal_config, bad_config])
def test_csv_parser_config(config) -> None:
    from rdflib import Graph

    from data2rdf.parsers import CSVParser

    parser = CSVParser(
        raw_data=raw_data,
        mapping=os.path.join(mapping_folder, "tensile_test_mapping.json"),
        parser_args=parser_args,
        config=config,
    )
    expected_graph = Graph()
    expected_graph.parse(expected)

    assert parser.graph.isomorphic(expected_graph)
    assert str(parser.graph.identifier) == config["graph_identifier"]
    assert sorted(list(parser.dataframe.columns)) == sorted(columns)


@pytest.mark.parametrize("extension", ["xlsx", "json", "csv", dict])
def test_parser_csv(extension) -> None:
    from rdflib import Graph

    from data2rdf.models import PropertyGraph, QuantityGraph
    from data2rdf.parsers import CSVParser

    if isinstance(extension, str):
        mapping = os.path.join(
            mapping_folder, f"tensile_test_mapping.{extension}"
        )

    else:
        path = os.path.join(mapping_folder, "tensile_test_mapping.json")
        with open(path, encoding="utf-8") as file:
            mapping = json.load(file)

    parser = CSVParser(
        raw_data=raw_data,
        mapping=mapping,
        parser_args=parser_args,
    )

    assert len(parser.general_metadata) == 20
    for row in parser.general_metadata:
        assert isinstance(row, QuantityGraph) or isinstance(row, PropertyGraph)

    assert len(parser.dataframe_metadata) == 6
    for row in parser.dataframe_metadata:
        assert isinstance(row, QuantityGraph)

    assert len(parser.dataframe.columns) == 6
    assert sorted(list(parser.dataframe.columns)) == sorted(columns)
    for name, column in parser.dataframe.items():
        assert len(column) == 5734

    expected_graph = Graph()
    expected_graph.parse(expected)

    assert parser.graph.isomorphic(expected_graph)

    assert remove_ids(parser.to_dict(schema=dsms_schema)) == sort_entries(
        metadata
    )
    assert sort_entries(parser.to_dict()) == as_non_dsms_schema(metadata)


@pytest.mark.parametrize("input_kind", ["path", "content"])
def test_parser_csv_input(input_kind) -> None:
    from rdflib import Graph

    from data2rdf.models import PropertyGraph, QuantityGraph
    from data2rdf.parsers import CSVParser

    if input_kind == "path":
        input_obj = raw_data
    elif input_kind == "content":
        with open(raw_data, encoding="utf-8") as file:
            input_obj = file.read()

    parser = CSVParser(
        raw_data=input_obj,
        mapping=os.path.join(mapping_folder, "tensile_test_mapping.json"),
        parser_args=parser_args,
    )

    assert len(parser.general_metadata) == 20
    for row in parser.general_metadata:
        assert isinstance(row, QuantityGraph) or isinstance(row, PropertyGraph)

    assert len(parser.dataframe_metadata) == 6
    for row in parser.dataframe_metadata:
        assert isinstance(row, QuantityGraph)

    assert len(parser.dataframe.columns) == 6
    assert sorted(list(parser.dataframe.columns)) == sorted(columns)
    for name, column in parser.dataframe.items():
        assert len(column) == 5734

    expected_graph = Graph()
    expected_graph.parse(expected)

    assert parser.graph.isomorphic(expected_graph)

    assert remove_ids(parser.to_dict(schema=dsms_schema)) == sort_entries(
        metadata
    )

    assert sort_entries(parser.to_dict()) == as_non_dsms_schema(metadata)
