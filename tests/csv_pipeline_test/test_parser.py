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
    "Bemerkung": "",
    "Datum/Uhrzeit": "44335.4",
    "Kraftaufnehmer": "Kraftaufnehmer_1",
    "Maschinendaten": "maschine_1",
    "Messlänge Standardweg": 80,
    "Probenbreite": 20.04,
    "Probendicke": 1.55,
    "Probenkennung 2": "Probentyp_2",
    "Probentyp": "Probentyp_1",
    "Projektname": "proj_name_1",
    "Projektnummer": "123456",
    "Prüfer": "abc",
    "Prüfgeschwindigkeit": 0.1,
    "Prüfinstitut": "institute_1",
    "Prüfnorm": "ISO-XX",
    "Temperatur": 22,
    "Versuchslänge": 120,
    "Vorkraft": 2,
    "Wegaufnehmer": "Wegaufnehmer_1",
    "Werkstoff": "Werkstoff_1",
}


@pytest.mark.parametrize("extension", ["xlsx", "json", dict])
def test_parser(extension) -> None:
    from rdflib import Graph

    from data2rdf.models.mapping import PropertyMapping, QuantityMapping
    from data2rdf.parsers.csv import CSVParser

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
