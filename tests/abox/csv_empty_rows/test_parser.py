"""Test the csv parser when rows might be empty"""

import os

test_folder = os.path.dirname(os.path.abspath(__file__))
working_folder = os.path.join(test_folder, "input")
output_folder = os.path.join(test_folder, "output")

mapping_folder = os.path.join(working_folder, "mapping")
raw_data = os.path.join(working_folder, "data", "data.csv")
expected = os.path.join(output_folder, "output_csv_parser.ttl")

parser_args = {
    "time_series_sep": ";",
    "metadata_length": 0,
    "time_series_header_length": 1,
    "drop_na": False,
}

columns = [
    "Temperature",
    "ThermalExpansionCoefficient",
    "SpecificHeatCapacity",
    "ModulusOfElasticity",
    "PoissonRatio",
    "ThermalConductivity",
    "MassDensity",
]


config = {"graph_identifier": "https://www.example.org"}


def test_csv_nan_vals() -> None:
    from rdflib import Graph

    from data2rdf import QuantityGraph
    from data2rdf.parsers import CSVParser

    parser = CSVParser(
        raw_data=raw_data,
        mapping=os.path.join(mapping_folder, "mapping.json"),
        parser_args=parser_args,
        config=config,
    )

    expected_graph = Graph()
    expected_graph.parse(expected)

    assert len(parser.general_metadata) == 0

    assert len(parser.time_series_metadata) == 7
    for row in parser.time_series_metadata:
        assert isinstance(row, QuantityGraph)

    assert len(parser.time_series.columns) == 7
    assert sorted(list(parser.time_series.columns)) == sorted(columns)

    for name, column in parser.time_series.items():
        assert len(column) == 31

    assert parser.graph.isomorphic(expected_graph)
    assert parser.plain_metadata == {}
