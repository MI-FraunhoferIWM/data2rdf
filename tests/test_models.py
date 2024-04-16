"""data2rdf unit test for models"""

import pytest

normal_config = {"graph_identifier": "https://www.example.org"}
bad_config = {"graph_identifier": "https://www.example.org", "foorbar": 123}


@pytest.mark.parametrize("config", [normal_config, bad_config])
def test_quantity_model(config) -> None:
    from rdflib import Graph

    from data2rdf import QuantityMapping

    expected = """@prefix fileid: <https://www.example.org/> .
    @prefix qudt: <http://qudt.org/schema/qudt/> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

    fileid:test a <https://example.org/test> ;
        qudt:hasUnit "http://qudt.org/vocab/unit/MilliM"^^xsd:anyURI ;
        qudt:value "0.1"^^xsd:float .
    """
    expected_graph = Graph()
    expected_graph.parse(format="turtle", data=expected)

    model = QuantityMapping(
        value=0.1,
        key="test",
        unit="mm",
        iri="https://example.org/test",
        config=config,
    )

    assert model.graph.isomorphic(expected_graph)
    assert str(model.graph.identifier) == config["graph_identifier"]


def test_valued_quantity():
    from rdflib import Graph

    from data2rdf import QuantityMapping

    expected = """@prefix fileid: <https://www.example.org/> .
    @prefix qudt: <http://qudt.org/schema/qudt/> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

    fileid:test a <https://example.org/test> ;
        qudt:hasUnit "http://qudt.org/vocab/unit/MilliM"^^xsd:anyURI ;
        qudt:value "0.1"^^xsd:float .
    """
    expected_graph = Graph()
    expected_graph.parse(format="turtle", data=expected)

    model = QuantityMapping(
        value=0.1, key="test", unit="mm", iri="https://example.org/test"
    )

    assert model.graph.isomorphic(expected_graph)
