# CSV file without metadata and with missing values

```{note}
Please follow [this link here](https://github.com/MI-FraunhoferIWM/data2rdf/blob/b29be66cb57beef8bd8f84e2cd588ccb8e17559c/examples/5_csv_w_na.ipynb) in order to access the related jupyter notebook.
```

## General understanding

In comparision to the [previous example of the csv file without metadata](1.4_csv_wo_metadata.md), we are using the similar data again, but now we have some missing values in the time series. Again, there will be no metadata in this case.

## The inputs

For this example, we will consider the following inputs:

* the csv file produced to be parsed
* the mapping for describing the data in RDF
* the parser arguments telling the pipeline that we do not have any metadata in the file and that we have missing values in the time series.


### The raw data

For this example, we will consider the following input data:

```
Temperature[°C];Coefficient of thermal exapansion[1/K];Specific heat[J/kgK];Young's modulus[Pa];Poison's ratio[-];Thermal conductivity[W/mK];Density[kg/m3]
20;8.70E-06;8.46E+02;7.47E+10;0.218;0.99;2.47E+03
100;9.00E-06;8.70E+02;7.43E+10;0.223;1.06;
200;9.20E-06;9.00E+02;7.34E+10;0.232;1.15;
300;9.50E-06;9.35E+02;7.25E+10;0.241;1.23;
400;9.80E-06;9.77E+02;7.11E+10;0.251;1.32;
450;1.03E-05;1.03E+03;6.98E+10;0.258;;
460;1.05E-05;1.06E+03;6.94E+10;0.26;;
470;1.08E-05;1.13E+03;6.88E+10;0.262;;
490;1.15E-05;1.28E+03;6.78E+10;0.267;;
500;1.20E-05;1.36E+03;6.70E+10;0.269;1.4;
510;1.29E-05;1.42E+03;6.64E+10;0.275;;
520;1.40E-05;1.44E+03;6.55E+10;0.284;;
530;1.52E-05;1.45E+03;6.48E+10;0.295;;
543;1.80E-05;1.44E+03;6.36E+10;0.309;;
550;1.95E-05;1.43E+03;6.28E+10;0.316;1.45;
560;2.20E-05;1.42E+03;6.16E+10;0.326;;
570;2.40E-05;1.42E+03;6.01E+10;0.335;;
580;2.53E-05;1.41E+03;5.83E+10;0.343;;
590;2.62E-05;1.40E+03;5.66E+10;0.351;;
600;2.68E-05;1.40E+03;5.46E+10;0.359;1.49;
610;2.72E-05;1.40E+03;5.23E+10;0.366;;
635;2.76E-05;1.38E+03;4.60E+10;0.383;;
650;;;;;1.53;
670;2.78E-05;1.37E+03;3.80E+10;0.4;;
700;2.79E-05;1.36E+03;3.15E+10;0.414;1.58;
770;2.79E-05;1.35E+03;2.13E+10;0.438;;
800;2.80E-05;1.35E+03;1.86E+10;0.444;1.66;
900;2.80E-05;1.34E+03;1.26E+10;0.463;1.75;
1000;2.80E-05;1.34E+03;8.70E+09;0.476;1.83;
1100;2.80E-05;1.34E+03;6.00E+09;0.486;1.92;
1200;2.80E-05;1.34E+03;3.80E+09;0.494;2;
```

As you may have noticed, this csv file here strictly speaking does not feature any time series, but a data frame of different samples with multiple properties like Young's modulus, specific heat capacity, etc.
Since the data frame here is vertically oriented, we are considering not to transform the data values into RDF again.

Additionally, there are some missing values, which are marked with `;;` in the csv file. These locations need to be properly handled in the pipeline, since we do not want to drop these rows while parsing.

### The parser arguments

According to the condition of the csv parser, we need to take the following parser arguments into account:

