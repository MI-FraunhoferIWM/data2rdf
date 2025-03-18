"""Test abox with multiple IRIs"""

DATA = {
    "Identifier": "123",
    "Material": [
        "https://example.materials-data.space/knowledge/material/material1",
        "https://example.materials-data.space/knowledge/material/material2",
    ],
}


MAPPING = [
    {
        "iri": [
            "https://w3id.org/emmo#EMMO_ee0466e4_780d_4236_8281_ace7ad3fc5d2",
            "https://example.org/0034d610-959d-4dd0-97f0-f3b36eeea5c4",
        ],
        "suffix": "Identifier",
        "value_location": "Identifier",
        "value_relation": "https://w3id.org/emmo#EMMO_a592c856_4103_43cf_8635_1982a1e5d5de",
        "datatype": "integer",
    },
    {
        "iri": [
            "https://w3id.org/emmo#Material",
            "https://example.org/0034d610-959d-4dd0-97f0-f3b36eeea5c4",
        ],
        "suffix": "Material",
        "value_location": "Material",
        "value_relation": "http://www.w3.org/2000/01/rdf-schema#relatedTo",
        "value_relation_type": "object_property",
    },
]

EXPECTED = """
@prefix ns1: <https://w3id.org/emmo#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<https://example.materials-data.space/knowledge/testing-machine/Identifier> a <https://example.org/0034d610-959d-4dd0-97f0-f3b36eeea5c4>,
        ns1:EMMO_ee0466e4_780d_4236_8281_ace7ad3fc5d2 ;
    ns1:EMMO_a592c856_4103_43cf_8635_1982a1e5d5de 123 .

<https://example.materials-data.space/knowledge/testing-machine/Material> a <https://example.org/0034d610-959d-4dd0-97f0-f3b36eeea5c4>,
        ns1:Material ;
    rdfs:relatedTo <https://example.materials-data.space/knowledge/material/material1>,
        <https://example.materials-data.space/knowledge/material/material2> .

"""

DATA_CUMSTOM_RELATIONS = {
    "testing-machine": [
        {
            "Description": "Some description",
            "Identifier": "123",
            "Material": [
                "https://example.materials-data.space/knowledge/material/material1",
                "https://example.materials-data.space/knowledge/material/material2",
            ],
            "id": "0034d610-959d-4dd0-97f0-f3b36eeea5c4",
            "slug": "testing-machine1",
            "Name": "Testing machine1",
        }
    ]
}

MAPPING_CUSTOM_RELATIONS = [
    {
        "iri": [
            "https://w3id.org/emmo#EMMO_ee0466e4_780d_4236_8281_ace7ad3fc5d2",
            "https://example.org/0034d610-959d-4dd0-97f0-f3b36eeea5c4",
        ],
        "suffix": "slug",
        "source": "testing-machine[*]",
        "suffix_from_location": True,
        "custom_relations": [
            {
                "object_location": "Description",
                "relation": "http://www.w3.org/2000/01/rdf-schema#comment",
                "relation_type": "property",
            },
            {
                "object_location": "Identifier",
                "relation": "https://w3id.org/emmo#EMMO_a592c856_4103_43cf_8635_1982a1e5d5de",
                "relation_type": "data_property",
            },
            {
                "object_location": "Material",
                "relation": "http://www.w3.org/2000/01/rdf-schema#relatedTo",
                "relation_type": "object_property",
            },
            {
                "object_location": "Name",
                "relation": "http://www.w3.org/2000/01/rdf-schema#label",
                "relation_type": "annotation_property",
            },
        ],
    }
]

