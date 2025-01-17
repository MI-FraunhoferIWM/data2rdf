"""CSV Pipeline pytest"""

import os

from ..utils import dsms_schema

test_folder = os.path.dirname(os.path.abspath(__file__))
working_folder = os.path.join(test_folder, "input")
output_folder = os.path.join(test_folder, "output")

mapping_folder = os.path.join(working_folder, "mapping")
raw_data = os.path.join(working_folder, "data", "data.csv")
expected = os.path.join(output_folder, "output_csv_pipeline.ttl")

parser_args = {
    "dataframe_sep": ";",
    "metadata_length": 0,
    "dataframe_header_length": 1,
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


def test_csv_na_values_pipeline() -> None:
    from rdflib import Graph

    from data2rdf import (  # isort:skip
        Data2RDF,
        Parser,
        QuantityGraph,
    )

    pipeline = Data2RDF(
        raw_data=raw_data,
        mapping=os.path.join(mapping_folder, "mapping.json"),
        parser=Parser.csv,
        parser_args=parser_args,
        config=config,
    )

    expected_graph = Graph()
    expected_graph.parse(expected)

    assert pipeline.graph.isomorphic(expected_graph)
    assert str(pipeline.graph.identifier) == config["graph_identifier"]
    assert sorted(list(pipeline.dataframe.columns)) == sorted(columns)

    assert len(pipeline.general_metadata) == 0

    assert len(pipeline.dataframe_metadata) == 7
    for row in pipeline.dataframe_metadata:
        assert isinstance(row, QuantityGraph)

    assert len(pipeline.dataframe.columns) == 7
    assert sorted(list(pipeline.dataframe.columns)) == sorted(columns)
    for name, column in pipeline.dataframe.items():
        assert len(column) == 31

    expected_graph = Graph()
    expected_graph.parse(expected)

    assert pipeline.graph.isomorphic(expected_graph)

    assert pipeline.to_dict(schema=dsms_schema) == {}
    assert pipeline.to_dict() == {}
