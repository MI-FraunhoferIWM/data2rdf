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


MAPPING_SUBGRAPHS = [
    {
        "iri": "https://w3id.org/steel/ProcessOntology/Specimen",
        "suffix": "A2",
        "worksheet": "tab1",
        "suffix_from_location": True,
        "custom_relations": [
            {
                "object_location": "B2",
                "relation": "https://w3id.org/steel/ProcessOntology/hasYoungsModulus",
                "object_type": {
                    "iri": "https://w3id.org/steel/ProcessOntology/YoungsModulus",
                    "unit": "GPa",
                },
            },
            {
                "object_location": "C2",
                "relation": "https://w3id.org/steel/ProcessOntology/hasMaterial",
                "object_type": {
                    "iri": "https://w3id.org/steel/ProcessOntology/Material",
                    "value_relation": "https://w3id.org/steel/ProcessOntology/hasIdentifier",
                },
            },
            {
                "object_location": "A2",
                "relation": "https://w3id.org/steel/ProcessOntology/hasIdentifier",
            },
        ],
    },
    {
        "iri": "https://w3id.org/steel/ProcessOntology/Specimen",
        "suffix": "A3",
        "worksheet": "tab1",
        "suffix_from_location": True,
        "custom_relations": [
            {
                "object_location": "B3",
                "relation": "https://w3id.org/steel/ProcessOntology/hasYoungsModulus",
                "object_type": {
                    "iri": "https://w3id.org/steel/ProcessOntology/YoungsModulus",
                    "unit": "GPa",
                },
            },
            {
                "object_location": "C3",
                "relation": "https://w3id.org/steel/ProcessOntology/hasMaterial",
                "object_type": {
                    "iri": "https://w3id.org/steel/ProcessOntology/Material",
                    "value_relation": "https://w3id.org/steel/ProcessOntology/hasIdentifier",
                },
            },
            {
                "object_location": "A3",
                "relation": "https://w3id.org/steel/ProcessOntology/hasIdentifier",
            },
        ],
    },
]

EXPECTED_SUBGRAPHS = """
@prefix ns1: <https://w3id.org/steel/ProcessOntology/> .
@prefix ns2: <http://qudt.org/schema/qudt/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#specimen_1> a ns1:Specimen ;
    ns1:hasIdentifier "specimen_1"^^xsd:string ;
    ns1:hasMaterial <https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#Material_specimen_1> ;
    ns1:hasYoungsModulus <https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#YoungsModulus_specimen_1> .

<https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#specimen_2> a ns1:Specimen ;
    ns1:hasIdentifier "specimen_2"^^xsd:string ;
    ns1:hasMaterial <https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#Material_specimen_2> ;
    ns1:hasYoungsModulus <https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#YoungsModulus_specimen_2> .

<https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#Material_specimen_1> a ns1:Material ;
    ns1:hasIdentifier "material_1"^^xsd:string .

<https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#Material_specimen_2> a ns1:Material ;
    ns1:hasIdentifier "material_2"^^xsd:string .

<https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#YoungsModulus_specimen_1> a ns1:YoungsModulus ;
    ns2:hasUnit "http://qudt.org/vocab/unit/GigaPA"^^xsd:anyURI ;
    ns2:value 100 .

<https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#YoungsModulus_specimen_2> a ns1:YoungsModulus ;
    ns2:hasUnit "http://qudt.org/vocab/unit/GigaPA"^^xsd:anyURI ;
    ns2:value 200 .

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
DATA2 = os.path.join(test_folder, "data2.xlsx")


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


def test_pipeline_xlsx_custom_relations_subgraphs() -> None:
    """Test with custom relations and datatypes"""

    from rdflib import Graph

    from data2rdf import Data2RDF, Parser

    pipeline = Data2RDF(
        raw_data=DATA2,
        mapping=MAPPING_SUBGRAPHS,
        parser=Parser.excel,
        parser_args={"dropna": True, "unit_from_macro": False},
        config={
            "base_iri": BASE_IRI,
            "separator": "#",
            "suppress_file_description": True,
        },
    )

    expected_graph = Graph()
    expected_graph.parse(data=EXPECTED_SUBGRAPHS)

    assert pipeline.graph.isomorphic(expected_graph)
