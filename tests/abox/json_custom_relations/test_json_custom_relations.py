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
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ns2:Jane a ns1:Operator ;
            foaf:name "Jane"^^xsd:string ;
            foaf:age "28"^^xsd:integer ;
            ns3:hasLaboratory "123"^^xsd:integer .

ns2:John a ns1:Operator ;
            foaf:name "John"^^xsd:string ;
            foaf:age "32"^^xsd:integer ;
            ns3:hasLaboratory "345"^^xsd:integer .
"""

EXPECTED_DATATYPE = """
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix ns1: <https://w3id.org/emmo/domain/characterisation-methodology/chameo#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix ns2: <https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#> .
@prefix ns3: <https://w3id.org/steel/ProcessOntology/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ns2:Jane a ns1:Operator ;
            foaf:name "Jane"^^xsd:string ;
            foaf:age "28"^^xsd:string ;
            ns3:hasLaboratory "123"^^xsd:string .

ns2:John a ns1:Operator ;
            foaf:name "John"^^xsd:string ;
            foaf:age "32"^^xsd:string ;
            ns3:hasLaboratory "345"^^xsd:string .
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


MAPPING_WILDCARD_DATATYPE = [
    {
        "iri": "https://w3id.org/emmo/domain/characterisation-methodology/chameo#Operator",
        "suffix": "name",
        "source": "data[*]",
        "suffix_from_location": True,
        "custom_relations": [
            {
                "object_location": "name",
                "relation": "http://xmlns.com/foaf/0.1/name",
                "object_data_type": "string",
            },
            {
                "object_location": "age",
                "relation": "http://xmlns.com/foaf/0.1/age",
                "object_data_type": "string",
            },
            {
                "object_location": "lab_no",
                "relation": "https://w3id.org/steel/ProcessOntology/hasLaboratory",
                "object_data_type": "string",
            },
        ],
    }
]

MAPPING_INDEX_DATATYPE = [
    {
        "iri": "https://w3id.org/emmo/domain/characterisation-methodology/chameo#Operator",
        "suffix": "data[0].name",
        "suffix_from_location": True,
        "custom_relations": [
            {
                "object_location": "data[0].name",
                "relation": "http://xmlns.com/foaf/0.1/name",
                "object_data_type": "string",
            },
            {
                "object_location": "data[0].age",
                "relation": "http://xmlns.com/foaf/0.1/age",
                "object_data_type": "string",
            },
            {
                "object_location": "data[0].lab_no",
                "relation": "https://w3id.org/steel/ProcessOntology/hasLaboratory",
                "object_data_type": "string",
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
                "object_data_type": "string",
            },
            {
                "object_location": "data[1].age",
                "relation": "http://xmlns.com/foaf/0.1/age",
                "object_data_type": "string",
            },
            {
                "object_location": "data[1].lab_no",
                "relation": "https://w3id.org/steel/ProcessOntology/hasLaboratory",
                "object_data_type": "string",
            },
        ],
    },
]

BASE_IRI = (
    "https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation"
)

ADDITIONAL_TRIPLES = """
@prefix : <http://abox-namespace-placeholder.org/> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .

:John foaf:knows :Jane .
"""

EXPECTED_ADDITIONAL_TRIPLES = """
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix ns1: <https://w3id.org/emmo/domain/characterisation-methodology/chameo#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix ns2: <https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#> .
@prefix ns3: <https://w3id.org/steel/ProcessOntology/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ns2:Jane a ns1:Operator ;
            foaf:name "Jane"^^xsd:string ;
            foaf:age "28"^^xsd:integer ;
            ns3:hasLaboratory "123"^^xsd:integer .


ns2:John a ns1:Operator ;
            foaf:name "John"^^xsd:string ;
            foaf:age "32"^^xsd:integer ;
            ns3:hasLaboratory "345"^^xsd:integer ;
            foaf:knows ns2:Jane .
"""


@pytest.mark.parametrize("mapping", [MAPPING_WILDCARD, MAPPING_INDEX])
def test_pipeline_json_custom_relations(mapping) -> None:
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

    assert pipeline.graph.isomorphic(expected_graph)


@pytest.mark.parametrize(
    "mapping", [MAPPING_WILDCARD_DATATYPE, MAPPING_INDEX_DATATYPE]
)
def test_pipeline_json_custom_relations_datatype(mapping) -> None:
    """Test with custom relations and datatypes"""

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
    expected_graph.parse(data=EXPECTED_DATATYPE)

    assert pipeline.graph.isomorphic(expected_graph)


def test_pipeline_json_custom_relations_additional_triples() -> None:
    from rdflib import Graph

    from data2rdf import Data2RDF, Parser

    pipeline = Data2RDF(
        raw_data=DATA,
        mapping=MAPPING_WILDCARD,
        parser=Parser.json,
        config={
            "base_iri": BASE_IRI,
            "separator": "#",
            "prefix_name": "nanoindentation",
            "suppress_file_description": True,
        },
        additional_triples=ADDITIONAL_TRIPLES,
    )
    expected_graph = Graph()
    expected_graph.parse(data=EXPECTED_ADDITIONAL_TRIPLES)

    assert pipeline.graph.isomorphic(expected_graph)
