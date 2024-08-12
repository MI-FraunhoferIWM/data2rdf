# TBox generation from a Python dictionary

## General understanding

data2rdf is able to run the pipeline in tbox mode. In tbox mode, data2rdf generates a class hierarchy of the provided data.

In the previous examples, we were only creating abox graphs. In order to create tbox graphs, we need to provide a different mapping scheme for describing the classes and their properties.

## The inputs

For this example, we will consider the following inputs:

* the json file holding the class specificaiton
* the mapping for describing the class generation
* the parser arguments telling the pipeline which is the column for the suffix of each class. Additionally, we also need to provide the names of the authors and the ontology title

### The raw data

Let us consider that we have a class definition like this:

```
[
  {
    "Author's name": "Jane Doe",
    "Comment": "This row is an example",
    "Description": "Quotient of change of stress and change of extension in the range of evaluation in the elastic regime.",
    "Measurement unit": "GPa",
    "Ontological concept ID": "ModulusOfElasticity",
    "Original name": "E",
    "Source": "DIN EN ISO 6892-1, 3.13"
  },
  {
    "Author's name": "John Doe",
    "Comment": "",
    "Description": "atio of the infinitesimal pressure increase to the resulting relative decrease of the volume",
    "Measurement unit": "MPa",
    "Ontological concept ID": "BulkModulus",
    "Original name": "B",
    "Source": "DIN EN ISO XXX"
  }
]
```

The example data for the mapping shown above consist of the following keys:

Note that the raw data above is a Python list of dictionaries. Each dictionary represents a class and contains several properties like the author's name, comment, description, measurement unit, original name, and source. Each of those attributes can be mapped to a object propery, datatype property, or annotation property.

```{note}
Note that we will need at least one key-value pair describing the suffix of the ontological class later on.
```

### The mapping


```
[
  {
    "key": "Original name",
    "relation": "http://www.w3.org/2000/01/rdf-schema#label",
    "relation_type": "annotation_property"
  },
  {
    "key": "Ontological concept ID",
    "relation": "http://www.w3.org/2004/02/skos/core#altlabel",
    "relation_type": "annotation_property"
  },
  {
    "key": "Description",
    "relation": "http://purl.org/dc/terms/description",
    "relation_type": "data_property"
  },
  {
    "key": "Source",
    "relation": "https://w3id.org/steel/ProcessOntology/hasLabelSource",
    "relation_type": "data_property"
  },
  {
    "key": "Measurement unit",
    "relation": "https://w3id.org/steel/ProcessOntology/hasTypicalUnitLabel",
    "relation_type": "data_property"
  },
  {
    "key": "Comment",
    "relation": "http://www.w3.org/2000/01/rdf-schema#comment",
    "relation_type": "data_property"
  },
  {
    "key": "Author's name",
    "relation": "http://purl.org/dc/terms/contributor",
    "relation_type": "data_property"
  }
]
```

This mapping describes how to map different attributes of a concept in the data file to an ontological class.

- The `"key"` is the attribute name in the data file.
- The `"relation"` is the IRI of the ontological property.
- The `"relation_type"` specifies the type of the relation. This can be either be a `"data_property"`, `"object_property"` or `"annotation_property"`. In case if the `relation_type` is `"object_property"`, the target of the relation (receivd from the column referenced with `key`) needs to be an IRI. This takes place, if one needs to set e.g. the superclass of the concept with `owl:isSubClassOf`.

