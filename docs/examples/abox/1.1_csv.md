# ABox generation from a CSV file with metadata and time series

## General understanding

In this example, we want to transfor a csv file which encorporates stress/strain of the measurement and some metadata about the experiment into an RDF repesentation.

For this purpose, we are describing the **general metadata** of the experiment as well as the **metadata of the time series**.

```{note}
We do not target to transform the time series itself into RDF, since it usually includes several thousands of datums per column. Hence we would give a reference in the form of an URI which is is pointing to the location of the file (e.g. a route in a web API or a local system path).
```

## The inputs

In this example we will consider the following inputs:

* the csv file produced by the tensile test machine
* the mapping for describing the data in RDF
* the parser arguments for reading the csv file
* the additional triples (optional) for describing additional concepts in RDF which are not contained in the csv file

### The raw data

The csv file produced by the tensile test machine looks like this:

![details](../../assets/img/docu/CSV-Parser.png)

The original file can be accessed [here](https://raw.githubusercontent.com/MI-FraunhoferIWM/data2rdf/f9e5adfe2c18dd0bd4887bc685459671b1fbb29a/tests/csv_pipeline_test/input/data/DX56_D_FZ2_WR00_43.TXT). Due to clarify reasons, we truncated the time series in this document here.

```{note}
We are strictly assuming that metadata is on top of the time series and has a the key-value-unit pattern. Therefore the metadata up to now needs to have a width of 2 to 3 columns. In the future, we may support extending the default width of the metadata, in case if we need to have a width of 4 or more columns, e.g. if there are be more concepts than just value and unit.

We generally assume that the **direction of the metadata is horizontally oriented**, which means that the firs key in each row is the index (or primary key) of the metadata. **All of the values in this metadata shall be represented in an RDF graph**.

Accordingly the **direction of the time series is vertically oriented**, which means that the first key in the header of each column will be the index (or primary key) of the time series. **In contrast to the metadata, we only want to describe the metadata of the time series in RDF and do not want to include each datum of each in the time series into the RDF**.
```

As you may see, the metadata of file _has a length of 22 rows_. The metadata itself is tab-separated, has the name of a concept in the first column (e.g.  `"Vorkraft"`=Preload), the value related to this metadatum in the second column (e.g. `"22"`) and optionally a unit in the third column (e.g. `"MPa"`).

Subsequently, there is the time series with a header which has a length of rows: one with a the concept name (e.g. `"Prüfzeit"`=Test time) columns and one with the respective unit again (e.g. `"s"`).

### The parser arguments

Since we are assuming to have a csv file, we can assume the following parser arguments:

* `"metadata_sep"`: The separator of the metadata
    In this example, we assume that the metadata is tab-separated. Hence the argument is `"\t"`.
* `"time_series_sep"`: The separator of the time series
    In this example, we assume that the time series is tab-separated. Hence the argument is `"\t"`.
* `"metadata_length"`: The length of the metadata
    In this example, we assume that the metadata has 22 rows.
    Hence the argument is `22`.
    The metadata of this example file is including the name of the concept, the value and the unit, if the concept has one:
    ```
    "Prüfinstitut"	"institute_1"
    "Projektnummer"	"123456"
    "Projektname"	"proj_name_1"
    [...]
    "Prüfgeschwindigkeit"	0.1	"mm/s"
    "Vorkraft"	2	"MPa"
    "Temperatur"	22	"°C"
    "Bemerkung"	""
    ```
* `time_series_header_length`: The length of the header of the time series.
    In this example, we assume that the time series has 2 rows, which is the name of the concept in the first row and the corresponding unit in the second row:
    ```
    "Standardweg"	"Breitenänderung"	"Dehnung"
    "s"	"N"	"mm"	"mm"	"mm"	"mm" Hence the argument is `2`
    ```

* `"fillna"`: The value to fill NaN values in the parsed dataframe.
    In this example, we assume that the NaN values in the dataframe are filled with `""`. Hence the argument is `""`. This is in particular of importance when the time series is parsed from the csv file. Since we are using pandas to parse the csv file, we need to make sure that gaps in the time series are filled with `""`, instead of the default `np.nan` values in the dataframe. If not applied here, this might lead to problems in the data2rdf pipeline.


### The mapping

In order to transform the relevant metadata into an RDF for describing the data and the experiment, we **need a well formulated ontology with classes** describing each individual concept in the file.

Since we are **instanciating individuals for each single concept** in the data file and assign the respective SI units, we need to map the key of the concept to the IRI of an ontological class and also make a statement whether we want to read the SI unit from the file or map it manually.

For the quantitative properties (e.g. `"Vorkraft"`=Preload) and non-quantitative properties (.e.g `"Prüfer"`= Name of the tester) in the metadata of the file, we can assume the following mapping:

<blockquote>
<Details>
<summary><b>Click here to expand</b></summary>

```{json}
[
  {
    "iri": "https://w3id.org/steel/ProcessOntology/Remark",
    "key": "Bemerkung"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/WidthChange",
    "key": "Breiten\u00e4nderung"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/TimeStamp",
    "key": "Datum/Uhrzeit"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/Elongation",
    "key": "Dehnung"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/ForceMeasuringDevice",
    "key": "Kraftaufnehmer"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/MachineData",
    "key": "Maschinendaten"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/OriginalGaugeLength",
    "key": "Messl\u00e4nge Standardweg"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/SpecimenWidth",
    "key": "Probenbreite"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/SpecimenThickness",
    "key": "Probendicke"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/SampleIdentifier-2",
    "key": "Probenkennung 2"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/SpecimenType",
    "key": "Probentyp"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/ProjectName",
    "key": "Projektname"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/ProjectNumber",
    "key": "Projektnummer"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/Tester",
    "key": "Pr\u00fcfer"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/TestingRate",
    "key": "Pr\u00fcfgeschwindigkeit"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/TestingFacility",
    "key": "Pr\u00fcfinstitut"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/TestStandard",
    "key": "Pr\u00fcfnorm"
  },
]
```
</Details>
</blockquote>



```{note}
We are using an ontology from the [*Stahldigital*](https://www.iwm.fraunhofer.de/de/warum-fraunhofer-iwm/loesungen-fuer-produktlebenzyklus/digitalisierung-in-der-werkstofftechnik/stahldigital.html) project (see [https://w3id.org/steel/ProcessOntology](https://w3id.org/steel/ProcessOntology)), in your usecase, it might be the case that you might need to establish your own ontology which describes your data set.
```

```{note}
You may notice that this mapping has to follow a certain schema in order to be valid. To be more precise, we have here a list of dictionaries with specifications for the mapping of a concept in the data file.

If you would like to read more about the schema and options for the mapping, please refer to the `Schema` chapter of this documentation.
```

You may see that we simply need to deliver a list of dictionaries with the keys `key` and `iri`. The key is the key of the concept in the data file and the IRI is the Internationalized Resource Identifier of the ontological class for describing the concept.

Let us take the following concept for the example: the key of the concept is `"Vorkraft"` and the IRI is `"https://w3id.org/steel/ProcessOntology/Preload"`, which has been defined in the introduced ontology above. Of course, you **may also choose any ontological IRI from any ontology** which matches your concept from the data file.

Please also note that we are defining the mappings of the metadata and the time series in the same dictionary. The **units of the metadata** is assumed to be read from the **third column of the metadata-section** whereas the **unit of the time series columns** is assumed to be read from the **second row of the time series header**.

During the pipeline run, the units extracted from the metadata and timeseries will be mapped to ontological concepts of the [QUDT ontology](https://www.qudt.org/pages/QUDToverviewPage.html), describing a large set of SI units and off-system units.

In the case that the unit cannot be extracted from the respective section in the data file, we also have the opportunity to map it manually like this:

```{json}
  {
    "iri": "https://w3id.org/steel/ProcessOntology/TestingRate",
    "key": "Pr\u00fcfgeschwindigkeit"
    "unit": "http://qudt.org/vocab/unit/MilliM-PER-SEC"
  }
```

As you may see, we are able to provide the IRI of the QUDT unit directly. However, we als are able to provide the string of the symbols for the unit:
```{json}
  {
    "iri": "https://w3id.org/steel/ProcessOntology/TestingRate",
    "key": "Pr\u00fcfgeschwindigkeit"
    "unit": "mm/s"
  }
```
### The additional triples (optional)

In some cases, the content of the data file does not provide all of the information which which we would like to describe. For this purpose, we can add additional triples to the data graph. These triples are added to the _data graph_ as a so-called _method graph_ which which we can provide as file, as a string with the direct content of this file, or as an RDFlib-Graph. For this example, the additional triples can be defined in the following way:

<blockquote>
<Details>
<summary><b>Click here to expand</b></summary>

```{turtle}
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix fileid: <http://abox-namespace-placeholder.org/> .

#  Describe the Tester and the Facility and lab

fileid:TestingFacility rdf:type prov:Organization , prov:Location .

fileid:TestingLab rdf:type prov:Location, prov:Agent ;
                  prov:atLocation fileid:TestingFacility .

fileid:Tester rdf:type prov:Agent ;
              prov:actedOnBehalfOf fileid:TestingFacility ;
              prov:atLocation fileid:TestingLab .

fileid:Temperature rdf:type prov:Entity ;
                   prov:wasAttributedTo fileid:TestingLab .


# describe the project

fileid:Project rdf:type prov:Activity ;
               prov:wasAssociatedWith fileid:TestingFacility ;
               prov:generated fileid:ProjectName ,
                              fileid:ProjectNumber .

fileid:ProjectName rdf:type prov:Entity .

fileid:ProjectNumber rdf:type prov:Entity .


# Describe the Specimen and its attributes

fileid:SamplePreparatation rdf:type prov:Activity ;
                           prov:wasAssociatedWith fileid:TensileTestSpecimen ,
                                                  fileid:Material ;
                           prov:generated fileid:ParallelLength ,
                                          fileid:SpecimenThickness ,
                                          fileid:SpecimenType ,
                                          fileid:SpecimenWidth ;
                           prov:wasInfluencedBy fileid:Project .

fileid:TensileTestSpecimen rdf:type prov:Agent , prov:Entity .

fileid:Material rdf:type prov:Agent .

fileid:ParallelLength rdf:type prov:Entity ;
                      prov:wasAttributedTo fileid:TensileTestSpecimen .

fileid:SpecimenThickness rdf:type prov:Entity ;
                         prov:wasAttributedTo fileid:TensileTestSpecimen .

fileid:SpecimenType rdf:type prov:Entity ;
                    prov:wasAttributedTo fileid:TensileTestSpecimen .

fileid:SpecimenWidth rdf:type prov:Entity ;
                    prov:wasAttributedTo fileid:TensileTestSpecimen .

# Describe the experiment preparation

fileid:ExperimentPreparation rdf:type prov:Activity ;
                             prov:atLocation fileid:TestingLab ;
                             prov:wasAssociatedWith fileid:Tester ,
                                                    fileid:ForceMeasuringDevice ,
                                                    fileid:DisplacementTransducer ,
                                                    fileid:TensileTestSpecimen ,
                                                    fileid:TensileTestingMachine ;
                             prov:generated fileid:Preload ,
                                            fileid:OriginalGaugeLength ,
                                            fileid:TestingRate ;
                            prov:wasInfluencedBy fileid:SamplePreparatation .

fileid:TensileTestingMachine rdf:type prov:Agent, prov:Entity ;
                             prov:atLocation fileid:TestingLab .

fileid:ForceMeasuringDevice rdf:type prov:Agent, prov:Entity ;
                            prov:atLocation fileid:TestingLab .

fileid:DisplacementTransducer rdf:type prov:Agent , prov:Entity ;
                              prov:atLocation fileid:TestingLab .

fileid:TestingRate rdf:type prov:Entity ;
                   prov:wasAttributedTo fileid:TensileTestingMachine .

fileid:Preload rdf:type prov:Entity ;
               prov:wasAttributedTo fileid:TensileTestingMachine .

fileid:OriginalGaugeLength rdf:type prov:Entity ;
                           prov:wasAttributedTo fileid:DisplacementTransducer .


# Describe the experiment and its data produced by which device

fileid:dataset rdf:type prov:Entity .

fileid:TensileTestExperiment rdf:type prov:Activity ;
    prov:wasAssociatedWith fileid:Tester ;
    prov:used fileid:TensileTestSpecimen ,
              fileid:TensileTestingMachine ,
              fileid:ForceMeasuringDevice ,
              fileid:DisplacementTransducer ,
              fileid:TestingFacility ;
    prov:generated fileid:Extension ,
                   fileid:StandardForce ,
                   fileid:AbsoluteCrossheadTravel ,
                   fileid:Remark ,
                   fileid:TimeStamp ,
                   fileid:dataset ;
    prov:hadPlan fileid:TestStandard ;
    prov:wasInfluencedBy fileid:ExperimentPreparation .

fileid:AbsoluteCrossheadTravel rdf:type prov:Entity;
                               prov:wasDerivedFrom fileid:DisplacementTransducer .

fileid:StandardForce rdf:type prov:Entity ;
                     prov:wasDerivedFrom fileid:ForceMeasuringDevice .

fileid:Extension rdf:type prov:Entity ;
                 prov:wasDerivedFrom fileid:DisplacementTransducer .

fileid:TestingStandard rdf:type prov:Plan .
```
</Details>
</blockquote>

Let us take the following snippet from the additional triples:
```{turtle}
fileid:SamplePreparatation rdf:type prov:Activity ;
                           prov:wasAssociatedWith fileid:TensileTestSpecimen ,
                                                  fileid:Material ;
                           prov:generated fileid:ParallelLength ,
                                          fileid:SpecimenThickness ,
                                          fileid:SpecimenType ,
                                          fileid:SpecimenWidth ;
                           prov:wasInfluencedBy fileid:Project .
```

The concepts of the parallel length, speciment thickness, specimen type and specimen width will be generated from the mappings while extracting the values from the CSV file. These individuals then will be set into context of a new individual called `fileid:SpecimenPreparation` of type `prov:Activity`. Additionally, we state that this is associated with the `TensileTestSpecimen` and `Material` individual.

Please note that all of the IRIs which will be generated from the pipeline will start with the `fileid:` prefix. This prefix is a placeholder with the value `http://abox-namespace-placeholder.org/` and will be replaced with the actual namespace in the pipeline, which has been defined in the pipeline configuration (see `base_url` in the [`Running the pipeline`](#running-the-pipeline) section). The suffix of the IRIs with the respective prefix are matching the suffixes of the IRIs in the mappings defined above.

For example, the concept with the key `Probentyp` and the IRI of `https://w3id.org/abox/SpecimenType` will have a suffix with `SpecimenType` and has a related IRI in the `additional_triples` with the value of `http://abox-namespace-placeholder.org/SpecimenType` as placeholder. When we assign a `base_iri` of e.g. `https://example.org/123` during the pipeline run, the resulting IRI will be `https://example.org/123/SpecimenType`.
The placeholder in the additional triples will be then replace with the actual namespace during the pipeline run.

In case if there are the same IRI mapped to multiple keys in the data file, the might be a conflict in the generated RDF, since there only one IRI can be mapped to a key in the data file. In such cases, we are able to provide an additional parameter `suffix` in the mapping, which is giving us the opportunity to assign the same IRI to different keys in the data file, but with a different suffix:

```{json}
{
    "key": "Probentyp",
    "iri": "https://w3id.org/steel/ProcessOntology/SpecimenType",
    "suffix": "ProbenArt"
}
```

When we assign a `base_iri` of e.g. `https://example.org/123`, the resulting IRI will be `https://example.org/123/ProbenArt` and the placeholder in the additional triples will need to have the value of `http://abox-namespace-placeholder.org/ProbenArt` as placeholder.

## Next steps

Please refer to the next sections for investigating more pipeline usecases or go to the [Run pipeline and retrieve outputs](3_pipeline_run_and_outputs) section for more details how to run the pipeline with the given setup.


## Running the pipeline


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

## The outputs

The pipeline run was succuessful, when no error has occured. If there are any missmatches in the mapping, the pipeline will raise it as a warning.

The pipeline will deliver you the following outputs:

* `graph`: the generated RDF graph
* `plain_metadata`: the plain values of the metadata of the experiment
* `time_series`: the plain time series of the experiment
* `time_series_metadata`: the metadata of the time series

### The RDF graph

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

#### Data graph

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


#### Method graph

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

### The general metadata

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

### The plain metadata

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

### The time series metadata

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


### The time series data

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
