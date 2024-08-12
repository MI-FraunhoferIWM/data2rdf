# JSON file or Python-dict with metadata and time series

```{note}
This example is building up on the very first one about the [CSV file with metadata and time series](1_csv.md).
Please start from this chapter in order to fully understand the content of this example.
```

## General understanding

Typically, data can also be provided in the serialization of a json file, which ulimately can be parsed in to a dict object in Python.

In this section, we would like to showcase how to write a mapping for a json file with metadata and time series. The content of the json can be nested into an arbitrary depth.

## The inputs

In this example we will need only two inputs:

* the json file produced by the tensile test machine
* the mapping for describing the data in RDF

We generally do not need parser arguments at this point, since we are using the `json` parser. However, setting the `encoding` in the `config`-argument in the pipeline might be needed in case of any special characaters in the json file. Please for refer to the [Additional configuration](../../config.md) for more details.

### The raw data

We are considering the following dummy data as json input:

```
raw_data = {
  "data": {
    "Breitenänderung": {
      "unit": "mm",
      "value": 1.0
    },
    "Dehnung": [
      1.0,
      2.0,
      3.0
    ],
    "Standardkraft": {
      "array": [
        2.0,
        3.0,
        4.0
      ],
      "unit": "kN"
    }
  },
  "details": {
    "Bemerkungen": "foobar"
  }
}
```

As you may notice, concepts like `Breitenänderung` and `Dehnung` both are time series with slighly different key-patters: `Standardkraft` is a dictionary/object with an additional subelement called `array` for the values and `unit` for the unit, whereas the `Dehnung` key directly has a list of values and no reference for the unit.

### The mapping

A valid mapping for the json defined above may look like this:

```
[
  {
    "iri": "https://w3id.org/steel/ProcessOntology/Remark",
    "key": "Bemerkungen",
    "value_location": "details.Bemerkungen"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/WidthChange",
    "key": "Breitenaenderung",
    "unit": "data.Breitenaenderung.unit",
    "value_location": "data.Breitenaenderung.value"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/PercentageElongation",
    "key": "Dehnung",
    "unit": "%",
    "value_location": "data.Dehnung"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/Force",
    "key": "Standardkraft",
    "unit_location": "data.Standardkraft.unit",
    "value_location": "data.Standardkraft.array"
  }
]
```