* `time_series_sep`: the separator for the time series. In this case, it is a  `;`.
* `metadata_length`: the length of the metadata in the csv file. In this case, it is 0, since we do not have any metadata.
* `time_series_header_length`: the length of the header of the time series in the csv file. In this case, it is 1, since the time series start at the second row.
* `drop_na`: whether to drop the rows with missing values. In this case, it is `False`.

The according Python dict for the parser arguments would look like this:
```
parser_args = {
    "time_series_sep": ";",
    "metadata_length": 0,
    "time_series_header_length": 1,
    "drop_na": False
}
```

### The mapping

The **schema** of the mapping itself is very similar to the one of the [very first example](1_csv.md), but for different ontological classes and different keys this time:

```
[
  {
    "iri": "https://w3id.org/steel/ProcessOntology/ThermalExpansionCoefficient",
    "key": "Coefficient of thermal exapansion[1/K]",
    "unit": "https://qudt.org/vocab/unit/PERCENT-PER-K"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/MassDensity",
    "key": "Density[kg/m3]",
    "unit": "http://qudt.org/vocab/unit/KiloGM-PER-M3"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/PoissonRatio",
    "key": "Poison's ratio[-]",
    "unit": "https://qudt.org/vocab/unit/NUM"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/SpecificHeatCapacity",
    "key": "Specific heat[J/kgK]",
    "unit": "http://qudt.org/vocab/unit/J-PER-KiloGM-K"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/Temperature",
    "key": "Temperature[\u00b0C]",
    "unit": "https://qudt.org/vocab/unit/DEG_C"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/ThermalConductivity",
    "key": "Thermal conductivity[W/mK]",
    "unit": "http://qudt.org/vocab/unit/KiloW-PER-M-K"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/ModulusOfElasticity",
    "key": "Young's modulus[Pa]",
    "unit": "https://qudt.org/vocab/unit/PA"
  }
]
```

As you may notice, we need to specify the unit in the mappings here, since the related units in the keys of the csv file cannot be easily extracted by the current implemented of the pipeline.

## Running the pipeline

Please apply the mapping, addtional triples and the parser arguments to the pipeline configuration and run the pipeline in the following manner:

