
# Running the pipeline

In this chapter we will show you how to run the pipeline and how to get the outputs of the pipeline. We will use the inputs for the first example with the csv file from the tensile test experiment. The inputs may differ for your usecase.

Please apply the mapping, addtional triples and the parser arguments to the pipeline configuration and run the pipeline in the following manner:


```{python}
from data2rdf import Data2RDF, Parser

parser_args = {
      "metadata_sep":"\t",
      "time_series_sep":"\t",
      "metadata_length":20
   }

raw_data = "path/to/file.csv"
mapping = "path/to/mapping.json"
extra = "path/to/additional_triples.ttl"

pipeline = Data2RDF(
    raw_data=raw_data,
    parser=Parser.csv,
    mapping=mapping_file,
    parser_args=parser_args,
    extra_triples=extra,
    config={
      "base_url": "https://example.org/123", #this is optional and defaults to "https://example.org"
    }
)
```

Alternatively, you are able to pass the mapping, the additional triples and the csv file with the data directly to the pipeline (the data has been shortened for readability - indicated by `[...]`):

```{python}
raw_data = """"Prüfinstitut"	"institute_1"
"Projektnummer"	"123456"
"Projektname"	"proj_name_1"
"Datum/Uhrzeit"	44335.4	""
[...]
"Prüfzeit"	"Standardkraft"	"Traversenweg absolut"	"Standardweg"	"Breitenänderung"	"Dehnung"
"s"	"N"	"mm"	"mm"	"mm"	"mm"
0.902359827	0.576537916	0.261094396	0.767421407	0.950183725	0.035807567
0.440620562	0.989528723	0.983277189	0.765300358	0.83547718	0.86967659
[...]
"""

mapping = [
  {
    "iri": "https://w3id.org/steel/ProcessOntology/TestTime",
    "key": "Pr\u00fcfzeit"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/StandardForce",
    "key": "Standardkraft"
  },
  [...]
]

extra="""
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix fileid: <http://abox-namespace-placeholder.org/> .

#  Describe the Tester and the Facility and lab

fileid:TestingFacility rdf:type prov:Organization , prov:Location .

fileid:TestingLab rdf:type prov:Location, prov:Agent ;
                  prov:atLocation fileid:TestingFacility .

[...]
"""

pipeline = Data2RDF(
    raw_data=raw_data,
    parser=Parser.csv,
    mapping=mapping,
    parser_args=parser_args,
    extra_triples=extra,
    config={
      "base_url": "https://example.org/123"
    }
)
```

The mapping can also be provided as a csv or excel file (**only as a file writen to disk, not as a string in memory**):

```{csv}
key;iri;annotation
Prüfinstitut;https://w3id.org/steel/ProcessOntology/TestingFacility;
Projektnummer;https://w3id.org/steel/ProcessOntology/ProjectNumber;
Projektname;https://w3id.org/steel/ProcessOntology/ProjectName;
Datum/Uhrzeit;https://w3id.org/steel/ProcessOntology/TimeStamp;
Maschinendaten;https://w3id.org/steel/ProcessOntology/MachineData;
Kraftaufnehmer;https://w3id.org/steel/ProcessOntology/ForceMeasuringDevice;
Wegaufnehmer;https://w3id.org/steel/ProcessOntology/DisplacementTransducer;
Prüfnorm;https://w3id.org/steel/ProcessOntology/TestStandard;
[...]
```

# The outputs

The pipeline run was succuessful, when no error has occured. If there are any missmatches in the mapping, the pipeline will raise it as a warning.

The pipeline will deliver you the following outputs:

* `graph`: the generated RDF graph
* `plain_metadata`: the plain values of the metadata of the experiment
* `time_series`: the plain time series of the experiment
* `time_series_metadata`: the metadata of the time series

## The RDF graph

You will be able to print the resulting graph with the following command:

```{python}
print(pipeline.graph.serialize())
```

The output will look like this:

<blockquote>
<Details>
<summary><b>Click here to expand</b></summary>