Please note that we are using a querying-language called [`jsonpath`](https://support.smartbear.com/alertsite/docs/monitors/api/endpoint/jsonpath.html) in order to extract the data at its specific location.

For example, we can specify the `key` as `data.Standardkraft.unit` and the `value_location` as `data.Standardkraft.array`, since we have seen that the `Standardkraft` concept is a dictionary/object with an additional subelement called `array` for the values and `unit` for the unit:

```
...
  {
    "iri": "https://w3id.org/steel/ProcessOntology/Force",
    "key": "Standardkraft",
    "unit_location": "data.Standardkraft.unit",
    "value_location": "data.Standardkraft.array"
  }
...
```

In the case of the `Dehnung` concept, we can specify the `key` as `data.Dehnung` and manually map the `unit` to `%`, since we cannot extract the information from the data:

```
...
  {
    "iri": "https://w3id.org/steel/ProcessOntology/PercentageElongation",
    "key": "Dehnung",
    "unit": "%",
    "value_location": "data.Dehnung"
  }
...
```

## Running the pipeline


Please apply the mapping, addtional triples and the parser arguments to the pipeline configuration and run the pipeline in the following manner:

```
from data2rdf import Data2RDF, Parser

mapping = [
  {
    "iri": "https://w3id.org/steel/ProcessOntology/Remark",
    "key": "Bemerkungen",
    "value_location": "details.Bemerkungen"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/WidthChange",
    "key": "Breitenaenderung",
    "unit": "data.Breitenaenderung.unit",
    "value_location": "data.Breitenaenderung.value"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/PercentageElongation",
    "key": "Dehnung",
    "unit": "%",
    "value_location": "data.Dehnung"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/Force",
    "key": "Standardkraft",
    "unit_location": "data.Standardkraft.unit",
    "value_location": "data.Standardkraft.array"
  }
]


Data2RDF(
    raw_data = "path/to/file.json",
    mapping = mapping,
    parser = Parser.json,
)
```

Alternatively, you are also able to pass the data as a python dictionary directly:

```
from data2rdf import Data2RDF, Parser

data = raw_data = {
  "data": {
    "Breitenaenderung": {
      "unit": "mm",
      "value": 1.0
    },
    "Dehnung": [
      1.0,
      2.0,
      3.0
    ],
    "Standardkraft": {
      "array": [
        2.0,
        3.0,
        4.0
      ],
      "unit": "kN"
    }
  },
  "details": {
    "Bemerkungen": "foobar"
  }
}

mapping = [
  {
    "iri": "https://w3id.org/steel/ProcessOntology/Remark",
    "key": "Bemerkungen",
    "value_location": "details.Bemerkungen"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/WidthChange",
    "key": "Breitenaenderung",
    "unit": "data.Breitenaenderung.unit",
    "value_location": "data.Breitenaenderung.value"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/PercentageElongation",
    "key": "Dehnung",
    "unit": "%",
    "value_location": "data.Dehnung"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/Force",
    "key": "Standardkraft",
    "unit_location": "data.Standardkraft.unit",
    "value_location": "data.Standardkraft.array"
  }
]


Data2RDF(
    raw_data = "path/to/file.json",
    mapping = mapping,
    parser = Parser.json,
)
```

## The output

When the pipeline run is succeded, you see the following output by running `print(pipeline.graph.serialize())`:

<blockquote>
<Details>
<summary><b>Click here to expand</b></summary>

```
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix fileid: <https://www.example.org/> .
@prefix foaf1: <http://xmlns.com/foaf/spec/> .
@prefix ns1: <prov:> .
@prefix qudt: <http://qudt.org/schema/qudt/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

fileid:dataset a dcat:Dataset ;
    dcterms:hasPart fileid:Dictionary ;
    dcat:distribution [ a dcat:Distribution ;
            dcat:accessURL "https://www.example.org/download"^^xsd:anyURI ;
            dcat:mediaType "https://www.iana.org/assignments/media-types/application/json"^^xsd:anyURI ] .

fileid:Dictionary a ns1:Dictionary ;
    ns1:hadDictionaryMember [ a ns1:KeyEntityPair ;
            ns1:pairEntity [ a ns1:Entity ;
                    dcterms:hasPart fileid:Remark ] ;
            ns1:pairKey "Bemerkungen"^^xsd:string ],
        [ a ns1:KeyEntityPair ;
            ns1:pairEntity [ a ns1:Entity ;
                    qudt:quantity fileid:WidthChange ] ;
            ns1:pairKey "Breitenaenderung"^^xsd:string ],
        [ a ns1:KeyEntityPair ;
            ns1:pairEntity [ a ns1:Entity ;
                    qudt:quantity fileid:PercentageElongation ;
                    foaf1:page [ a foaf1:Document ;
                            dcterms:format "https://www.iana.org/assignments/media-types/application/json"^^xsd:anyURI ;
                            dcterms:identifier "https://www.example.org/column-0"^^xsd:anyURI ;
                            dcterms:type "http://purl.org/dc/terms/Dataset"^^xsd:anyURI ] ] ;
            ns1:pairKey "Dehnung"^^xsd:string ],
        [ a ns1:KeyEntityPair ;
            ns1:pairEntity [ a ns1:Entity ;
                    qudt:quantity fileid:Force ;
                    foaf1:page [ a foaf1:Document ;
                            dcterms:format "https://www.iana.org/assignments/media-types/application/json"^^xsd:anyURI ;
                            dcterms:identifier "https://www.example.org/column-1"^^xsd:anyURI ;
                            dcterms:type "http://purl.org/dc/terms/Dataset"^^xsd:anyURI ] ] ;
            ns1:pairKey "Standardkraft"^^xsd:string ] .

fileid:Force a <https://w3id.org/steel/ProcessOntology/Force> ;
    qudt:hasUnit "http://qudt.org/vocab/unit/KiloN"^^xsd:anyURI .

fileid:PercentageElongation a <https://w3id.org/steel/ProcessOntology/PercentageElongation> ;
    qudt:hasUnit "http://qudt.org/vocab/unit/PERCENT"^^xsd:anyURI .

fileid:Remark a <https://w3id.org/steel/ProcessOntology/Remark> ;
    rdfs:label "foobar" .

fileid:WidthChange a <https://w3id.org/steel/ProcessOntology/WidthChange> ;
    qudt:hasUnit "http://qudt.org/vocab/unit/MilliM"^^xsd:anyURI ;
    qudt:value "1.0"^^xsd:float .
```

</Details>
</blockQuote>

Again, you will be able to investigate the `general_metadata`, `plain_metadata`, `time_series_metadata` and `time_series` attributes in the same way as stated in the [first example](1_csv).
