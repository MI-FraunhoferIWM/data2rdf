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

As you may see, the metadata of file _has a length of 22 rows_. The metadata itself is tab-separated, has the name of a concept in the first column (e.g.  `"Vorkraft"`=Preload), the value related to this metadatum in the second column (e.g. `"22"`) and optionally a unit in the third column (e.g. `"MPa"`).

Subsequently, there is the time series with a header which has a length of rows: one with a the concept name (e.g. `"Prüfzeit"`=Test time) columns and one with the respective unit again (e.g. `"s"`).



### The mapping

In order to transform the relevant metadata into an RDF for describing the data and the experiment, we **need a well formulated ontology with classes** describing each individual concept in the file.

Since we are **instanciating individuals for each single concept** in the data file and assign the respective SI units, we need to map the key of the concept to the IRI of an ontological class and also make a statement whether we want to read the SI unit from the file or map it manually.

For the quantitative properties (e.g. `"Vorkraft"`=Preload) and non-quantitative properties (.e.g `"Prüfer"`= Name of the tester) in the metadata of the file, we can assume the following mapping:

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

```{note}
We are using an ontology from the [*Stahldigital*](https://www.iwm.fraunhofer.de/de/warum-fraunhofer-iwm/loesungen-fuer-produktlebenzyklus/digitalisierung-in-der-werkstofftechnik/stahldigital.html) project (see [https://w3id.org/steel/ProcessOntology](https://w3id.org/steel/ProcessOntology)), in your usecase, it might be the case that you might need to establish your own ontology which describes your data set.
```

```{note}
You may notice that this mapping has to follow a certain schema in order to be valid. To be more precise, we have here a list of dictionaries with specifications for the mapping of a concept in the data file.

If you would like to read more about the schema and options for the mapping, please refer to the `Schema` chapter of this documentation.
```