```{turtle}
@prefix csvw: <http://www.w3.org/ns/csvw#> .
@prefix dcat: <http://www.w3.org/ns/dcat#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix fileid: <https://www.example.org/> .
@prefix foaf1: <http://xmlns.com/foaf/spec/> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix qudt: <http://qudt.org/schema/qudt/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

fileid:TensileTestExperiment a prov:Activity ;
    prov:generated fileid:AbsoluteCrossheadTravel,
        fileid:Extension,
        fileid:Remark,
        fileid:StandardForce,
        fileid:TimeStamp,
        fileid:dataset ;
    prov:hadPlan fileid:TestStandard ;
    prov:used fileid:DisplacementTransducer,
        fileid:ForceMeasuringDevice,
        fileid:TensileTestSpecimen,
        fileid:TensileTestingMachine,
        fileid:TestingFacility ;
    prov:wasAssociatedWith fileid:Tester ;
    prov:wasInfluencedBy fileid:ExperimentPreparation .

fileid:TestingStandard a prov:Plan .

fileid:Elongation a <https://w3id.org/steel/ProcessOntology/Elongation> ;
    qudt:hasUnit "http://qudt.org/vocab/unit/MilliM"^^xsd:anyURI .

fileid:ExperimentPreparation a prov:Activity ;
    prov:atLocation fileid:TestingLab ;
    prov:generated fileid:OriginalGaugeLength,
        fileid:Preload,
        fileid:TestingRate ;
    prov:wasAssociatedWith fileid:DisplacementTransducer,
        fileid:ForceMeasuringDevice,
        fileid:TensileTestSpecimen,
        fileid:TensileTestingMachine,
        fileid:Tester ;
    prov:wasInfluencedBy fileid:SamplePreparatation .

fileid:MachineData a <https://w3id.org/steel/ProcessOntology/MachineData> ;
    rdfs:label "maschine_1" .

fileid:Project a prov:Activity ;
    prov:generated fileid:ProjectName,
        fileid:ProjectNumber ;
    prov:wasAssociatedWith fileid:TestingFacility .

fileid:SampleIdentifier-2 a <https://w3id.org/steel/ProcessOntology/SampleIdentifier-2> ;
    rdfs:label "Probentyp_2" .

fileid:SamplePreparatation a prov:Activity ;
    prov:generated fileid:ParallelLength,
        fileid:SpecimenThickness,
        fileid:SpecimenType,
        fileid:SpecimenWidth ;
    prov:wasAssociatedWith fileid:Material,
        fileid:TensileTestSpecimen ;
    prov:wasInfluencedBy fileid:Project .

fileid:Temperature a prov:Entity,
        <https://w3id.org/steel/ProcessOntology/Temperature> ;
    qudt:hasUnit "http://qudt.org/vocab/unit/DEG_C"^^xsd:anyURI ;
    qudt:value "22.0"^^xsd:float ;
    prov:wasAttributedTo fileid:TestingLab .

fileid:TestTime a <https://w3id.org/steel/ProcessOntology/TestTime> ;
    qudt:hasUnit "http://qudt.org/vocab/unit/SEC"^^xsd:anyURI .

fileid:WidthChange a <https://w3id.org/steel/ProcessOntology/WidthChange> ;
    qudt:hasUnit "http://qudt.org/vocab/unit/MilliM"^^xsd:anyURI .

fileid:dataset a dcat:Dataset,
        prov:Entity ;
    dcterms:hasPart fileid:tableGroup ;
    dcat:distribution [ a dcat:Distribution ;
            dcat:accessURL "https://www.example.org/download"^^xsd:anyURI ;
            dcat:mediaType "http://www.iana.org/assignments/media-types/text/csv"^^xsd:anyURI ] .

fileid:tableGroup a csvw:TableGroup ;
    csvw:table [ a csvw:Table ;
            rdfs:label "Metadata" ;
            csvw:row [ a csvw:Row ;
                    csvw:describes fileid:TimeStamp ;
                    csvw:rownum 3 ;
                    csvw:titles "Datum/Uhrzeit"^^xsd:string ],
                [ a csvw:Row ;
                    qudt:quantity fileid:SpecimenThickness ;
                    csvw:rownum 14 ;
                    csvw:titles "Probendicke"^^xsd:string ],
                [ a csvw:Row ;
                    csvw:describes fileid:Remark ;
                    csvw:rownum 19 ;
                    csvw:titles "Bemerkung"^^xsd:string ],
                [ a csvw:Row ;
                    qudt:quantity fileid:ParallelLength ;
                    csvw:rownum 13 ;
                    csvw:titles "Versuchslänge"^^xsd:string ],
                [ a csvw:Row ;
                    csvw:describes fileid:TestingFacility ;
                    csvw:rownum 0 ;
                    csvw:titles "Prüfinstitut"^^xsd:string ],
                [ a csvw:Row ;
                    csvw:describes fileid:Material ;
                    csvw:rownum 8 ;
                    csvw:titles "Werkstoff"^^xsd:string ],
                [ a csvw:Row ;
                    csvw:describes fileid:DisplacementTransducer ;
                    csvw:rownum 6 ;
                    csvw:titles "Wegaufnehmer"^^xsd:string ],
                [ a csvw:Row ;
                    csvw:describes fileid:ProjectNumber ;
                    csvw:rownum 1 ;
                    csvw:titles "Projektnummer"^^xsd:string ],
                [ a csvw:Row ;
                    qudt:quantity fileid:OriginalGaugeLength ;
                    csvw:rownum 12 ;
                    csvw:titles "Messlänge Standardweg"^^xsd:string ],
                [ a csvw:Row ;
                    csvw:describes fileid:Tester ;
                    csvw:rownum 10 ;
                    csvw:titles "Prüfer"^^xsd:string ],
                [ a csvw:Row ;
                    qudt:quantity fileid:Preload ;
                    csvw:rownum 17 ;
                    csvw:titles "Vorkraft"^^xsd:string ],
                [ a csvw:Row ;
                    csvw:describes fileid:MachineData ;
                    csvw:rownum 4 ;
                    csvw:titles "Maschinendaten"^^xsd:string ],
                [ a csvw:Row ;
                    qudt:quantity fileid:Temperature ;
                    csvw:rownum 18 ;
                    csvw:titles "Temperatur"^^xsd:string ],
                [ a csvw:Row ;
                    csvw:describes fileid:TestStandard ;
                    csvw:rownum 7 ;
                    csvw:titles "Prüfnorm"^^xsd:string ],
                [ a csvw:Row ;
                    csvw:describes fileid:SampleIdentifier-2 ;
                    csvw:rownum 11 ;
                    csvw:titles "Probenkennung 2"^^xsd:string ],
                [ a csvw:Row ;
                    csvw:describes fileid:SpecimenType ;
                    csvw:rownum 9 ;
                    csvw:titles "Probentyp"^^xsd:string ],
                [ a csvw:Row ;
                    qudt:quantity fileid:SpecimenWidth ;
                    csvw:rownum 15 ;
                    csvw:titles "Probenbreite"^^xsd:string ],
                [ a csvw:Row ;
                    csvw:describes fileid:ProjectName ;
                    csvw:rownum 2 ;
                    csvw:titles "Projektname"^^xsd:string ],
                [ a csvw:Row ;
                    csvw:describes fileid:ForceMeasuringDevice ;
                    csvw:rownum 5 ;
                    csvw:titles "Kraftaufnehmer"^^xsd:string ],
                [ a csvw:Row ;
                    qudt:quantity fileid:TestingRate ;
                    csvw:rownum 16 ;
                    csvw:titles "Prüfgeschwindigkeit"^^xsd:string ] ],
        [ a csvw:Table ;
            rdfs:label "Time series data" ;
            csvw:tableSchema [ a csvw:Schema ;
                    csvw:column [ a csvw:Column ;
                            qudt:quantity fileid:Elongation ;
                            csvw:titles "Dehnung"^^xsd:string ;
                            foaf1:page [ a foaf1:Document ;
                                    dcterms:format "https://www.iana.org/assignments/media-types/application/json"^^xsd:anyURI ;
                                    dcterms:identifier "https://www.example.org/column-5"^^xsd:anyURI ;
                                    dcterms:type "http://purl.org/dc/terms/Dataset"^^xsd:anyURI ] ],
                        [ a csvw:Column ;
                            qudt:quantity fileid:WidthChange ;
                            csvw:titles "Breitenänderung"^^xsd:string ;
                            foaf1:page [ a foaf1:Document ;
                                    dcterms:format "https://www.iana.org/assignments/media-types/application/json"^^xsd:anyURI ;
                                    dcterms:identifier "https://www.example.org/column-4"^^xsd:anyURI ;
                                    dcterms:type "http://purl.org/dc/terms/Dataset"^^xsd:anyURI ] ],
                        [ a csvw:Column ;
                            qudt:quantity fileid:AbsoluteCrossheadTravel ;
                            csvw:titles "Traversenweg absolut"^^xsd:string ;
                            foaf1:page [ a foaf1:Document ;
                                    dcterms:format "https://www.iana.org/assignments/media-types/application/json"^^xsd:anyURI ;
                                    dcterms:identifier "https://www.example.org/column-2"^^xsd:anyURI ;
                                    dcterms:type "http://purl.org/dc/terms/Dataset"^^xsd:anyURI ] ],
                        [ a csvw:Column ;
                            qudt:quantity fileid:Extension ;
                            csvw:titles "Standardweg"^^xsd:string ;
                            foaf1:page [ a foaf1:Document ;
                                    dcterms:format "https://www.iana.org/assignments/media-types/application/json"^^xsd:anyURI ;
                                    dcterms:identifier "https://www.example.org/column-3"^^xsd:anyURI ;
                                    dcterms:type "http://purl.org/dc/terms/Dataset"^^xsd:anyURI ] ],
                        [ a csvw:Column ;
                            qudt:quantity fileid:StandardForce ;
                            csvw:titles "Standardkraft"^^xsd:string ;
                            foaf1:page [ a foaf1:Document ;
                                    dcterms:format "https://www.iana.org/assignments/media-types/application/json"^^xsd:anyURI ;
                                    dcterms:identifier "https://www.example.org/column-1"^^xsd:anyURI ;
                                    dcterms:type "http://purl.org/dc/terms/Dataset"^^xsd:anyURI ] ],
                        [ a csvw:Column ;
                            qudt:quantity fileid:TestTime ;
                            csvw:titles "Prüfzeit"^^xsd:string ;
                            foaf1:page [ a foaf1:Document ;
                                    dcterms:format "https://www.iana.org/assignments/media-types/application/json"^^xsd:anyURI ;
                                    dcterms:identifier "https://www.example.org/column-0"^^xsd:anyURI ;
                                    dcterms:type "http://purl.org/dc/terms/Dataset"^^xsd:anyURI ] ] ] ] .

fileid:AbsoluteCrossheadTravel a prov:Entity,
        <https://w3id.org/steel/ProcessOntology/AbsoluteCrossheadTravel> ;
    qudt:hasUnit "http://qudt.org/vocab/unit/MilliM"^^xsd:anyURI ;
    prov:wasDerivedFrom fileid:DisplacementTransducer .

fileid:Extension a prov:Entity,
        <https://w3id.org/steel/ProcessOntology/Extension> ;
    qudt:hasUnit "http://qudt.org/vocab/unit/MilliM"^^xsd:anyURI ;
    prov:wasDerivedFrom fileid:DisplacementTransducer .

fileid:Material a prov:Agent,
        <https://w3id.org/steel/ProcessOntology/Material>,
        <https://w3id.org/steel/ProcessOntology/Werkstoff_1> ;
    rdfs:label "Werkstoff_1" .

fileid:OriginalGaugeLength a prov:Entity,
        <https://w3id.org/steel/ProcessOntology/OriginalGaugeLength> ;
    qudt:hasUnit "http://qudt.org/vocab/unit/MilliM"^^xsd:anyURI ;
    qudt:value "80.0"^^xsd:float ;
    prov:wasAttributedTo fileid:DisplacementTransducer .

fileid:ParallelLength a prov:Entity,
        <https://w3id.org/steel/ProcessOntology/ParallelLength> ;
    qudt:hasUnit "http://qudt.org/vocab/unit/MilliM"^^xsd:anyURI ;
    qudt:value "120.0"^^xsd:float ;
    prov:wasAttributedTo fileid:TensileTestSpecimen .

fileid:Preload a prov:Entity,
        <https://w3id.org/steel/ProcessOntology/Preload> ;
    qudt:hasUnit "http://qudt.org/vocab/unit/MegaPA"^^xsd:anyURI ;
    qudt:value "2.0"^^xsd:float ;
    prov:wasAttributedTo fileid:TensileTestingMachine .

fileid:ProjectName a prov:Entity,
        <https://w3id.org/steel/ProcessOntology/ProjectName> ;
    rdfs:label "proj_name_1" .

fileid:ProjectNumber a prov:Entity,
        <https://w3id.org/steel/ProcessOntology/ProjectNumber> ;
    rdfs:label "123456" .

fileid:Remark a <https://w3id.org/steel/ProcessOntology/Remark> ;
    rdfs:label "" .

fileid:SpecimenThickness a prov:Entity,
        <https://w3id.org/steel/ProcessOntology/SpecimenThickness> ;
    qudt:hasUnit "http://qudt.org/vocab/unit/MilliM"^^xsd:anyURI ;
    qudt:value "1.55"^^xsd:float ;
    prov:wasAttributedTo fileid:TensileTestSpecimen .

fileid:SpecimenType a prov:Entity,
        <https://w3id.org/steel/ProcessOntology/SpecimenType> ;
    rdfs:label "Probentyp_1" ;
    prov:wasAttributedTo fileid:TensileTestSpecimen .

fileid:SpecimenWidth a prov:Entity,
        <https://w3id.org/steel/ProcessOntology/SpecimenWidth> ;
    qudt:hasUnit "http://qudt.org/vocab/unit/MilliM"^^xsd:anyURI ;
    qudt:value "20.04"^^xsd:float ;
    prov:wasAttributedTo fileid:TensileTestSpecimen .

fileid:StandardForce a prov:Entity,
        <https://w3id.org/steel/ProcessOntology/StandardForce> ;
    qudt:hasUnit "http://qudt.org/vocab/unit/N"^^xsd:anyURI ;
    prov:wasDerivedFrom fileid:ForceMeasuringDevice .

fileid:TestStandard a <https://w3id.org/steel/ProcessOntology/TestStandard> ;
    rdfs:label "ISO-XX" .

fileid:TestingRate a prov:Entity,
        <https://w3id.org/steel/ProcessOntology/TestingRate> ;
    qudt:hasUnit "http://qudt.org/vocab/unit/MilliM-PER-SEC"^^xsd:anyURI ;
    qudt:value "0.1"^^xsd:float ;
    prov:wasAttributedTo fileid:TensileTestingMachine .

fileid:TimeStamp a <https://w3id.org/steel/ProcessOntology/TimeStamp> ;
    rdfs:label "44335.4" .

fileid:Tester a prov:Agent,
        <https://w3id.org/steel/ProcessOntology/Tester> ;
    rdfs:label "abc" ;
    prov:actedOnBehalfOf fileid:TestingFacility ;
    prov:atLocation fileid:TestingLab .

fileid:ForceMeasuringDevice a prov:Agent,
        prov:Entity,
        <https://w3id.org/steel/ProcessOntology/ForceMeasuringDevice> ;
    rdfs:label "Kraftaufnehmer_1" ;
    prov:atLocation fileid:TestingLab .

fileid:TensileTestingMachine a prov:Agent,
        prov:Entity ;
    prov:atLocation fileid:TestingLab .

fileid:TestingFacility a prov:Location,
        prov:Organization,
        <https://w3id.org/steel/ProcessOntology/TestingFacility> ;
    rdfs:label "institute_1" .

fileid:DisplacementTransducer a prov:Agent,
        prov:Entity,
        <https://w3id.org/steel/ProcessOntology/DisplacementTransducer> ;
    rdfs:label "Wegaufnehmer_1" ;
    prov:atLocation fileid:TestingLab .

fileid:TestingLab a prov:Agent,
        prov:Location ;
    prov:atLocation fileid:TestingFacility .

fileid:TensileTestSpecimen a prov:Agent,
        prov:Entity .

```
</Details>
</blockquote>


