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
raw_data = os.path.join(working_folder, "data", "DX56_D_FZ2_WR00_43.TXT")
expected = os.path.join(output_folder, "output_pipeline.ttl")

parser_args = {"header_sep": "\t", "column_sep": "\t", "metadata_length": 20}
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


def test_csv_pipeline_bad_mapping() -> None:
    from rdflib import Graph

    from data2rdf import AnnotationPipeline, Parser

    pipeline = AnnotationPipeline(
        raw_data=raw_data,
        mapping=os.path.join(mapping_folder, "bad_tensile_test_mapping.json"),
        parser=Parser.csv,
        parser_args=parser_args,
        extra_triples=template,
    )
    expected_graph = Graph()
    expected_graph.parse(expected)

    assert pipeline.graph.isomorphic(expected_graph)


def test_csv_pipeline_no_match_in_mapping() -> None:
    from rdflib import Graph

    from data2rdf import AnnotationPipeline, Parser
    from data2rdf.warnings import MappingMissmatchWarning

    with pytest.warns(UserWarning, match="No match found") as warnings:
        pipeline = AnnotationPipeline(
            raw_data=os.path.join(
                working_folder, "data", "BAD_DX56_D_FZ2_WR00_43.TXT"
            ),
            parser=Parser.csv,
            extra_triples=template,
            mapping=os.path.join(mapping_folder, "tensile_test_mapping.json"),
            parser_args={
                "header_sep": "\t",
                "column_sep": "\t",
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

    assert pipeline.graph.isomorphic(expected_graph)
    assert sorted(list(pipeline.time_series.keys())) == sorted(columns)


@pytest.mark.parametrize("config", [normal_config, bad_config])
def test_csv_pipeline_config(config) -> None:
    from rdflib import Graph

    from data2rdf import (  # isort:skip
        AnnotationPipeline,
        Parser,
    )

    pipeline = AnnotationPipeline(
        raw_data=raw_data,
        mapping=os.path.join(mapping_folder, "tensile_test_mapping.json"),
        parser=Parser.csv,
        parser_args=parser_args,
        extra_triples=template,
        config=config,
    )
    expected_graph = Graph()
    expected_graph.parse(expected)

    assert pipeline.graph.isomorphic(expected_graph)
    assert str(pipeline.graph.identifier) == config["graph_identifier"]
    assert sorted(list(pipeline.time_series.keys())) == sorted(columns)


@pytest.mark.parametrize("extension", ["xlsx", "json", "csv", dict])
def test_csv_pipeline(extension) -> None:
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
        parser=Parser.csv,
        parser_args=parser_args,
        extra_triples=template,
    )

    assert len(pipeline.general_metadata) == 20
    for row in pipeline.general_metadata:
        assert isinstance(row, QuantityMapping) or isinstance(
            row, PropertyMapping
        )

    assert len(pipeline.time_series_metadata) == 6
    for row in pipeline.time_series_metadata:
        assert isinstance(row, QuantityMapping)

    assert len(pipeline.time_series) == 6
    assert sorted(list(pipeline.time_series.keys())) == sorted(columns)
    for row in pipeline.time_series.values():
        assert len(row) == 5734
        assert isinstance(row, list)

    expected_graph = Graph()
    expected_graph.parse(expected)

    assert pipeline.graph.isomorphic(expected_graph)

    assert pipeline.plain_metadata == metadata


@pytest.mark.parametrize("input_kind", ["path", "content"])
def test_csv_pipeline_inputs(input_kind) -> None:
    from rdflib import Graph

    from data2rdf import (  # isort:skip
        AnnotationPipeline,
        Parser,
        PropertyMapping,
        QuantityMapping,
    )

    if input_kind == "path":
        input_obj = raw_data
    elif input_kind == "content":
        with open(raw_data, encoding="utf-8") as file:
            input_obj = file.read()

    pipeline = AnnotationPipeline(
        raw_data=input_obj,
        mapping=os.path.join(mapping_folder, "tensile_test_mapping.json"),
        parser=Parser.csv,
        parser_args=parser_args,
        extra_triples=template,
    )

    assert len(pipeline.general_metadata) == 20
    for row in pipeline.general_metadata:
        assert isinstance(row, QuantityMapping) or isinstance(
            row, PropertyMapping
        )

    assert len(pipeline.time_series_metadata) == 6
    for row in pipeline.time_series_metadata:
        assert isinstance(row, QuantityMapping)

    assert len(pipeline.time_series) == 6
    assert sorted(list(pipeline.time_series.keys())) == sorted(columns)
    for row in pipeline.time_series.values():
        assert len(row) == 5734
        assert isinstance(row, list)

    expected_graph = Graph()
    expected_graph.parse(expected)

    assert pipeline.graph.isomorphic(expected_graph)

    assert pipeline.plain_metadata == metadata
