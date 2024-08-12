# CSV file without metadata

## General understanding

In this example, we are looking into dummy sensor data which is provided by a csv file. However, we do not have any metadata in this case, but directly start with the time series. Additionaly, each column in this time series is of the same ontological class, but was recorded by a different sensor.

## The inputs

For this example, we will consider the following inputs:

* the csv file produced by the sensors
* the mapping for describing the data in RDF
* the parser arguments telling the pipeline that we do not have any metadata in the file.

### The raw data

The csv file produced by the dummy sensors looks like this:

```{csv}
time,column_01,column_02,column_03
2,2,2,2
3,3,3,3
4,4,4,4
5,5,5,5
6,6,6,6
7,7,7,7
```

You may note that the first column is the time and the rest of the columns are of the same class. As already mentioned above, there is no metadata, but only time series in this case.

### The parser arguments

Since we are considering the csv parser again, we need to take the following parser arguments into account:

* `time_series_sep`: the separator for the time series. In this case, it is a  `,`.
* `metadata_length`: the length of the metadata in the csv file. In this case, it is 0, since we do not have any metadata.
* `time_series_header_length`: the length of the header of the time series in the csv file. In this case, it is 1, since the time series start at the second row.

The resulting Python dictionary for the parser arguments would look like this:

```
parser_args = {
    "time_series_sep": ",",
    "metadata_length": 0,
    "time_series_header_length": 1
}
```

### The mapping

The **schema** of the mapping itself is very similar to the one of the [very first example](1_csv.md), but for different ontological classes and different keys this time:

```{python}
[
  {
    "iri": "https://w3id.org/steel/ProcessOntology/Sensor",
    "key": "column_01",
    "suffix": "Sensor1"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/Sensor",
    "key": "column_02",
    "suffix": "Sensor2"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/Sensor",
    "key": "column_03",
    "suffix": "Sensor3"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/TestTime",
    "key": "time"
  }
]
```

As you may notice, each column which is mapped to a `https://w3id.org/steel/ProcessOntology/Sensor` is of the same class. This results into the need, that each of those mappings will need a unique suffix.


## Running the pipeline

Please apply the mapping, addtional triples and the parser arguments to the pipeline configuration and run the pipeline in the following manner:

```
from data2rdf import Data2RDF, Parser

data = """
time,column_01,column_02,column_03
2,2,2,2
3,3,3,3
4,4,4,4
5,5,5,5
6,6,6,6
7,7,7,7
"""

mapping = [
  {
    "iri": "https://w3id.org/steel/ProcessOntology/Sensor",
    "key": "column_01",
    "suffix": "Sensor1"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/Sensor",
    "key": "column_02",
    "suffix": "Sensor2"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/Sensor",
    "key": "column_03",
    "suffix": "Sensor3"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/TestTime",
    "key": "time"
  }
]

parser_args = {
    "time_series_sep": ",",
    "metadata_length": 0,
    "time_series_header_length": 1
}

data2rdf = Data2RDF(
    raw_data = data,
    mapping = mapping,
    parser = Parser.csv,
    parser_args = parser_args
)
```

## The output

When the pipeline run is succeded, you see the following output by running `print(pipeline.graph.serialize())`:

<blockQuote>
<Details>
<summary><b>Click here to expand</b></summary>

```
@prefix csvw: <http://www.w3.org/ns/csvw#> .
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix fileid: <https://www.example.org/> .
@prefix foaf1: <http://xmlns.com/foaf/spec/> .
@prefix qudt: <http://qudt.org/schema/qudt/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

fileid:dataset a dcat:Dataset ;
    dcterms:hasPart fileid:tableGroup ;
    dcat:distribution [ a dcat:Distribution ;
            dcat:accessURL "https://www.example.org/download"^^xsd:anyURI ;
            dcat:mediaType "http://www.iana.org/assignments/media-types/text/csv"^^xsd:anyURI ] .

fileid:Sensor1 a <https://w3id.org/steel/ProcessOntology/Sensor> .

fileid:Sensor2 a <https://w3id.org/steel/ProcessOntology/Sensor> .

fileid:Sensor3 a <https://w3id.org/steel/ProcessOntology/Sensor> .

fileid:TestTime a <https://w3id.org/steel/ProcessOntology/TestTime> .

fileid:tableGroup a csvw:TableGroup ;
    csvw:table [ a csvw:Table ;
            rdfs:label "Time series data" ;
            csvw:tableSchema [ a csvw:Schema ;
                    csvw:column [ a csvw:Column ;
                            qudt:quantity fileid:Sensor2 ;
                            csvw:titles "column_02"^^xsd:string ;
                            foaf1:page [ a foaf1:Document ;
                                    dcterms:format "https://www.iana.org/assignments/media-types/application/json"^^xsd:anyURI ;
                                    dcterms:identifier "https://www.example.org/column-2"^^xsd:anyURI ;
                                    dcterms:type "http://purl.org/dc/terms/Dataset"^^xsd:anyURI ] ],
                        [ a csvw:Column ;
                            qudt:quantity fileid:TestTime ;
                            csvw:titles "time"^^xsd:string ;
                            foaf1:page [ a foaf1:Document ;
                                    dcterms:format "https://www.iana.org/assignments/media-types/application/json"^^xsd:anyURI ;
                                    dcterms:identifier "https://www.example.org/column-0"^^xsd:anyURI ;
                                    dcterms:type "http://purl.org/dc/terms/Dataset"^^xsd:anyURI ] ],
                        [ a csvw:Column ;
                            qudt:quantity fileid:Sensor3 ;
                            csvw:titles "column_03"^^xsd:string ;
                            foaf1:page [ a foaf1:Document ;
                                    dcterms:format "https://www.iana.org/assignments/media-types/application/json"^^xsd:anyURI ;
                                    dcterms:identifier "https://www.example.org/column-3"^^xsd:anyURI ;
                                    dcterms:type "http://purl.org/dc/terms/Dataset"^^xsd:anyURI ] ],
                        [ a csvw:Column ;
                            qudt:quantity fileid:Sensor1 ;
                            csvw:titles "column_01"^^xsd:string ;
                            foaf1:page [ a foaf1:Document ;
                                    dcterms:format "https://www.iana.org/assignments/media-types/application/json"^^xsd:anyURI ;
                                    dcterms:identifier "https://www.example.org/column-1"^^xsd:anyURI ;
                                    dcterms:type "http://purl.org/dc/terms/Dataset"^^xsd:anyURI ] ] ] ] .
```

</Details>
</blockQuote>


Again, you will be able to investigate the `general_metadata`, `plain_metadata`, `time_series_metadata` and `time_series` attributes in the same way as stated in the [first example](1_csv).
