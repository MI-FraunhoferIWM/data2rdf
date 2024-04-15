import os
import json
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

parser_args = {"header_sep": "\t", "column_sep": "\t", "header_length": 20}
metadata = {'Bemerkung': '',
            'Datum/Uhrzeit': '44335.4',
            'Kraftaufnehmer': 'Kraftaufnehmer_1',
            'Maschinendaten': 'maschine_1',
            'Messlänge Standardweg': 80,
            'Probenbreite': 20.04,
            'Probendicke': 1.55,
            'Probenkennung 2': 'Probentyp_2',
            'Probentyp': 'Probentyp_1',
            'Projektname': 'proj_name_1',
            'Projektnummer': '123456',
            'Prüfer': 'abc',
            'Prüfgeschwindigkeit': 0.1,
            'Prüfinstitut': 'institute_1',
            'Prüfnorm': 'ISO-XX',
            'Temperatur': 22,
            'Versuchslänge': 120,
            'Vorkraft': 2,
            'Wegaufnehmer': 'Wegaufnehmer_1',
            'Werkstoff': 'Werkstoff_1'
 }

@pytest.mark.parametrize("extension", ["xlsx", "json", dict])
def test_csv_pipeline(extension) -> None:
    from rdflib import Graph

    from data2rdf import AnnotationPipeline, Parser, QuantityMapping, PropertyMapping

    if isinstance(extension, str):

        mapping = os.path.join(mapping_folder, f"tensile_test_mapping.{extension}")
    
    else:

        path = os.path.join(mapping_folder, "tensile_test_mapping.json")
        with open(path, "r", encoding="utf-8") as file:
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
    for row in pipeline.time_series.values():
        assert len(row) == 5734
        assert isinstance(row, list)

    expected_graph = Graph()
    expected_graph.parse(expected)

    # TODO: NODE hashes are differing with every pipeline run. Not dramatic but this test should be executed
    #assert pipeline.graph.isomorphic(expected_graph) 

    assert pipeline.plain_metadata == metadata