For example, if the data file contains a concept with the attribute `"Description"`, this mapping will map this attribute to the IRI `"http://purl.org/dc/terms/description"` which is a property of the [DCMI Metadata Terms vocabulary](https://www.dublincore.org/specifications/dublin-core/dcmi-terms/).

### The parser arguments

In order to generate the TBox graph properties, we need to take the following parser arguments into account:

* `"suffix_location"`: The attribute name which is used for the suffix of the ontological class (required). In this case, it is `"Ontological concept ID"`, since we are considering to find it under this column in the raw data.
* `"ontology_title"`: The title of the ontology (required). In this case, we just name it `"Test Ontology"`.
* `"authors"`: A list of authors of the ontology (required). In this case, we just name it `"Jane Doe"`.


```
parser_args={
    "suffix_location": "Ontological concept ID",
    "ontology_title": "Test Ontology",
    "authors": ["Jane Doe"],
}
```

## Running the pipeline

Please apply the mapping, addtional triples and the parser arguments to the pipeline configuration and run the pipeline in the following manner:

```
from data2rdf import Data2RDF, Parser

data = [
  {
    "Author's name": "Jane Doe",
    "Comment": "This row is an example",
    "Description": "Quotient of change of stress and change of extension in the range of evaluation in the elastic regime.",
    "Measurement unit": "GPa",
    "Ontological concept ID": "ModulusOfElasticity",
    "Original name": "E",
    "Source": "DIN EN ISO 6892-1, 3.13"
  },
  {
    "Author's name": "John Doe",
    "Comment": "",
    "Description": "atio of the infinitesimal pressure increase to the resulting relative decrease of the volume",
    "Measurement unit": "MPa",
    "Ontological concept ID": "BulkModulus",
    "Original name": "B",
    "Source": "DIN EN ISO XXX"
  }
]

mapping = [  {
    "key": "Original name",
    "relation": "http://www.w3.org/2000/01/rdf-schema#label",
    "relation_type": "annotation_property"
  },
  {
    "key": "Ontological concept ID",
    "relation": "http://www.w3.org/2004/02/skos/core#altlabel",
    "relation_type": "annotation_property"
  },
  {
    "key": "Description",
    "relation": "http://purl.org/dc/terms/description",
    "relation_type": "data_property"
  },
  {
    "key": "Source",
    "relation": "https://w3id.org/steel/ProcessOntology/hasLabelSource",
    "relation_type": "data_property"
  },
  {
    "key": "Measurement unit",
    "relation": "https://w3id.org/steel/ProcessOntology/hasTypicalUnitLabel",
    "relation_type": "data_property"
  },
  {
    "key": "Comment",
    "relation": "http://www.w3.org/2000/01/rdf-schema#comment",
    "relation_type": "data_property"
  },
  {
    "key": "Author's name",
    "relation": "http://purl.org/dc/terms/contributor",
    "relation_type": "data_property"
  }
]

parser_args={
    "suffix_location": "Ontological concept ID",
    "ontology_title": "Test Ontology",
    "authors": ["Jane Doe"],
}

data2rdf = Data2RDF(
    mode="tbox",
    raw_data = data,
    mapping = mapping,
    parser = Parser.json,
    parser_args = parser_args,
    config={
        "base_iri": "https://w3id.org/my_project",
    }
)
```

Please note that we are running the pipeline in the `"tbox"` mode this time.

## The output

When the pipeline run is succeded, you see the following output by running `print(pipeline.graph.serialize())`:

```
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix foaf1: <http://xmlns.com/foaf/spec/> .
@prefix ns1: <https://w3id.org/steel/ProcessOntology/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<https://w3id.org/dimat> a owl:Ontology ;
    dcterms:creator [ a foaf1:Person ;
            foaf1:name "Jane Doe" ] ;
    dcterms:title "Test Ontology" ;
    owl:versionInfo "1.0.0" .

<https://w3id.org/dimat/BulkModulus> a owl:Class ;
    rdfs:label "B"^^xsd:string ;
    dcterms:contributor "John Doe"^^xsd:string ;
    dcterms:description "atio of the infinitesimal pressure increase to the resulting relative decrease of the volume"^^xsd:string ;
    rdfs:comment ""^^xsd:string ;
    skos:altlabel "BulkModulus"^^xsd:string ;
    ns1:hasLabelSource "DIN EN ISO XXX"^^xsd:string ;
    ns1:hasTypicalUnitLabel "MPa "^^xsd:string .

<https://w3id.org/dimat/ModulusOfElasticity> a owl:Class ;
    rdfs:label "E"^^xsd:string ;
    dcterms:contributor "Jane Doe"^^xsd:string ;
    dcterms:description "Quotient of change of stress and change of extension in the range of evaluation in the elastic regime."^^xsd:string ;
    rdfs:comment "This row is an example"^^xsd:string ;
    skos:altlabel "ModulusOfElasticity"^^xsd:string ;
    ns1:hasLabelSource "DIN EN ISO 6892-1, 3.13"^^xsd:string ;
    ns1:hasTypicalUnitLabel "GPa"^^xsd:string .
```

In this case, there will be **no** `general_metadata`, `plain_metadata`, `time_series` or `time_series_metadata` attributes, since those outputs do not apply in the for the tbox mode of the pipeline.