EXPECTED_CUSTOM_RELATIONS = """
@prefix ns1: <https://w3id.org/emmo#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix ex: <https://example.org/> .

<https://example.materials-data.space/knowledge/testing-machine/testing-machine1> a ns1:EMMO_ee0466e4_780d_4236_8281_ace7ad3fc5d2 , ex:0034d610-959d-4dd0-97f0-f3b36eeea5c4 ;
    rdfs:label "Testing machine1"^^xsd:string ;
    rdfs:comment "Some description"^^xsd:string ;
    rdfs:relatedTo <https://example.materials-data.space/knowledge/material/material1> ,
                   <https://example.materials-data.space/knowledge/material/material2> ;
    ns1:EMMO_a592c856_4103_43cf_8635_1982a1e5d5de 123 .
"""


DATA_SPECIAL_CHARS = {
    "testing-machine": [
        {
            "Description (foo)": "Some description",
            "Identifier 123": "123",
            "Material (öä§$%)": [
                "https://example.materials-data.space/knowledge/material/material1",
                "https://example.materials-data.space/knowledge/material/material2",
            ],
            "id": "0034d610-959d-4dd0-97f0-f3b36eeea5c4",
            "slug": "testing-machine1",
            "Name": "Testing machine1",
        }
    ]
}

MAPPING_SPECIAL_CHARS = [
    {
        "iri": [
            "https://w3id.org/emmo#EMMO_ee0466e4_780d_4236_8281_ace7ad3fc5d2",
            "https://example.org/0034d610-959d-4dd0-97f0-f3b36eeea5c4",
        ],
        "suffix": "slug",
        "source": "testing-machine[*]",
        "suffix_from_location": True,
        "custom_relations": [
            {
                "object_location": "Description (foo)",
                "relation": "http://www.w3.org/2000/01/rdf-schema#comment",
                "relation_type": "property",
            },
            {
                "object_location": "Identifier 123",
                "relation": "https://w3id.org/emmo#EMMO_a592c856_4103_43cf_8635_1982a1e5d5de",
                "relation_type": "data_property",
            },
            {
                "object_location": "Material (öä§$%)",
                "relation": "http://www.w3.org/2000/01/rdf-schema#relatedTo",
                "relation_type": "object_property",
            },
            {
                "object_location": "Name",
                "relation": "http://www.w3.org/2000/01/rdf-schema#label",
                "relation_type": "annotation_property",
            },
        ],
    }
]


def test_multiple_iris_custom_relations():
    from rdflib import Graph

    from data2rdf import Data2RDF, Parser

    pipeline = Data2RDF(
        raw_data=DATA_CUMSTOM_RELATIONS,
        mapping=MAPPING_CUSTOM_RELATIONS,
        parser=Parser.json,
        parser_args={"expand_array": True},
        config={
            "base_iri": "https://example.materials-data.space/knowledge/testing-machine/",
            "suppress_file_description": True,
        },
    )
    expected_graph = Graph()
    expected_graph.parse(data=EXPECTED_CUSTOM_RELATIONS)

    assert pipeline.graph.isomorphic(expected_graph)


def test_multiple_iris():
    from rdflib import Graph

    from data2rdf import Data2RDF, Parser

    pipeline = Data2RDF(
        raw_data=DATA,
        mapping=MAPPING,
        parser=Parser.json,
        parser_args={"expand_array": True},
        config={
            "base_iri": "https://example.materials-data.space/knowledge/testing-machine/",
            "suppress_file_description": True,
        },
    )
    expected_graph = Graph()
    expected_graph.parse(data=EXPECTED)

    assert pipeline.graph.isomorphic(expected_graph)


def test_special_chars():
    from rdflib import Graph

    from data2rdf import Data2RDF, Parser

    pipeline = Data2RDF(
        raw_data=DATA_SPECIAL_CHARS,
        mapping=MAPPING_SPECIAL_CHARS,
        parser=Parser.json,
        parser_args={"expand_array": True},
        config={
            "base_iri": "https://example.materials-data.space/knowledge/testing-machine/",
            "suppress_file_description": True,
        },
    )
    expected_graph = Graph()
    expected_graph.parse(data=EXPECTED_CUSTOM_RELATIONS)

    assert pipeline.graph.isomorphic(expected_graph)
