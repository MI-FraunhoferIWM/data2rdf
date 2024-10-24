"""Test custom relations for JSON parser"""
import pytest

DATA = {
    "data": [
        {
            "name": "Jane",
            "age": 28,
            "lab_no": 123,
        },
        {
            "name": "John",
            "age": 32,
            "lab_no": 345,
        },
    ]
}

EXPECTED = """
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix ns1: <https://w3id.org/emmo/domain/characterisation-methodology/chameo#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix ns2: <https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#> .
@prefix ns3: <https://w3id.org/steel/ProcessOntology/> .

ns2:Jane a ns1:Operator ;
            foaf:name "Jane" ;
            foaf:age 28 ;
            ns3:hasLaboratory 123 .

ns2:John a ns1:Operator ;
            foaf:name "John" ;
            foaf:age 32 ;
            ns3:hasLaboratory 345 .
"""


MAPPING_WILDCARD = [
    {
        "iri": "https://w3id.org/emmo/domain/characterisation-methodology/chameo#Operator",
        "suffix": "name",
        "source": "data[*]",
        "suffix_from_location": True,
        "custom_relations": [
            {
                "object_location": "name",
                "relation": "http://xmlns.com/foaf/0.1/name",
            },
            {
                "object_location": "age",
                "relation": "http://xmlns.com/foaf/0.1/age",
            },
            {
                "object_location": "lab_no",
                "relation": "https://w3id.org/steel/ProcessOntology/hasLaboratory",
            },
        ],
    }
]

MAPPING_INDEX = [
    {
        "iri": "https://w3id.org/emmo/domain/characterisation-methodology/chameo#Operator",
        "suffix": "data[0].name",
        "suffix_from_location": True,
        "custom_relations": [
            {
                "object_location": "data[0].name",
                "relation": "http://xmlns.com/foaf/0.1/name",
            },
            {
                "object_location": "data[0].age",
                "relation": "http://xmlns.com/foaf/0.1/age",
            },
            {
                "object_location": "data[0].lab_no",
                "relation": "https://w3id.org/steel/ProcessOntology/hasLaboratory",
            },
        ],
    },
    {
        "iri": "https://w3id.org/emmo/domain/characterisation-methodology/chameo#Operator",
        "suffix": "data[1].name",
        "suffix_from_location": True,
        "custom_relations": [
            {
                "object_location": "data[1].name",
                "relation": "http://xmlns.com/foaf/0.1/name",
            },
            {
                "object_location": "data[1].age",
                "relation": "http://xmlns.com/foaf/0.1/age",
            },
            {
                "object_location": "data[1].lab_no",
                "relation": "https://w3id.org/steel/ProcessOntology/hasLaboratory",
            },
        ],
    },
]

BASE_IRI = (
    "https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation"
)


@pytest.mark.parametrize("mapping", [MAPPING_WILDCARD, MAPPING_INDEX])
def test_pipeline_dict_custom_properties(mapping) -> None:
    from rdflib import Graph

    from data2rdf import Data2RDF, Parser

    pipeline = Data2RDF(
        raw_data=DATA,
        mapping=mapping,
        parser=Parser.json,
        config={
            "base_iri": BASE_IRI,
            "separator": "#",
            "prefix_name": "nanoindentation",
            "suppress_file_description": True,
        },
    )

    expected_graph = Graph()
    expected_graph.parse(data=EXPECTED)
    print(pipeline.graph.serialize())

    assert pipeline.graph.isomorphic(expected_graph)