```{info}
You can see that the graph consist now out of several subgraphs:

* the data graph
    * graph describing the metadata of the experiment and the metadata of the time series.
    * the graph describing the structure of the csv file
* the additional triples

Please see the following sections for more details.
```

### Data graph

The part of the graph describing the metadata of the experiment and the metadata of the time series may look like this:
```{turtle}
[...]


# this is from the experiment metadata
fileid:Material a prov:Agent,
        <https://w3id.org/steel/ProcessOntology/Material> ;
    rdfs:label "Werkstoff_1" .

# this is from the experiment metadata
fileid:OriginalGaugeLength a prov:Entity,
        <https://w3id.org/steel/ProcessOntology/OriginalGaugeLength> ;
    qudt:hasUnit "http://qudt.org/vocab/unit/MilliM"^^xsd:anyURI ;
    qudt:value "80.0"^^xsd:float .

# this is from the time series metadata
fileid:AbsoluteCrossheadTravel a prov:Entity,
        <https://w3id.org/steel/ProcessOntology/AbsoluteCrossheadTravel> ;
    qudt:hasUnit "http://qudt.org/vocab/unit/MilliM"^^xsd:anyURI .

# this is from the time series metadata
fileid:Extension a prov:Entity,
        <https://w3id.org/steel/ProcessOntology/Extension> ;
    qudt:hasUnit "http://qudt.org/vocab/unit/MilliM"^^xsd:anyURI .
[...]
```

