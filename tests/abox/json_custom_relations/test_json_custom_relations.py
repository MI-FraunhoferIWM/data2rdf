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


DATA_NULL = {
    "data": [
        {
            "name": "",
            "age": 28,
            "lab_no": 0,
        },
        {
            "name": "John",
            "age": 32,
            "lab_no": 345,
        },
    ]
}

DATA_SUBGRAPHS = {
    "data": [
        {
            "name": "specimen_1",
            "youngs_modulus": 100,
            "material": "material_1",
            "kitem": "kitem_1",
            "tensile_strength": [100, 200],
        },
        {
            "name": "specimen_2",
            "youngs_modulus": "200-300",
            "material": "material_2",
            "kitem": ["kitem_2", "kitem_3"],
            "tensile_strength": [200, 300],
        },
        {
            "name": "specimen_3",
            "youngs_modulus": [300, 400],
            "material": "material_3",
            "kitem": "kitem_4",
            "tensile_strength": [300, 400],
        },
    ]
}

MAPPING_SUBGRAPHS = [
    {
        "iri": "https://w3id.org/steel/ProcessOntology/Specimen",
        "suffix": "name",
        "source": "data[*]",
        "suffix_from_location": True,
        "custom_relations": [
            {
                "object_location": "youngs_modulus",
                "relation": "https://w3id.org/steel/ProcessOntology/hasYoungsModulus",
                "object_type": {
                    "iri": "https://w3id.org/steel/ProcessOntology/YoungsModulus",
                    "unit": "GPa",
                },
            },
            {
                "object_location": "material",
                "relation": "https://w3id.org/steel/ProcessOntology/hasMaterial",
                "object_type": {
                    "iri": "https://w3id.org/steel/ProcessOntology/Material",
                    "value_relation": "https://w3id.org/steel/ProcessOntology/hasIdentifier",
                },
            },
            {
                "object_location": "name",
                "relation": "https://w3id.org/steel/ProcessOntology/hasIdentifier",
            },
            {
                "object_location": "kitem",
                "relation": "https://w3id.org/steel/ProcessOntology/hasKitem",
                "object_type": {
                    "iri": "https://w3id.org/steel/ProcessOntology/Kitem/",
                    "concatenate": True,
                },
            },
            {
                "object_location": "tensile_strength[0]",
                "relation": "https://w3id.org/steel/ProcessOntology/hasMinimumTensileStrength",
                "object_type": {
                    "iri": "https://w3id.org/steel/ProcessOntology/TensileStrength",
                    "unit": "MPa",
                    "suffix": "tensile_strength_min",
                },
            },
            {
                "object_location": "tensile_strength[1]",
                "relation": "https://w3id.org/steel/ProcessOntology/hasMaximumTensileStrength",
                "object_type": {
                    "iri": "https://w3id.org/steel/ProcessOntology/TensileStrength",
                    "unit": "MPa",
                    "suffix": "tensile_strength_max",
                },
            },
        ],
    }
]

