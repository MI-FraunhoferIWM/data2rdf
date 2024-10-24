"""Test custom relations for JSON parser"""
import os

EXPECTED = """
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix ns1: <https://w3id.org/emmo/domain/characterisation-methodology/chameo#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix ns2: <https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#> .
@prefix ns3: <https://w3id.org/steel/ProcessOntology/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ns2:Jane a ns1:Operator ;
            foaf:name "Jane"^^xsd:string ;
            foaf:age 28 ;
            ns3:hasLaboratory 123 .

ns2:John a ns1:Operator ;
            foaf:name "John"^^xsd:string ;
            foaf:age 32 ;
            ns3:hasLaboratory 456 .
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
            ns3:hasLaboratory "456"^^xsd:string .
"""


MAPPING_INDEX = [
    {
        "iri": "https://w3id.org/emmo/domain/characterisation-methodology/chameo#Operator",
        "suffix": "A2",
        "suffix_from_location": True,
        "worksheet": "tab1",
        "custom_relations": [
            {
                "object_location": "A2",
                "relation": "http://xmlns.com/foaf/0.1/name",
            },
            {
                "object_location": "B2",
                "relation": "http://xmlns.com/foaf/0.1/age",
            },
            {
                "object_location": "C2",
                "relation": "https://w3id.org/steel/ProcessOntology/hasLaboratory",
            },
        ],
    },
    {
        "iri": "https://w3id.org/emmo/domain/characterisation-methodology/chameo#Operator",
        "suffix": "A3",
        "suffix_from_location": True,
        "worksheet": "tab1",
        "custom_relations": [
            {
                "object_location": "A3",
                "relation": "http://xmlns.com/foaf/0.1/name",
            },
            {
                "object_location": "B3",
                "relation": "http://xmlns.com/foaf/0.1/age",
            },
            {
                "object_location": "C3",
                "relation": "https://w3id.org/steel/ProcessOntology/hasLaboratory",
            },
        ],
    },
]


MAPPING_INDEX_DATATYPE = [
    {
        "iri": "https://w3id.org/emmo/domain/characterisation-methodology/chameo#Operator",
        "suffix": "A2",
        "suffix_from_location": True,
        "worksheet": "tab1",
        "custom_relations": [
            {
                "object_location": "A2",
                "relation": "http://xmlns.com/foaf/0.1/name",
                "object_data_type": "string",
            },
            {
                "object_location": "B2",
                "relation": "http://xmlns.com/foaf/0.1/age",
                "object_data_type": "string",
            },
            {
                "object_location": "C2",
                "relation": "https://w3id.org/steel/ProcessOntology/hasLaboratory",
                "object_data_type": "string",
            },
        ],
    },
    {
        "iri": "https://w3id.org/emmo/domain/characterisation-methodology/chameo#Operator",
        "suffix": "A3",
        "suffix_from_location": True,
        "worksheet": "tab1",
        "custom_relations": [
            {
                "object_location": "A3",
                "relation": "http://xmlns.com/foaf/0.1/name",
                "object_data_type": "string",
            },
            {
                "object_location": "B3",
                "relation": "http://xmlns.com/foaf/0.1/age",
                "object_data_type": "string",
            },
            {
                "object_location": "C3",
                "relation": "https://w3id.org/steel/ProcessOntology/hasLaboratory",
                "object_data_type": "string",
            },
        ],
    },
]

BASE_IRI = (
    "https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation"
)

test_folder = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(test_folder, "data.xlsx")


def test_pipeline_xlsx_custom_relations() -> None:
    from rdflib import Graph

    from data2rdf import Data2RDF, Parser

    pipeline = Data2RDF(
        raw_data=DATA,
        mapping=MAPPING_INDEX,
        parser=Parser.excel,
        parser_args={"dropna": True, "unit_from_macro": True},
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


def test_pipeline_xlsx_custom_relations_datatype() -> None:
    """Test with custom relations and datatypes"""

    from rdflib import Graph

    from data2rdf import Data2RDF, Parser

    pipeline = Data2RDF(
        raw_data=DATA,
        mapping=MAPPING_INDEX_DATATYPE,
        parser=Parser.excel,
        parser_args={"dropna": True, "unit_from_macro": True},
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