Whereas the part of the graph describing the structure of the csv file may look like this:

```{turtle}
fileid:tableGroup a csvw:TableGroup ;
    csvw:table [ a csvw:Table ;
            rdfs:label "Metadata" ;
            csvw:row [ a csvw:Row ;
                    qudt:quantity fileid:OriginalGaugeLength ;
                    csvw:rownum 12 ;
                    csvw:titles "Messlänge Standardweg"^^xsd:string ],
                [ a csvw:Row ;
                    csvw:describes fileid:Material ;
                    csvw:rownum 8 ;
                    csvw:titles "Werkstoff"^^xsd:string ],

            ...

            ];


        [ a csvw:Table ;
            rdfs:label "Time series data" ;
            csvw:tableSchema [ a csvw:Schema ;
                    csvw:column [ a csvw:Column ;
                            qudt:quantity fileid:AbsoluteCrossheadTravel ;
                            csvw:titles "Traversenweg absolut"^^xsd:string ;
                            foaf:page [ a foaf:Document ;
                                    dcterms:format "https://www.iana.org/assignments/media-types/application/json"^^xsd:anyURI ;
                                    dcterms:identifier "https://www.example.org/download/column-2"^^xsd:anyURI ;
                                    dcterms:type "http://pu.,rl.org/dc/terms/Dataset"^^xsd:anyURI ] ],
                        [ a csvw:Column ;
                            qudt:quantity fileid:Extension ;
                            csvw:titles "Standardweg"^^xsd:string ;
                            foaf:page [ a foaf:Document ;
                                    dcterms:format "https://www.iana.org/assignments/media-types/application/json"^^xsd:anyURI ;
                                    dcterms:identifier "https://www.example.org/download/column-3"^^xsd:anyURI ;
                                    dcterms:type "http://purl.org/dc/terms/Dataset"^^xsd:anyURI ] ],

                          ...

                          ] ] .
```

