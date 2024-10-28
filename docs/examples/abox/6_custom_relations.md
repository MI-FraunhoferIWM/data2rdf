# Graph with custom relations

```{note}
Please follow [this link here](https://github.com/MI-FraunhoferIWM/data2rdf/blob/main/examples/6_graph_custom_relations.ipynb) in order to access the related jupyter notebook.
```

## General understanding

In this very small example, we would like to generate a graph with custom relations, e.g. labels and other arbitrary properties. However, we are going to show how to use wildcards in order to apply the mapping to an arbitrary number of individuals.

## The inputs

For this example, we will consider the following inputs:

* a json or Python dictionary to be parsed
* the mapping for describing the data in RDF
* additional triples for connecting the individuals produced by the pipeline.
* some additional configuration arguments for setting the base IRI, the separator between the prefix and the suffix, as well as boolean value that we do not need to have the semantic description of the data in the output.

### The raw data

For this example, we will consider the following input data:

```
{
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
```

As you may have noticed, this json here simply features the name of a person and the name of a measurement.

### The mapping

For this minimal example, we only need a very short mapping:

```
[
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
                "object_data_type": "string",
            },
        ],
    }
]
```

You may notice here, that we are not using the `value_location` here but use a field called `custom_relations` instead. The `custom_relations` field contains a list of predicates and objects that we need to add to the graph. Here again, the `object_location` can be a jsonpath or the cell number of a spreadsheet which is pointing to a value in the respective file. The `relation` must be an IRI which is used in order to point towards this object resolved from the `object_location`.


We can also set the `object_data_type` if we want to set the datatype of the object.
Important to note here is that this datatype must be an existing [xsd](https://www.w3.org/TR/xmlschema-2/)-datatype.

Note, that we are using a wildcard with `data[*]` in order to apply the mapping to an arbitrary number of individuals in the list under the key `data`. This wild card is going to be set in the `source` field of the mapping. By looking into the `suffix` field, we can see that the suffix of the individual is going to be the name of the person, which is stored under the key `name`.
We are setting `suffix_from_location` to `True` in order to use the location of the individual as suffix. Otherwise simply the provided string with the value `"name"` will be used as suffix.

Once the `source` field is set with the according wildcard, we are assuming that the jsonpath specified there returns a list (or an iterable) of objects (here in our data a list of dictionaries with the keys `name`, `age` and `lab_no`). The `suffix` and `object_location` fields will then be used as a relative path in order to resolve the values from this list of objects. If the `source` is not set, the `object_location` and `suffix` will be treated as absolute paths.


```{warning}
Once you use the `custom_relations` field, the `value_location`, `time_series_start`, and `unit_location` fields will be ignored.
```

### Additional triples

Since we want to connect the persons in the graph with its measurement, we need to add some additional triples:

```
@prefix : <http://abox-namespace-placeholder.org/> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .

:John foaf:knows :Jane .
```

Is is important to note here that we are using the suffixes `John` and `Jane` for the individuals which are going to be parsed from the `name` key of the dictionary.

### The configuration arguments

In order to exclude the semantic description of the data file itself in the generated RDF graph, we need to set the `suppress_file_description` to `True`.

Optionally, we can also set the base IRI of the graph, its separator, as well as the prefix of the IRI in the header of the produced RDF:

```
config = {
        "base_iri": "https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation",
        "separator": "#",
        "prefix_name": "nanoindentation",
        "suppress_file_description": True
}
```

## Running the pipeline

Please apply the mapping, addtional triples and the parser arguments to the pipeline configuration and run the pipeline in the following manner:

```
from data2rdf import Data2RDF, Parser

data = {
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

mapping = [
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

additional_triples = """
@prefix : <http://abox-namespace-placeholder.org/> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .

:John foaf:knows :Jane .
"""


config = {
    "base_iri": "https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation",
    "separator": "#",
    "prefix_name": "nanoindentation",
    "suppress_file_description": True
}

data2rdf = Data2RDF(
    raw_data = data,
    mapping = mapping,
    parser = Parser.json,
    config = config,
    additional_triples = additional_triples
)

```

## The output


When the pipeline run is succeded, you see the following output by running `print(pipeline.graph.serialize())`:

```
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix ns1: <https://w3id.org/steel/ProcessOntology/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix chameo: <https://w3id.org/emmo/domain/characterisation-methodology/chameo#> .
@prefix nanoindentation: <https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#> .

nanoindentation:John a chameo:Operator ;
    foaf:age 32 ;
    foaf:knows nanoindentation:Jane ;
    foaf:name "John"^^xsd:string ;
    ns1:hasLaboratory 345 .

nanoindentation:Jane a chameo:Operator ;
    foaf:age 28 ;
    foaf:name "Jane"^^xsd:string ;
    ns1:hasLaboratory 123 .

```

Again, you will be able to investigate the `general_metadata` and `plain_metadata` in the same way as stated in the [first example](1_csv). But this does take place for the `time_series_metadata` and `time_series` attributes, since we do not include any time series in this example here.
