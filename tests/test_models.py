"""data2rdf unit test for models"""

from rdflib import Graph


def test_valued_quantity():
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