You may note here that the two kinds of metadata are described through two tables groups in the output graph: one with an `rdfs:label "Metadata" ` and one with an `rdfs:label "Time series data"`. Both table groups are either describing the rows (e.g. for `fileid:Material` and `fileid:OriginalGaugeLength`) or the columns (e.g. `fileid:AbsoluteCrossheadTravel` and `fileid:Extension`) of the respective metadata and are pointing to the definition of the individuals datum (see snippet above).

Please note here that the concepts for the individuals `fileid:AbloluteCrossheadTravel` and `fileid:Extension` describing the time series data only make a reference to an access url described by `https://www.example.org/download/column-2` and `https://www.example.org/download/column-3`, which may be the routes in a web server or an access url in a database. The base of this access url is `https://www.example.org/download` and can be adjusted in the config of the pipeline by setting `config = {"data_download_uri": "https://www.example.org/download/dataset-123"}`.

By setting `config = {"suppress_file_description": True}` this file description of the table groups will be neglected in the output graph.


### Method graph

As already mentioned above, the method graph is not automatically derived from the data. The domain expert needs to supply the information in coordination with the ontologist.

When the data graph is generated from the pipeline, the abox placeholder of the method graph is replaced with the base uri of the data graph so that the IRI of the individuals between the method graph and the data graph are the same. Have a look on this snipped below in order to see that the individual for `fileid:TestingRate` from the data graph is now connected with the individual for `fileid:TensileTestingMachine` from the method graph:

```{turtle}
fileid:TestingRate a prov:Entity,
        <https://w3id.org/steel/ProcessOntology/TestingRate> ;
    qudt:hasUnit "http://qudt.org/vocab/unit/MilliM-PER-SEC"^^xsd:anyURI ;
    qudt:value "0.1"^^xsd:float ;
    prov:wasAttributedTo fileid:TensileTestingMachine .

fileid:TensileTestingMachine a prov:Agent,
        prov:Entity ;
    prov:atLocation fileid:TestingLab .
```

## The general metadata

In case of the need of further processing the general metadata (key-value pairs) resulting from the pipeline after parsing, the `general_metadata` property can be accessed as follows:

```{python}
print(pipeline.general_metadata)
```

The result should look like this:

<blockQuote>
<Details>
<summary><b>Click here to expand</b></summary>

```{python}
[PropertyGraph(
	iri=https://w3id.org/steel/ProcessOntology/TestingFacility,
	suffix=TestingFacility,
	key=Prüfinstitut,
	value=institute_1,
	annotation=None,
	value_relation=rdfs:label),
 PropertyGraph(
	iri=https://w3id.org/steel/ProcessOntology/ProjectNumber,
	suffix=ProjectNumber,
	key=Projektnummer,
	value=123456,
	annotation=None,
	value_relation=rdfs:label),
 PropertyGraph(
	iri=https://w3id.org/steel/ProcessOntology/ProjectName,
	suffix=ProjectName,
	key=Projektname,
	value=proj_name_1,
	annotation=None,
	value_relation=rdfs:label),
 PropertyGraph(
	iri=https://w3id.org/steel/ProcessOntology/TimeStamp,
	suffix=TimeStamp,
	key=Datum/Uhrzeit,
	value=44335.4,
	annotation=None,
	value_relation=rdfs:label),
 PropertyGraph(
	iri=https://w3id.org/steel/ProcessOntology/MachineData,
	suffix=MachineData,
	key=Maschinendaten,
	value=maschine_1,
	annotation=None,
	value_relation=rdfs:label),
 PropertyGraph(
	iri=https://w3id.org/steel/ProcessOntology/ForceMeasuringDevice,
	suffix=ForceMeasuringDevice,
	key=Kraftaufnehmer,
	value=Kraftaufnehmer_1,
	annotation=None,
	value_relation=rdfs:label),
 PropertyGraph(
	iri=https://w3id.org/steel/ProcessOntology/DisplacementTransducer,
	suffix=DisplacementTransducer,
	key=Wegaufnehmer,
	value=Wegaufnehmer_1,
	annotation=None,
	value_relation=rdfs:label),
 PropertyGraph(
	iri=https://w3id.org/steel/ProcessOntology/TestStandard,
	suffix=TestStandard,
	key=Prüfnorm,
	value=ISO-XX,
	annotation=None,
	value_relation=rdfs:label),
 PropertyGraph(
	iri=https://w3id.org/steel/ProcessOntology/Material,
	suffix=Material,
	key=Werkstoff,
	value=Werkstoff_1,
	annotation=https://w3id.org/steel/ProcessOntology/Werkstoff_1,
	value_relation=rdfs:label),
 PropertyGraph(
	iri=https://w3id.org/steel/ProcessOntology/SpecimenType,
	suffix=SpecimenType,
	key=Probentyp,
	value=Probentyp_1,
	annotation=None,
	value_relation=rdfs:label),
 PropertyGraph(
	iri=https://w3id.org/steel/ProcessOntology/Tester,
	suffix=Tester,
	key=Prüfer,
	value=abc,
	annotation=None,
	value_relation=rdfs:label),
 PropertyGraph(
	iri=https://w3id.org/steel/ProcessOntology/SampleIdentifier-2,
	suffix=SampleIdentifier-2,
	key=Probenkennung 2,
	value=Probentyp_2,
	annotation=None,
	value_relation=rdfs:label),
 QuantityGraph(
	iri=https://w3id.org/steel/ProcessOntology/OriginalGaugeLength,
	suffix=OriginalGaugeLength,
	key=Messlänge Standardweg,
	unit=http://qudt.org/vocab/unit/MilliM,
	value=80,
	unit_relation=qudt:hasUnit,
	value_relation=qudt:value),
 QuantityGraph(
	iri=https://w3id.org/steel/ProcessOntology/ParallelLength,
	suffix=ParallelLength,
	key=Versuchslänge,
	unit=http://qudt.org/vocab/unit/MilliM,
	value=120,
	unit_relation=qudt:hasUnit,
	value_relation=qudt:value),
 QuantityGraph(
	iri=https://w3id.org/steel/ProcessOntology/SpecimenThickness,
	suffix=SpecimenThickness,
	key=Probendicke,
	unit=http://qudt.org/vocab/unit/MilliM,
	value=1.55,
	unit_relation=qudt:hasUnit,
	value_relation=qudt:value),
 QuantityGraph(
	iri=https://w3id.org/steel/ProcessOntology/SpecimenWidth,
	suffix=SpecimenWidth,
	key=Probenbreite,
	unit=http://qudt.org/vocab/unit/MilliM,
	value=20.04,
	unit_relation=qudt:hasUnit,
	value_relation=qudt:value),
 QuantityGraph(
	iri=https://w3id.org/steel/ProcessOntology/TestingRate,
	suffix=TestingRate,
	key=Prüfgeschwindigkeit,
	unit=http://qudt.org/vocab/unit/MilliM-PER-SEC,
	value=0.1,
	unit_relation=qudt:hasUnit,
	value_relation=qudt:value),
 QuantityGraph(
	iri=https://w3id.org/steel/ProcessOntology/Preload,
	suffix=Preload,
	key=Vorkraft,
	unit=http://qudt.org/vocab/unit/MegaPA,
	value=2,
	unit_relation=qudt:hasUnit,
	value_relation=qudt:value),
 QuantityGraph(
	iri=https://w3id.org/steel/ProcessOntology/Temperature,
	suffix=Temperature,
	key=Temperatur,
	unit=http://qudt.org/vocab/unit/DEG_C,
	value=22,
	unit_relation=qudt:hasUnit,
	value_relation=qudt:value),
 PropertyGraph(
	iri=https://w3id.org/steel/ProcessOntology/Remark,
	suffix=Remark,
	key=Bemerkung,
	value=,
	annotation=None,
	value_relation=rdfs:label)]
```
</Details>
</blockQuote>

