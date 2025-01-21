import json
import os

import pytest

from ..utils import as_non_dsms_schema, dsms_schema, remove_ids, sort_entries

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

metadata_suffix = {
    "sections": [
        {
            "entries": [
                {
                    "label": "Time2",
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

columns_suffix = [
    "Time1",
    "StandardForce",
    "Extension",
    "PercentageElongation",
    "AbsoluteCrossheadTravel",
    "WidthChange",
]


normal_config = {"graph_identifier": "https://www.example.org"}
bad_config = {"graph_identifier": "https://www.example.org", "foorbar": 123}


@pytest.mark.parametrize("config", [normal_config, bad_config])
def test_xlsx_pipeline_config(config) -> None:
    from rdflib import Graph

    from data2rdf.warnings import MappingMissmatchWarning

    from data2rdf import (  # isort:skip
        Data2RDF,
        Parser,
    )

    with pytest.warns(
        MappingMissmatchWarning, match="Concept with key"
    ) as warnings:
        pipeline = Data2RDF(
            raw_data=raw_data,
            mapping=os.path.join(mapping_folder, "tensile_test_mapping.json"),
            parser=Parser.excel,
            additional_triples=template,
            parser_args={"dropna": True, "unit_from_macro": True},
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

    assert pipeline.graph.isomorphic(expected_graph)
    assert str(pipeline.graph.identifier) == config["graph_identifier"]

    assert remove_ids(pipeline.to_dict(schema=dsms_schema)) == sort_entries(
        metadata
    )
    assert sort_entries(pipeline.to_dict()) == as_non_dsms_schema(metadata)
    assert sorted(list(pipeline.dataframe.columns)) == sorted(columns)


@pytest.mark.parametrize("extension", ["xlsx", "json", "csv", dict])
def test_excel_pipeline(extension) -> None:
    from rdflib import Graph

    from data2rdf.warnings import MappingMissmatchWarning

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

    with pytest.warns(
        MappingMissmatchWarning, match="Concept with key"
    ) as warnings:
        pipeline = Data2RDF(
            raw_data=raw_data,
            mapping=mapping,
            parser=Parser.excel,
            additional_triples=template,
            parser_args={"dropna": True, "unit_from_macro": True},
        )

    missmatches = [
        warning
        for warning in warnings
        if warning.category == MappingMissmatchWarning
    ]
    assert len(missmatches) == 1

    assert len(pipeline.general_metadata) == 12
    for row in pipeline.general_metadata:
        assert isinstance(row, QuantityGraph) or isinstance(row, PropertyGraph)

    assert len(pipeline.dataframe_metadata) == 6
    for row in pipeline.dataframe_metadata:
        assert isinstance(row, QuantityGraph)

    assert len(pipeline.dataframe.columns) == 6
    assert sorted(list(pipeline.dataframe.columns)) == sorted(columns)
    for name, column in pipeline.dataframe.items():
        assert len(column) == 460

    expected_graph = Graph()
    expected_graph.parse(expected)

    assert pipeline.graph.isomorphic(expected_graph)

    assert remove_ids(pipeline.to_dict(schema=dsms_schema)) == sort_entries(
        metadata
    )
    assert sort_entries(pipeline.to_dict()) == as_non_dsms_schema(metadata)


@pytest.mark.parametrize("input_kind", ["path", "content"])
def test_excel_pipeline_inputs(input_kind) -> None:
    from rdflib import Graph

    from data2rdf.warnings import MappingMissmatchWarning

    from data2rdf import (  # isort:skip
        Data2RDF,
        Parser,
        PropertyGraph,
        QuantityGraph,
    )

    if input_kind == "path":
        input_obj = raw_data
    elif input_kind == "content":
        with open(raw_data, "rb") as file:
            input_obj = file.read()

    with pytest.warns(
        MappingMissmatchWarning, match="Concept with key"
    ) as warnings:
        pipeline = Data2RDF(
            raw_data=input_obj,
            mapping=os.path.join(mapping_folder, "tensile_test_mapping.json"),
            parser=Parser.excel,
            additional_triples=template,
            parser_args={"dropna": True, "unit_from_macro": True},
        )

    missmatches = [
        warning
        for warning in warnings
        if warning.category == MappingMissmatchWarning
    ]
    assert len(missmatches) == 1

    assert len(pipeline.general_metadata) == 12
    for row in pipeline.general_metadata:
        assert isinstance(row, QuantityGraph) or isinstance(row, PropertyGraph)

    assert len(pipeline.dataframe_metadata) == 6
    for row in pipeline.dataframe_metadata:
        assert isinstance(row, QuantityGraph)

    assert len(pipeline.dataframe.columns) == 6
    assert sorted(list(pipeline.dataframe.columns)) == sorted(columns)
    for name, column in pipeline.dataframe.items():
        assert len(column) == 460

    expected_graph = Graph()
    expected_graph.parse(expected)

    assert pipeline.graph.isomorphic(expected_graph)

    assert remove_ids(pipeline.to_dict(schema=dsms_schema)) == sort_entries(
        metadata
    )
    assert sort_entries(pipeline.to_dict()) == as_non_dsms_schema(metadata)


def test_excel_pipeline_suffix() -> None:
    from rdflib import Graph

    from data2rdf.warnings import MappingMissmatchWarning

    from data2rdf import (  # isort:skip
        Data2RDF,
        Parser,
    )

    raw_data = os.path.join(working_folder, "data", "AFZ1-Fz-S1Q.xlsm")
    expected = os.path.join(output_folder, "output_pipeline_suffix.ttl")

    with pytest.warns(
        MappingMissmatchWarning, match="Concept with key"
    ) as warnings:
        pipeline = Data2RDF(
            raw_data=raw_data,
            mapping=os.path.join(mapping_folder, "mapping_suffix.json"),
            parser=Parser.excel,
            parser_args={"dropna": True, "unit_from_macro": True},
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

    assert remove_ids(pipeline.to_dict(schema=dsms_schema)) == sort_entries(
        metadata_suffix
    )

    assert sorted(list(pipeline.dataframe.columns)) == sorted(columns_suffix)


def test_excel_pipeline_test_alias() -> None:
    from rdflib import Graph

    from data2rdf.warnings import MappingMissmatchWarning

    from data2rdf import (  # isort:skip
        Data2RDF,
        Parser,
        PropertyGraph,
        QuantityGraph,
    )

    with open(raw_data, "rb") as file:
        input_obj = file.read()

    with pytest.warns(
        MappingMissmatchWarning, match="Concept with key"
    ) as warnings:
        pipeline = Data2RDF(
            raw_data=input_obj,
            mapping=os.path.join(
                mapping_folder, "tensile_test_mapping_alias.json"
            ),
            parser=Parser.excel,
            additional_triples=template,
            parser_args={"dropna": True, "unit_from_macro": True},
        )

    missmatches = [
        warning
        for warning in warnings
        if warning.category == MappingMissmatchWarning
    ]
    assert len(missmatches) == 1

    assert len(pipeline.general_metadata) == 12
    for row in pipeline.general_metadata:
        assert isinstance(row, QuantityGraph) or isinstance(row, PropertyGraph)

    assert len(pipeline.dataframe_metadata) == 6
    for row in pipeline.dataframe_metadata:
        assert isinstance(row, QuantityGraph)

    assert len(pipeline.dataframe.columns) == 6
    assert sorted(list(pipeline.dataframe.columns)) == sorted(columns)
    for name, column in pipeline.dataframe.items():
        assert len(column) == 460

    expected_graph = Graph()
    expected_graph.parse(expected)

    assert pipeline.graph.isomorphic(expected_graph)

    assert remove_ids(pipeline.to_dict(schema=dsms_schema)) == sort_entries(
        metadata
    )
    assert sort_entries(pipeline.to_dict()) == as_non_dsms_schema(metadata)
