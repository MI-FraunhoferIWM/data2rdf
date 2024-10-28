"""JSON pipeline pytest"""


def test_pipeline_dict_custom_properties() -> None:
    from rdflib import Graph

    from data2rdf import Data2RDF, Parser

    data = {
        "data": {
            "name": "Jane Doe",
            "measurement": "Continuous Stiffness Measurement",
        }
    }

    mapping = [
        {
            "value_location": "data.name",
            "value_relation": "http://xmlns.com/foaf/0.1/name",
            "iri": "https://w3id.org/emmo/domain/characterisation-methodology/chameo#Operator",
            "suffix": "Operator1",
        },
        {
            "value_location": "data.measurement",
            "iri": "https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#EMMO_5ca6e1c1-93e9-5e1a-881b-2c2bd38074b1",
            "suffix": "CSM1",
        },
    ]

    addtional_triples = """
    @prefix : <http://abox-namespace-placeholder.org/> .
    @prefix chameo: <https://w3id.org/emmo/domain/characterisation-methodology/chameo#> .

    :CSM1 chameo:hasOperator :Operator1 .
    """

    base_iri = (
        "https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation"
    )

    expected = """
    @prefix foaf: <http://xmlns.com/foaf/0.1/> .
    @prefix ns1: <https://w3id.org/emmo/domain/characterisation-methodology/chameo#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix ns2: <https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

    ns2:CSM1 a ns2:EMMO_5ca6e1c1-93e9-5e1a-881b-2c2bd38074b1 ;
             rdfs:label "Continuous Stiffness Measurement"^^xsd:string ;
             ns1:hasOperator ns2:Operator1 .

    ns2:Operator1 a ns1:Operator ;
                  foaf:name "Jane Doe"^^xsd:string .
    """

    pipeline = Data2RDF(
        raw_data=data,
        mapping=mapping,
        parser=Parser.json,
        additional_triples=addtional_triples,
        config={
            "base_iri": base_iri,
            "separator": "#",
            "prefix_name": "nanoindentation",
            "suppress_file_description": True,
        },
    )

    expected_graph = Graph()
    expected_graph.parse(data=expected)

    assert pipeline.graph.isomorphic(expected_graph)