The result is a list of `PropertyGraph` and `QuantityGraph` objects which result from the pipeline. The `PropertyGraph` objects contain the key, value and annotation of non-quantity objects such as the `TestStandard`, `Material` and `SpecimenType`	. The `QuantityGraph` objects contain the key, value and unit of quantivative concepts such as the `OriginalGaugeLength` and `SpecimenThickness`.

The properties for each of the objects in the list can be accessed as follows (in this case the key, value, suffix and unit are printed):

```{python}
print([
    (obj.key, obj.value, obj.suffix, obj.unit)
    if hasattr(obj,"unit") else (obj.key, obj.value, obj.suffix)
    for obj in pipeline.general_metadata
])
```

The output should look like this:
```{python}
[('Prüfinstitut', 'institute_1', 'TestingFacility'),
 ('Projektnummer', '123456', 'ProjectNumber'),
 ('Projektname', 'proj_name_1', 'ProjectName'),
 ('Datum/Uhrzeit', '44335.4', 'TimeStamp'),
 ('Maschinendaten', 'maschine_1', 'MachineData'),
 ('Kraftaufnehmer', 'Kraftaufnehmer_1', 'ForceMeasuringDevice'),
 ('Wegaufnehmer', 'Wegaufnehmer_1', 'DisplacementTransducer'),
 ('Prüfnorm', 'ISO-XX', 'TestStandard'),
 ('Werkstoff', 'Werkstoff_1', 'Material'),
 ('Probentyp', 'Probentyp_1', 'SpecimenType'),
 ('Prüfer', 'abc', 'Tester'),
 ('Probenkennung 2', 'Probentyp_2', 'SampleIdentifier-2'),
 ('Messlänge Standardweg', 80, 'OriginalGaugeLength','http://qudt.org/vocab/unit/MilliM'),
 ('Versuchslänge', 120, 'ParallelLength', 'http://qudt.org/vocab/unit/MilliM'),
 ('Probendicke', 1.55, 'SpecimenThickness', 'http://qudt.org/vocab/unit/MilliM'),
 ('Probenbreite', 20.04, 'SpecimenWidth', 'http://qudt.org/vocab/unit/MilliM'),
 ('Prüfgeschwindigkeit', 0.1, 'TestingRate', 'http://qudt.org/vocab/unit/MilliM-PER-SEC'),
 ('Vorkraft', 2, 'Preload', 'http://qudt.org/vocab/unit/MegaPA'),
 ('Temperatur', 22, 'Temperature', 'http://qudt.org/vocab/unit/DEG_C'),
 ('Bemerkung', '', 'Remark')]

```

The data2rdf package is built in a modular way and all of the single `PropertyGraph` and `QuantityGraph` objects are producing small subgraphs describing their individual concept and finally are contributing to the merged `pipeline.graph` object. The individual subgraphs which are describing these entities can be accessed as follows:

```{python}
for object in pipeline.general_metadata:
    print("Subgraph for concept `", object.key,"`:\n")
    print(object.graph.serialize())
    print("\n")
```
The result should look like this:

