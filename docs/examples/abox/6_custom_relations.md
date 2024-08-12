# ABox generation for a graph with custom relations

## General understanding

In this very small example, we would like to generate a graph without quantitative data, but some other alpha-numeric properties, like names or labels. Additionally, we would like to set a custom relation like an annotation property or datatype property between the node of the individual and the data which we parse.

## The inputs

For this example, we will consider the following inputs:

* a json or Python dictionary to be parsed
* the mapping for describing the data in RDF
* additional triples for connecting the individuals produced by the pipeline.
* some additional configuration arguments for setting the base IRI, the separator between the prefix and the suffix, as well as boolean value that we do not need to have the semantic description of the data in the output.

### The raw data

For this example, we will consider the following input data:

```{json}
{
    "data": {
      "name": "Jane Doe",
      "measurement": "Continuous Stiffness Measurement"
    }
}
```

As you may have noticed, this json here simply features the name of a person and the name of a measurement.

### The mapping

For this minimal example, we only need a very short mapping:

´´´{json}
[
  {
    "value_location": "data.name",
    "value_relation": "http://xmlns.com/foaf/0.1/name",
    "iri": "https://w3id.org/emmo/domain/characterisation-methodology/chameo#Operator",
    "suffix": "Operator1"
  },
  {
    "value_location": "data.measurement",
    "iri": "https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#EMMO_5ca6e1c1-93e9-5e1a-881b-2c2bd38074b1 ",
    "suffix": "CSM1"
  }
]
´´´

You may notice here, that we are setting explicitly the `value_relation` for the first mapping to `foaf:name` and `suffix` for both mappings to `Operator1` and `CSM1`.

### Additional triples

Since we want to connect the persons in the graph with its measurement, we need to add some additional triples:

```{turtle}
@prefix : <http://abox-namespace-placeholder.org/> .
@prefix chameo: <https://w3id.org/emmo/domain/characterisation-methodology/chameo#> .

:CSM1 chameo:hasOperator :Operator1 .
```

Is is important to note here that we are using the suffixes `CSM1` and `Operator1` for the individuals of the operator and the measurement. Both of these suffixes need to match with the ones from the mapping above.

### The configuration arguments

In order to exclude the semantic description of the data file itself in the generated RDF graph, we need to set the `suppress_file_description` to `True`.

Optionally, we can also set the base IRI of the graph, its separator, as well as the prefix of the IRI in the header of the produced RDF:

```{json}
config = {
        "base_iri": "https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation",
        "separator": "#",
        "prefix_name": "nanoindentation",
        "suppress_file_description": True
}
```

## Running the pipeline

Please apply the mapping, addtional triples and the parser arguments to the pipeline configuration and run the pipeline in the following manner:

```{python}
from data2rdf import Data2RDF, Parser

data = {
    "data": {
      "name": "Jane Doe",
      "measurement": "Continuous Stiffness Measurement"
    }
}

mapping = [
  {
    "value_location": "data.name",
    "value_relation": "http://xmlns.com/foaf/0.1/name",
    "iri": "https://w3id.org/emmo/domain/characterisation-methodology/chameo#Operator",
    "suffix": "Operator1"
  },
  {
    "value_location": "data.measurement",
    "iri": "https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#EMMO_5ca6e1c1-93e9-5e1a-881b-2c2bd38074b1 ",
    "suffix": "CSM1"
  }
]

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
    config = config
)

```

## The output


When the pipeline run is succeded, you see the following output by running `print(pipeline.graph.serialize())`:

<blockQuote>
<Details>
<summary><b>Click here to expand</b></summary>
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix ns1: <https://w3id.org/emmo/domain/characterisation-methodology/chameo#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

<https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#CSM1> rdfs:label "Continuous Stiffness Measurement" ;
    ns1:hasOperator <https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#Operator1> .

<https://w3id.org/emmo/domain/domain-nanoindentation/nanoindentation#Operator1> a ns1:Operator ;
    foaf:name "G. Konstantopoulos" .

</Details>
</blockQuote>

Again, you will be able to investigate the `general_metadata` and `plain_metadata` in the same way as stated in the [first example](1_csv). But this does take place for the `time_series_metadata` and `time_series` attributes, since we do not include any time series in this example here.
