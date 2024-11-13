"""Test for explicit datatypes."""

import pytest

DATA = [
    {
        "Ontological concept ID": "TestingMachine",
        "Label": "Testing machine",
        "Description": "Some description",
        "Superclass": "http://example.org#Object",
        "Comment": None,
        "Source": 123,
        "Author's name": None,
        "Author's email": None,
    },
    {
        "Ontological concept ID": "hasTestingMachine",
        "Label": "has Testing machine",
        "Type": "owl:ObjectProperty",
        "Description": "Some description",
        "Comment": None,
        "Source": None,
        "Author's name": None,
        "Author's email": None,
    },
]


MAPPING = [
    {
        "key": "Label",
        "relation": "http://www.w3.org/2000/01/rdf-schema#label",
        "relation_type": "annotation_property",
    },
    {
        "key": "Description",
        "relation": "http://purl.org/dc/terms/description",
        "relation_type": "data_property",
    },
    {
        "key": "Superclass",
        "relation": "http://www.w3.org/2000/01/rdf-schema#subClassOf",
        "relation_type": "object_property",
    },
    {
        "key": "Comment",
        "relation": "http://www.w3.org/2000/01/rdf-schema#comment",
        "relation_type": "data_property",
    },
    {
        "key": "Source",
        "relation": "http://purl.org/dc/terms/source",
        "relation_type": "data_property",
        "datatype": "float",
    },
    {
        "key": "Author's name",
        "relation": "http://purl.org/dc/terms/contributor",
        "relation_type": "data_property",
    },
    {
        "key": "Author's email",
        "relation": "http://xmlns.com/foaf/0.1/mbox",
        "relation_type": "data_property",
    },
]

EXPECTED = """
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix foaf1: <http://xmlns.com/foaf/spec/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<https://w3id.org/dimat> a owl:Ontology ;
    dcterms:creator [ a foaf1:Person ;
            foaf1:name "Jane Doe" ] ;
    dcterms:title "Test Ontology" ;
    owl:versionInfo "1.0.0" .

<https://w3id.org/dimat/TestingMachine> a owl:Class ;
    rdfs:label "Testing machine"^^xsd:string ;
    dcterms:description "Some description"^^xsd:string ;
    dcterms:source "123.0"^^xsd:float ;
    rdfs:subClassOf <http://example.org#Object> .

<https://w3id.org/dimat/hasTestingMachine> a owl:ObjectProperty ;
    rdfs:label "has Testing machine"^^xsd:string ;
    dcterms:description "Some description"^^xsd:string ."""


def test_explicit_datatypes():
    from rdflib import Graph

    from data2rdf.warnings import MappingMissmatchWarning

    from data2rdf import (  # isort:skip
        Data2RDF,
        Parser,
    )

    with pytest.warns(
        MappingMissmatchWarning, match="Data for key"
    ) as warnings:
        pipeline = Data2RDF(
            mode="tbox",
            raw_data=DATA,
            mapping=MAPPING,
            parser=Parser.json,
            parser_args={
                "suffix_location": "Ontological concept ID",
                "rdfs_type_location": "Type",
                "ontology_title": "Test Ontology",
                "authors": ["Jane Doe"],
                "version_info": "1.0.0",
            },
            config={
                "base_iri": "https://w3id.org/dimat",
            },
        )

    missmatches = [
        warning
        for warning in warnings
        if warning.category == MappingMissmatchWarning
    ]
    assert len(missmatches) == 9

    expected_graph = Graph()
    expected_graph.parse(data=EXPECTED)

    assert pipeline.graph.isomorphic(expected_graph)