<blockQuote>
<Details>
<summary><b>Click here to expand</b></summary>

```
Subgraph for concept ` Prüfinstitut `:

@prefix fileid: <https://www.example.org/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

fileid:TestingFacility a <https://w3id.org/steel/ProcessOntology/TestingFacility> ;
    rdfs:label "institute_1" .


Subgraph for concept ` Projektnummer `:

@prefix fileid: <https://www.example.org/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

fileid:ProjectNumber a <https://w3id.org/steel/ProcessOntology/ProjectNumber> ;
    rdfs:label "123456" .


Subgraph for concept ` Projektname `:

@prefix fileid: <https://www.example.org/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

fileid:ProjectName a <https://w3id.org/steel/ProcessOntology/ProjectName> ;
    rdfs:label "proj_name_1" .


Subgraph for concept ` Datum/Uhrzeit `:

@prefix fileid: <https://www.example.org/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

fileid:TimeStamp a <https://w3id.org/steel/ProcessOntology/TimeStamp> ;
    rdfs:label "44335.4" .


Subgraph for concept ` Maschinendaten `:

@prefix fileid: <https://www.example.org/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

fileid:MachineData a <https://w3id.org/steel/ProcessOntology/MachineData> ;
    rdfs:label "maschine_1" .


Subgraph for concept ` Kraftaufnehmer `:

@prefix fileid: <https://www.example.org/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

fileid:ForceMeasuringDevice a <https://w3id.org/steel/ProcessOntology/ForceMeasuringDevice> ;
    rdfs:label "Kraftaufnehmer_1" .


Subgraph for concept ` Wegaufnehmer `:

@prefix fileid: <https://www.example.org/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

fileid:DisplacementTransducer a <https://w3id.org/steel/ProcessOntology/DisplacementTransducer> ;
    rdfs:label "Wegaufnehmer_1" .


Subgraph for concept ` Prüfnorm `:

@prefix fileid: <https://www.example.org/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

fileid:TestStandard a <https://w3id.org/steel/ProcessOntology/TestStandard> ;
    rdfs:label "ISO-XX" .


Subgraph for concept ` Werkstoff `:

@prefix fileid: <https://www.example.org/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

fileid:Material a <https://w3id.org/steel/ProcessOntology/Material>,
        <https://w3id.org/steel/ProcessOntology/Werkstoff_1> ;
    rdfs:label "Werkstoff_1" .


Subgraph for concept ` Probentyp `:

@prefix fileid: <https://www.example.org/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

fileid:SpecimenType a <https://w3id.org/steel/ProcessOntology/SpecimenType> ;
    rdfs:label "Probentyp_1" .


Subgraph for concept ` Prüfer `:

@prefix fileid: <https://www.example.org/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

fileid:Tester a <https://w3id.org/steel/ProcessOntology/Tester> ;
    rdfs:label "abc" .


Subgraph for concept ` Probenkennung 2 `:

@prefix fileid: <https://www.example.org/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

fileid:SampleIdentifier-2 a <https://w3id.org/steel/ProcessOntology/SampleIdentifier-2> ;
    rdfs:label "Probentyp_2" .


Subgraph for concept ` Messlänge Standardweg `:

@prefix fileid: <https://www.example.org/> .
@prefix qudt: <http://qudt.org/schema/qudt/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

fileid:OriginalGaugeLength a <https://w3id.org/steel/ProcessOntology/OriginalGaugeLength> ;
    qudt:hasUnit "http://qudt.org/vocab/unit/MilliM"^^xsd:anyURI ;
    qudt:value "80.0"^^xsd:float .


Subgraph for concept ` Versuchslänge `:

@prefix fileid: <https://www.example.org/> .
@prefix qudt: <http://qudt.org/schema/qudt/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

fileid:ParallelLength a <https://w3id.org/steel/ProcessOntology/ParallelLength> ;
    qudt:hasUnit "http://qudt.org/vocab/unit/MilliM"^^xsd:anyURI ;
    qudt:value "120.0"^^xsd:float .


Subgraph for concept ` Probendicke `:

@prefix fileid: <https://www.example.org/> .
@prefix qudt: <http://qudt.org/schema/qudt/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

fileid:SpecimenThickness a <https://w3id.org/steel/ProcessOntology/SpecimenThickness> ;
    qudt:hasUnit "http://qudt.org/vocab/unit/MilliM"^^xsd:anyURI ;
    qudt:value "1.55"^^xsd:float .


Subgraph for concept ` Probenbreite `:

@prefix fileid: <https://www.example.org/> .
@prefix qudt: <http://qudt.org/schema/qudt/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

fileid:SpecimenWidth a <https://w3id.org/steel/ProcessOntology/SpecimenWidth> ;
    qudt:hasUnit "http://qudt.org/vocab/unit/MilliM"^^xsd:anyURI ;
    qudt:value "20.04"^^xsd:float .


Subgraph for concept ` Prüfgeschwindigkeit `:

@prefix fileid: <https://www.example.org/> .
@prefix qudt: <http://qudt.org/schema/qudt/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

fileid:TestingRate a <https://w3id.org/steel/ProcessOntology/TestingRate> ;
    qudt:hasUnit "http://qudt.org/vocab/unit/MilliM-PER-SEC"^^xsd:anyURI ;
    qudt:value "0.1"^^xsd:float .


Subgraph for concept ` Vorkraft `:

@prefix fileid: <https://www.example.org/> .
@prefix qudt: <http://qudt.org/schema/qudt/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

fileid:Preload a <https://w3id.org/steel/ProcessOntology/Preload> ;
    qudt:hasUnit "http://qudt.org/vocab/unit/MegaPA"^^xsd:anyURI ;
    qudt:value "2.0"^^xsd:float .


Subgraph for concept ` Temperatur `:

@prefix fileid: <https://www.example.org/> .
@prefix qudt: <http://qudt.org/schema/qudt/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

fileid:Temperature a <https://w3id.org/steel/ProcessOntology/Temperature> ;
    qudt:hasUnit "http://qudt.org/vocab/unit/DEG_C"^^xsd:anyURI ;
    qudt:value "22.0"^^xsd:float .


Subgraph for concept ` Bemerkung `:

@prefix fileid: <https://www.example.org/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

fileid:Remark a <https://w3id.org/steel/ProcessOntology/Remark> ;
    rdfs:label "" .
```
</Details>
</blockQuote>

