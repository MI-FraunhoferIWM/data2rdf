# ABox generation from a CSV file

## General understanding

In this example, we want to transfor a csv file which encorporates stress/strain of the measurement and some metadata about the experiment into an RDF repesentation.

For this purpose, we are describing the **general metadata** of the experiment as well as the **metadata of the time series**.

```{note}
We do not target to transform the time series itself into RDF, since it usually includes several thousands of datums per column. Hence we would give a reference in the form of an URI which is is pointing to the location of the file (e.g. a route in a web API or a local system path).
```

## The input data

### The raw data

The csv file produced by the tensile test machine looks like this:

```
"Prüfinstitut"	"institute_1"
"Projektnummer"	"123456"
"Projektname"	"proj_name_1"
"Datum/Uhrzeit"	44335.4	""
"Maschinendaten"	"maschine_1"
"Kraftaufnehmer"	"Kraftaufnehmer_1"
"Wegaufnehmer"	"Wegaufnehmer_1"
"Prüfnorm"	"ISO-XX"
"Werkstoff"	"Werkstoff_1"
"Probentyp"	"Probentyp_1"
"Prüfer"	"abc"
"Probenkennung 2"	"Probentyp_2"
"Messlänge Standardweg"	80	"mm"
"Versuchslänge"	120	"mm"
"Probendicke"	1.55	"mm"
"Probenbreite"	20.04	"mm"
"Prüfgeschwindigkeit"	0.1	"mm/s"
"Vorkraft"	2	"MPa"
"Temperatur"	22	"°C"
"Bemerkung"	""
"Prüfzeit"	"Standardkraft"	"Traversenweg absolut"	"Standardweg"	"Breitenänderung"	"Dehnung"
"s"	"N"	"mm"	"mm"	"mm"	"mm"
0.902359827	0.576537916	0.261094396	0.767421407	0.950183725	0.035807567
0.440620562	0.989528723	0.983277189	0.765300358	0.83547718	0.86967659
0.534511863	0.174351389	0.964046052	0.908144146	0.196001376	0.777251975
0.077564232	0.483112915	0.043854329	0.235058804	0.162114934	0.17809479
0.747648914	0.563390673	0.791011895	0.851891125	0.133555843	0.150183086
0.290519566	0.50761779	0.251250803	0.339549835	0.581404705	0.18957134
0.94014275	0.019307096	0.000430385	0.334206988	0.796205038	0.284730471
0.02484182	0.498115846	0.116693561	0.991365858	0.913819806	0.938140356
...
```

The original file can be accessed [here](https://raw.githubusercontent.com/MI-FraunhoferIWM/data2rdf/f9e5adfe2c18dd0bd4887bc685459671b1fbb29a/tests/csv_pipeline_test/input/data/DX56_D_FZ2_WR00_43.TXT). Due to clarify reasons, we truncated the time series in this document here.

```{note}
We are strictly assuming that metadata is on top of the time series and has a the key-value-unit pattern. Therefore the metadata up to now needs to have a width of 2 to 3 columns. In the future, we may support extending the default width of the metadata, in case if we need to have a width of 4 or more columns, e.g. if there are be more concepts than just value and unit.
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
### The additional triples

In some cases, the content of the data file does not provide all of the information which which we would like to describe. For this purpose, we can add additional triples to the data graph. These triples are added to the data graph by using the _method graph_ which which we can provide as file, as a string with the direct content of this file, or as an RDFlib-Graph. For this example, the additional triples can be defined in the following way:

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

## Running the pipeline




```{python}
```