```
from data2rdf import Data2RDF, Parser

data = """Temperature[°C];Coefficient of thermal exapansion[1/K];Specific heat[J/kgK];Young's modulus[Pa];Poison's ratio[-];Thermal conductivity[W/mK];Density[kg/m3]
20;8.70E-06;8.46E+02;7.47E+10;0.218;0.99;2.47E+03
100;9.00E-06;8.70E+02;7.43E+10;0.223;1.06;
200;9.20E-06;9.00E+02;7.34E+10;0.232;1.15;
300;9.50E-06;9.35E+02;7.25E+10;0.241;1.23;
400;9.80E-06;9.77E+02;7.11E+10;0.251;1.32;
450;1.03E-05;1.03E+03;6.98E+10;0.258;;
460;1.05E-05;1.06E+03;6.94E+10;0.26;;
470;1.08E-05;1.13E+03;6.88E+10;0.262;;
490;1.15E-05;1.28E+03;6.78E+10;0.267;;
500;1.20E-05;1.36E+03;6.70E+10;0.269;1.4;
510;1.29E-05;1.42E+03;6.64E+10;0.275;;
520;1.40E-05;1.44E+03;6.55E+10;0.284;;
530;1.52E-05;1.45E+03;6.48E+10;0.295;;
543;1.80E-05;1.44E+03;6.36E+10;0.309;;
550;1.95E-05;1.43E+03;6.28E+10;0.316;1.45;
560;2.20E-05;1.42E+03;6.16E+10;0.326;;
570;2.40E-05;1.42E+03;6.01E+10;0.335;;
580;2.53E-05;1.41E+03;5.83E+10;0.343;;
590;2.62E-05;1.40E+03;5.66E+10;0.351;;
600;2.68E-05;1.40E+03;5.46E+10;0.359;1.49;
610;2.72E-05;1.40E+03;5.23E+10;0.366;;
635;2.76E-05;1.38E+03;4.60E+10;0.383;;
650;;;;;1.53;
670;2.78E-05;1.37E+03;3.80E+10;0.4;;
700;2.79E-05;1.36E+03;3.15E+10;0.414;1.58;
770;2.79E-05;1.35E+03;2.13E+10;0.438;;
800;2.80E-05;1.35E+03;1.86E+10;0.444;1.66;
900;2.80E-05;1.34E+03;1.26E+10;0.463;1.75;
1000;2.80E-05;1.34E+03;8.70E+09;0.476;1.83;
1100;2.80E-05;1.34E+03;6.00E+09;0.486;1.92;
1200;2.80E-05;1.34E+03;3.80E+09;0.494;2;
"""

mapping = [
  {
    "iri": "https://w3id.org/steel/ProcessOntology/ThermalExpansionCoefficient",
    "key": "Coefficient of thermal exapansion[1/K]",
    "unit": "https://qudt.org/vocab/unit/PERCENT-PER-K"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/MassDensity",
    "key": "Density[kg/m3]",
    "unit": "http://qudt.org/vocab/unit/KiloGM-PER-M3"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/PoissonRatio",
    "key": "Poison's ratio[-]",
    "unit": "https://qudt.org/vocab/unit/NUM"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/SpecificHeatCapacity",
    "key": "Specific heat[J/kgK]",
    "unit": "http://qudt.org/vocab/unit/J-PER-KiloGM-K"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/Temperature",
    "key": "Temperature[\u00b0C]",
    "unit": "https://qudt.org/vocab/unit/DEG_C"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/ThermalConductivity",
    "key": "Thermal conductivity[W/mK]",
    "unit": "http://qudt.org/vocab/unit/KiloW-PER-M-K"
  },
  {
    "iri": "https://w3id.org/steel/ProcessOntology/ModulusOfElasticity",
    "key": "Young's modulus[Pa]",
    "unit": "https://qudt.org/vocab/unit/PA"
  }
]

parser_args = {
    "time_series_sep": ";",
    "metadata_length": 0,
    "time_series_header_length": 1,
    "drop_na": False
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

fileid:MassDensity a <https://w3id.org/steel/ProcessOntology/MassDensity> ;
    qudt:hasUnit "http://qudt.org/vocab/unit/KiloGM-PER-M3"^^xsd:anyURI .

fileid:ModulusOfElasticity a <https://w3id.org/steel/ProcessOntology/ModulusOfElasticity> ;
    qudt:hasUnit "https://qudt.org/vocab/unit/PA"^^xsd:anyURI .

fileid:PoissonRatio a <https://w3id.org/steel/ProcessOntology/PoissonRatio> ;
    qudt:hasUnit "https://qudt.org/vocab/unit/NUM"^^xsd:anyURI .

fileid:SpecificHeatCapacity a <https://w3id.org/steel/ProcessOntology/SpecificHeatCapacity> ;
    qudt:hasUnit "http://qudt.org/vocab/unit/J-PER-KiloGM-K"^^xsd:anyURI .

fileid:Temperature a <https://w3id.org/steel/ProcessOntology/Temperature> ;
    qudt:hasUnit "https://qudt.org/vocab/unit/DEG_C"^^xsd:anyURI .

fileid:ThermalConductivity a <https://w3id.org/steel/ProcessOntology/ThermalConductivity> ;
    qudt:hasUnit "http://qudt.org/vocab/unit/KiloW-PER-M-K"^^xsd:anyURI .

fileid:ThermalExpansionCoefficient a <https://w3id.org/steel/ProcessOntology/ThermalExpansionCoefficient> ;
    qudt:hasUnit "https://qudt.org/vocab/unit/PERCENT-PER-K"^^xsd:anyURI .

fileid:tableGroup a csvw:TableGroup ;
    csvw:table [ a csvw:Table ;
            rdfs:label "Time series data" ;
            csvw:tableSchema [ a csvw:Schema ;
                    csvw:column [ a csvw:Column ;
                            qudt:quantity fileid:ThermalConductivity ;
                            csvw:titles "Thermal conductivity[W/mK]"^^xsd:string ;
                            foaf1:page [ a foaf1:Document ;
                                    dcterms:format "https://www.iana.org/assignments/media-types/application/json"^^xsd:anyURI ;
                                    dcterms:identifier "https://www.example.org/column-5"^^xsd:anyURI ;
                                    dcterms:type "http://purl.org/dc/terms/Dataset"^^xsd:anyURI ] ],
                        [ a csvw:Column ;
                            qudt:quantity fileid:SpecificHeatCapacity ;
                            csvw:titles "Specific heat[J/kgK]"^^xsd:string ;
                            foaf1:page [ a foaf1:Document ;
                                    dcterms:format "https://www.iana.org/assignments/media-types/application/json"^^xsd:anyURI ;
                                    dcterms:identifier "https://www.example.org/column-2"^^xsd:anyURI ;
                                    dcterms:type "http://purl.org/dc/terms/Dataset"^^xsd:anyURI ] ],
                        [ a csvw:Column ;
                            qudt:quantity fileid:PoissonRatio ;
                            csvw:titles "Poison's ratio[-]"^^xsd:string ;
                            foaf1:page [ a foaf1:Document ;
                                    dcterms:format "https://www.iana.org/assignments/media-types/application/json"^^xsd:anyURI ;
                                    dcterms:identifier "https://www.example.org/column-4"^^xsd:anyURI ;
                                    dcterms:type "http://purl.org/dc/terms/Dataset"^^xsd:anyURI ] ],
                        [ a csvw:Column ;
                            qudt:quantity fileid:Temperature ;
                            csvw:titles "Temperature[°C]"^^xsd:string ;
                            foaf1:page [ a foaf1:Document ;
                                    dcterms:format "https://www.iana.org/assignments/media-types/application/json"^^xsd:anyURI ;
                                    dcterms:identifier "https://www.example.org/column-0"^^xsd:anyURI ;
                                    dcterms:type "http://purl.org/dc/terms/Dataset"^^xsd:anyURI ] ],
                        [ a csvw:Column ;
                            qudt:quantity fileid:ThermalExpansionCoefficient ;
                            csvw:titles "Coefficient of thermal exapansion[1/K]"^^xsd:string ;
                            foaf1:page [ a foaf1:Document ;
                                    dcterms:format "https://www.iana.org/assignments/media-types/application/json"^^xsd:anyURI ;
                                    dcterms:identifier "https://www.example.org/column-1"^^xsd:anyURI ;
                                    dcterms:type "http://purl.org/dc/terms/Dataset"^^xsd:anyURI ] ],
                        [ a csvw:Column ;
                            qudt:quantity fileid:MassDensity ;
                            csvw:titles "Density[kg/m3]"^^xsd:string ;
                            foaf1:page [ a foaf1:Document ;
                                    dcterms:format "https://www.iana.org/assignments/media-types/application/json"^^xsd:anyURI ;
                                    dcterms:identifier "https://www.example.org/column-6"^^xsd:anyURI ;
                                    dcterms:type "http://purl.org/dc/terms/Dataset"^^xsd:anyURI ] ],
                        [ a csvw:Column ;
                            qudt:quantity fileid:ModulusOfElasticity ;
                            csvw:titles "Young's modulus[Pa]"^^xsd:string ;
                            foaf1:page [ a foaf1:Document ;
                                    dcterms:format "https://www.iana.org/assignments/media-types/application/json"^^xsd:anyURI ;
                                    dcterms:identifier "https://www.example.org/column-3"^^xsd:anyURI ;
                                    dcterms:type "http://purl.org/dc/terms/Dataset"^^xsd:anyURI ] ] ] ] .
```

</Details>
</blockQuote>



Again, you will be able to investigate the `general_metadata`, `plain_metadata`, `time_series_metadata` and `time_series` attributes in the same way as stated in the [first example](1_csv).