Note that all of the `obj.graph` objects are of type `rdflib.graph.Graph` and can also combined and queried individually.

## The plain metadata

In case of the need of further processing the plain metadata (key-value pairs with out units) resulting from the pipeline after parsing, the `plain_metadata` property can be accessed as follows:

```{python}
print(pipeline.plain_metadata)
```

The result should look like this:

```{python}
{'DisplacementTransducer': 'Wegaufnehmer_1',
 'ForceMeasuringDevice': 'Kraftaufnehmer_1',
 'MachineData': 'maschine_1',
 'Material': 'Werkstoff_1',
 'OriginalGaugeLength': 80,
 'ParallelLength': 120,
 'Preload': 2,
 'ProjectName': 'proj_name_1',
 'ProjectNumber': '123456',
 'Remark': '',
 'SampleIdentifier-2': 'Probentyp_2',
 'SpecimenThickness': 1.55,
 'SpecimenType': 'Probentyp_1',
 'SpecimenWidth': 20.04,
 'Temperature': 22,
 'TestStandard': 'ISO-XX',
 'Tester': 'abc',
 'TestingFacility': 'institute_1',
 'TestingRate': 0.1,
 'TimeStamp': '44335.4'}
```

You will notice that this `plain_metadata` is a shorthand for a code snippet like:

```{python}
print({obj.suffix: obj.value for obj in pipeline.general_metadata})
```

## The time series metadata

In case of the need of further processing the time series metadata (header of the time series) resulting from the pipeline after parsing, the `time_series_metadata` property can be accessed as follows:

```{python}
print(pipeline.time_series_metadata)
```

The result should look like this:
```
[QuantityGraph(
	iri=https://w3id.org/steel/ProcessOntology/TestTime,
	suffix=TestTime,
	key=Prüfzeit,
	unit=http://qudt.org/vocab/unit/SEC,
	value=None,
	unit_relation=qudt:hasUnit,
	value_relation=qudt:value),
 QuantityGraph(
	iri=https://w3id.org/steel/ProcessOntology/StandardForce,
	suffix=StandardForce,
	key=Standardkraft,
	unit=http://qudt.org/vocab/unit/N,
	value=None,
	unit_relation=qudt:hasUnit,
	value_relation=qudt:value),
 QuantityGraph(
	iri=https://w3id.org/steel/ProcessOntology/AbsoluteCrossheadTravel,
	suffix=AbsoluteCrossheadTravel,
	key=Traversenweg absolut,
	unit=http://qudt.org/vocab/unit/MilliM,
	value=None,
	unit_relation=qudt:hasUnit,
	value_relation=qudt:value),
 QuantityGraph(
	iri=https://w3id.org/steel/ProcessOntology/Extension,
	suffix=Extension,
	key=Standardweg,
	unit=http://qudt.org/vocab/unit/MilliM,
	value=None,
	unit_relation=qudt:hasUnit,
	value_relation=qudt:value),
 QuantityGraph(
	iri=https://w3id.org/steel/ProcessOntology/WidthChange,
	suffix=WidthChange,
	key=Breitenänderung,
	unit=http://qudt.org/vocab/unit/MilliM,
	value=None,
	unit_relation=qudt:hasUnit,
	value_relation=qudt:value),
 QuantityGraph(
	iri=https://w3id.org/steel/ProcessOntology/Elongation,
	suffix=Elongation,
	key=Dehnung,
	unit=http://qudt.org/vocab/unit/MilliM,
	value=None,
	unit_relation=qudt:hasUnit,
	value_relation=qudt:value)]
```

The result is a list of `QuantityGraph` which (or `PropertyGraph` in case of non-quantative columns) which result from the pipeline. Each object contains information about the time series metadata of a single quantity, such as the key, the unit and the value.


## The time series data

In case of the need of further processing the time series data (tabular data) resulting from the pipeline after parsing, the `time_series` property can be accessed as follows:

```{python}
print(pipeline.time_series)
```

The result is a pandas dataframe and should look like this:

```{python}
         TestTime StandardForce AbsoluteCrossheadTravel    Extension  \
0     0.902359827   0.576537916             0.261094396  0.767421407
1     0.440620562   0.989528723             0.983277189  0.765300358
2     0.534511863   0.174351389             0.964046052  0.908144146
3     0.077564232   0.483112915             0.043854329  0.235058804
4     0.747648914   0.563390673             0.791011895  0.851891125
...           ...           ...                     ...          ...
5729  0.783890462   0.032321797             0.457387448  0.791476396
5730  0.544208828   0.238646028             0.476266364  0.015594418
5731  0.193468426   0.631924775             0.251083259  0.721486115
5732  0.324592426   0.987658323             0.901640266  0.641948648
5733   0.67402323   0.658051293             0.874914004  0.311573918

      WidthChange   Elongation
0     0.950183725  0.035807567
1      0.83547718   0.86967659
2     0.196001376  0.777251975
3     0.162114934   0.17809479
4     0.133555843  0.150183086
...           ...          ...
5729  0.109708946  0.088801482
5730  0.925846039  0.500010629
5731  0.366851207  0.554173276
5732  0.037053021  0.802063516
5733  0.120744053  0.219704279

[5734 rows x 6 columns]
```
