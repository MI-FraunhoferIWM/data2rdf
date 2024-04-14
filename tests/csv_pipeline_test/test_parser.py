"""CSV Parser pytest"""

import os

from rdflib import Graph

test_folder = os.path.dirname(os.path.abspath(__file__))
working_folder = os.path.join(test_folder, "input")
output_folder = os.path.join(test_folder, "output")

mapping_file = os.path.join(
    working_folder, "mapping", "tensile_test_mapping.xlsx"
)
raw_data = os.path.join(working_folder, "data", "DX56_D_FZ2_WR00_43.TXT")
expected = os.path.join(output_folder, "output_csv_parser.ttl")

parser_args = {"header_sep": "\t", "column_sep": "\t", "header_length": 20}


def test_parser() -> None:
    from data2rdf.models.mapping import PropertyMapping, QuantityMapping
    from data2rdf.parsers.csv import CSVParser

    parser = CSVParser(raw_data=raw_data, mapping=mapping_file, **parser_args)

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
