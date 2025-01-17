"""CSV Parser pytest"""

import json
import os

import pytest

from ..utils import as_non_dsms_schema, dsms_schema, remove_ids, sort_entries

test_folder = os.path.dirname(os.path.abspath(__file__))
working_folder = os.path.join(test_folder, "input")
output_folder = os.path.join(test_folder, "output")

mapping_folder = os.path.join(working_folder, "mapping")
raw_data = os.path.join(working_folder, "data", "AFZ1-Fz-S1Q.xlsm")
expected = os.path.join(output_folder, "output_excel_parser.ttl")

metadata = {
    "sections": [
        {
            "entries": [
                {
                    "label": "TimeStamp",
                    "value": "2016-10-11 00:00:00",
                    "relation_mapping": {
                        "class_iri": "https://w3id.org/steel/ProcessOntology/TimeStamp"
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
                    "value": 15,
                    "relation_mapping": {
                        "class_iri": "https://w3id.org/steel/ProcessOntology/OriginalGaugeLength"
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
                    "value": 9.5,
                    "relation_mapping": {
                        "class_iri": "https://w3id.org/steel/ProcessOntology/SpecimenWidth"
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
                    "value": 1.5,
                    "relation_mapping": {
                        "class_iri": "https://w3id.org/steel/ProcessOntology/SpecimenThickness"
                    },
                },
                {
                    "label": "SpecimenType",
                    "value": "Fz 10x20",
                    "relation_mapping": {
                        "class_iri": "https://w3id.org/steel/ProcessOntology/SpecimenType"
                    },
                },
                {
                    "label": "SampleIdentifier-2",
                    "value": "123456",
                    "relation_mapping": {
                        "class_iri": "https://w3id.org/steel/ProcessOntology/SampleIdentifier-2"
                    },
                },
                {
                    "label": "ProjectNumber",
                    "value": "Projekt_1",
                    "relation_mapping": {
                        "class_iri": "https://w3id.org/steel/ProcessOntology/ProjectNumber"
                    },
                },
                {
                    "label": "Tester",
                    "value": "Fe",
                    "relation_mapping": {
                        "class_iri": "https://w3id.org/steel/ProcessOntology/Tester"
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
                    "value": 0.02,
                    "relation_mapping": {
                        "class_iri": "https://w3id.org/steel/ProcessOntology/TestingRate"
                    },
                },
                {
                    "label": "MachineData",
                    "value": "M_1",
                    "relation_mapping": {
                        "class_iri": "https://w3id.org/steel/ProcessOntology/MachineData"
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
                    "value": 25,
                    "relation_mapping": {
                        "class_iri": "https://w3id.org/steel/ProcessOntology/Temperature"
                    },
                },
                {
                    "label": "Material",
                    "value": "Werkstoff_1",
                    "relation_mapping": {
                        "class_iri": "https://w3id.org/steel/ProcessOntology/Material"
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
    "PercentageElongation",
    "AbsoluteCrossheadTravel",
    "WidthChange",
]


normal_config = {"graph_identifier": "https://www.example.org"}
bad_config = {"graph_identifier": "https://www.example.org", "foorbar": 123}


def test_xlsx_parser_no_match_in_metadata_from_mapping() -> None:
    from rdflib import Graph

    from data2rdf.models import PropertyGraph, QuantityGraph
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
            parser_args={"unit_from_macro": True, "dropna": True},
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
        assert isinstance(row, QuantityGraph) or isinstance(row, PropertyGraph)

    assert len(parser.dataframe_metadata) == 6
    for row in parser.dataframe_metadata:
        assert isinstance(row, QuantityGraph)

    assert len(parser.dataframe.columns) == 6
    assert sorted(list(parser.dataframe.columns)) == sorted(columns)
    for name, column in parser.dataframe.items():
        assert len(column) == 460


def test_xlsx_parser_no_match_in_timeseries_from_mapping() -> None:
    from rdflib import Graph

    from data2rdf.models import PropertyGraph, QuantityGraph
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
            parser_args={"unit_from_macro": True, "dropna": True},
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
        assert isinstance(row, QuantityGraph) or isinstance(row, PropertyGraph)

    assert len(parser.dataframe_metadata) == 5
    for row in parser.dataframe_metadata:
        assert isinstance(row, QuantityGraph)

    assert len(parser.dataframe.columns) == 5
    for name, column in parser.dataframe.items():
        assert len(column) == 460

    assert remove_ids(parser.to_dict(schema=dsms_schema)) == sort_entries(
        metadata
    )
    assert sort_entries(parser.to_dict()) == as_non_dsms_schema(metadata)


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
            parser_args={"unit_from_macro": True, "dropna": True},
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
    assert remove_ids(parser.to_dict(schema=dsms_schema)) == sort_entries(
        metadata
    )
    assert sort_entries(parser.to_dict()) == as_non_dsms_schema(metadata)
    assert sorted(list(parser.dataframe.columns)) == sorted(columns)


@pytest.mark.parametrize("extension", ["xlsx", "json", "csv", dict])
def test_parser_excel(extension) -> None:
    from rdflib import Graph

    from data2rdf.models import PropertyGraph, QuantityGraph
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
        parser = ExcelParser(
            raw_data=raw_data,
            mapping=mapping,
            parser_args={"unit_from_macro": True, "dropna": True},
        )

    missmatches = [
        warning
        for warning in warnings
        if warning.category == MappingMissmatchWarning
    ]
    assert len(missmatches) == 1

    assert len(parser.general_metadata) == 12
    for row in parser.general_metadata:
        assert isinstance(row, QuantityGraph) or isinstance(row, PropertyGraph)

    assert len(parser.dataframe_metadata) == 6
    for row in parser.dataframe_metadata:
        assert isinstance(row, QuantityGraph)

    assert len(parser.dataframe.columns) == 6
    assert sorted(list(parser.dataframe.columns)) == sorted(columns)
    for name, column in parser.dataframe.items():
        assert len(column) == 460

    expected_graph = Graph()
    expected_graph.parse(expected)

    assert parser.graph.isomorphic(expected_graph)

    assert remove_ids(parser.to_dict(schema=dsms_schema)) == sort_entries(
        metadata
    )
    assert sort_entries(parser.to_dict()) == as_non_dsms_schema(metadata)


@pytest.mark.parametrize("input_kind", ["path", "content"])
def test_parser_excel_inputs(input_kind) -> None:
    from rdflib import Graph

    from data2rdf.models import PropertyGraph, QuantityGraph
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
            parser_args={"unit_from_macro": True, "dropna": True},
        )
    missmatches = [
        warning
        for warning in warnings
        if warning.category == MappingMissmatchWarning
    ]
    assert len(missmatches) == 1

    assert len(parser.general_metadata) == 12
    for row in parser.general_metadata:
        assert isinstance(row, QuantityGraph) or isinstance(row, PropertyGraph)

    assert len(parser.dataframe_metadata) == 6
    for row in parser.dataframe_metadata:
        assert isinstance(row, QuantityGraph)

    assert len(parser.dataframe.columns) == 6
    assert sorted(list(parser.dataframe.columns)) == sorted(columns)
    for name, column in parser.dataframe.items():
        assert len(column) == 460

    expected_graph = Graph()
    expected_graph.parse(expected)

    assert parser.graph.isomorphic(expected_graph)

    assert remove_ids(parser.to_dict(schema=dsms_schema)) == sort_entries(
        metadata
    )
    assert sort_entries(parser.to_dict()) == as_non_dsms_schema(metadata)