EXPECTED_SUBGRAPHS = """
@prefix ns1: <https://w3id.org/steel/ProcessOntology/> .
@prefix ns2: <http://qudt.org/schema/qudt/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#specimen_1> a ns1:Specimen ;
    ns1:hasIdentifier "specimen_1"^^xsd:string ;
    ns1:hasMaterial <https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#Material_specimen_1> ;
    ns1:hasYoungsModulus <https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#YoungsModulus_specimen_1> ;
    ns1:hasMaximumTensileStrength <https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#tensile_strength_max_specimen_1> ;
    ns1:hasMinimumTensileStrength <https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#tensile_strength_min_specimen_1> ;
    ns1:hasKitem <https://w3id.org/steel/ProcessOntology/Kitem/kitem_1> .

<https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#specimen_2> a ns1:Specimen ;
    ns1:hasIdentifier "specimen_2"^^xsd:string ;
    ns1:hasMaterial <https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#Material_specimen_2> ;
    ns1:hasYoungsModulus <https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#YoungsModulus_specimen_2> ;
    ns1:hasMaximumTensileStrength <https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#tensile_strength_max_specimen_2> ;
    ns1:hasMinimumTensileStrength <https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#tensile_strength_min_specimen_2> ;
    ns1:hasKitem <https://w3id.org/steel/ProcessOntology/Kitem/kitem_2>, <https://w3id.org/steel/ProcessOntology/Kitem/kitem_3> .

<https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#specimen_3> a ns1:Specimen ;
    ns1:hasIdentifier "specimen_3"^^xsd:string ;
    ns1:hasMaterial <https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#Material_specimen_3> ;
    ns1:hasYoungsModulus <https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#YoungsModulus_specimen_3> ;
    ns1:hasMaximumTensileStrength <https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#tensile_strength_max_specimen_3> ;
    ns1:hasMinimumTensileStrength <https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#tensile_strength_min_specimen_3> ;
    ns1:hasKitem <https://w3id.org/steel/ProcessOntology/Kitem/kitem_4> .


<https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#Material_specimen_1> a ns1:Material ;
    ns1:hasIdentifier "material_1"^^xsd:string .

<https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#Material_specimen_2> a ns1:Material ;
    ns1:hasIdentifier "material_2"^^xsd:string .

<https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#Material_specimen_3> a ns1:Material ;
    ns1:hasIdentifier "material_3"^^xsd:string .

<https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#YoungsModulus_specimen_1> a ns1:YoungsModulus ;
    ns2:hasUnit "http://qudt.org/vocab/unit/GigaPA"^^xsd:anyURI ;
    ns2:value 100 .

<https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#YoungsModulus_specimen_2> a ns1:YoungsModulus ;
    ns2:hasUnit "http://qudt.org/vocab/unit/GigaPA"^^xsd:anyURI ;
    ns2:value "200-300"^^xsd:string .

<https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#YoungsModulus_specimen_3> a ns1:YoungsModulus ;
    ns2:hasUnit "http://qudt.org/vocab/unit/GigaPA"^^xsd:anyURI ;
    ns2:value 300, 400 .

<https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#tensile_strength_max_specimen_1> a ns1:TensileStrength ;
    ns2:hasUnit "http://qudt.org/vocab/unit/MegaPA"^^xsd:anyURI ;
    ns2:value 200 .

<https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#tensile_strength_max_specimen_2> a ns1:TensileStrength ;
    ns2:hasUnit "http://qudt.org/vocab/unit/MegaPA"^^xsd:anyURI ;
    ns2:value 300 .

<https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#tensile_strength_max_specimen_3> a ns1:TensileStrength ;
    ns2:hasUnit "http://qudt.org/vocab/unit/MegaPA"^^xsd:anyURI ;
    ns2:value 400 .

<https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#tensile_strength_min_specimen_1> a ns1:TensileStrength ;
    ns2:hasUnit "http://qudt.org/vocab/unit/MegaPA"^^xsd:anyURI ;
    ns2:value 100 .

<https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#tensile_strength_min_specimen_2> a ns1:TensileStrength ;
    ns2:hasUnit "http://qudt.org/vocab/unit/MegaPA"^^xsd:anyURI ;
    ns2:value 200 .

<https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#tensile_strength_min_specimen_3> a ns1:TensileStrength ;
    ns2:hasUnit "http://qudt.org/vocab/unit/MegaPA"^^xsd:anyURI ;
    ns2:value 300 .
"""

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


EXPECTED_NULL = """
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix ns1: <https://w3id.org/emmo/domain/characterisation-methodology/chameo#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix ns2: <https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#> .
@prefix ns3: <https://w3id.org/steel/ProcessOntology/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ns2:Operator a ns1:Operator ;
           foaf:age "28"^^xsd:integer ;
           ns3:hasLaboratory "0"^^xsd:integer .


ns2:John a ns1:Operator ;
            foaf:name "John"^^xsd:string ;
            foaf:age "32"^^xsd:integer ;
            ns3:hasLaboratory "345"^^xsd:integer .
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


def test_pipeline_json_custom_relations_additional_triples_null() -> None:
    from rdflib import Graph

    from data2rdf import Data2RDF, Parser
    from data2rdf.warnings import MappingMissmatchWarning

    with pytest.warns(UserWarning, match="Concept with for ") as warnings:
        pipeline = Data2RDF(
            raw_data=DATA_NULL,
            mapping=MAPPING_WILDCARD,
            parser=Parser.json,
            config={
                "base_iri": BASE_IRI,
                "separator": "#",
                "prefix_name": "nanoindentation",
                "suppress_file_description": True,
            },
        )

    missmatches = [
        warning
        for warning in warnings
        if warning.category == MappingMissmatchWarning
    ]
    assert len(missmatches) == 1

    expected_graph = Graph()
    expected_graph.parse(data=EXPECTED_NULL)

    assert pipeline.graph.isomorphic(expected_graph)


def test_pipeline_json_custom_relations_quantity_graph() -> None:
    from rdflib import Graph

    from data2rdf import Data2RDF, Parser
    from data2rdf.warnings import ParserWarning

    with pytest.warns(ParserWarning, match="Cannot") as warnings:
        pipeline = Data2RDF(
            raw_data=DATA_SUBGRAPHS,
            mapping=MAPPING_SUBGRAPHS,
            parser=Parser.json,
            config={
                "base_iri": BASE_IRI,
                "separator": "#",
                "suppress_file_description": True,
            },
        )

    warnings = [
        warning for warning in warnings if warning.category == ParserWarning
    ]
    assert len(warnings) == 1

    expected_graph = Graph()
    expected_graph.parse(data=EXPECTED_SUBGRAPHS)

    assert pipeline.graph.isomorphic(expected_graph)
