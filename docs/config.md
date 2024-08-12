# The Data2RDF configuration


The configuration of the package is crucial for the correct parsing and transformation of the data into RDF. The configuration is done via a dictionary which is passed to the `Data2RDF` constructor. The configuration is used to define the base IRI for the individuals, the QUDT unit and quantity kinds, the separator used for the IRI, the encoding used for parsing etc. Below you can find a table with the keys and their corresponding data types, descriptions and default values.

| Key | Data Type | Description | Default Value | Required |
| --- | --- | --- | --- | --- |
| qudt_units | AnyUrl | URI to QUDT Unit ontology for unit conversion | http://qudt.org/2.1/vocab/unit | No |
| qudt_quantity_kinds | AnyUrl | URI to QUDT quantity kind ontology for unit conversion | http://qudt.org/vocab/quantitykind/ | No |
| base_iri | AnyUrl | Base IRI for individuals | https://www.example.org | No |
| prefix_name | str | Prefix used referencing the base_iri in the context of the graph | fileid | No |
| separator | str | Separator between base IRI and suffix | / | No |
| encoding | str | Encoding used while parsing | utf-8 | No |
| data_download_uri | AnyUrl | General base iri for downloading the time series after uploading | https://www.example.org/download | No |
| graph_identifier | Optional[str, AnyUrl] | Identifier of the graph to be produced | None | No |
| namespace_placeholder | Union[str, AnyUrl] | Placeholder of the extra triples to be replaced with the base_iri during the pipeline run | http://abox-namespace-placeholder.org/ | No |
| remove_from_unit | List[str] | Characters which should be removed from the input value for the unit | ["[", "]", '"', " "] | No |
| mapping_csv_separator | str | When the mapping file is a csv, the separator to be used for parsing | ; | No |
| remove_from_datafile | List[str] | In plain text parsers, e.g. the CSV-parser, there might be the need to remove certain characters when parsing | ['"', "\r", "\n"] | No |
| suppress_file_description | bool | In ABox mode, the pipeline is producing an additional subgraph graph for describing the data file in its structure, mime type, etc. This will be suppressed if enabled. | False | No |

```{python}
example_config = {
    "qudt_units": "http://qudt.org/2.1/vocab/unit",
    "qudt_quantity_kinds": "http://qudt.org/vocab/quantitykind/",
    "base_iri": "https://www.example.org",
    "prefix_name": "fileid",
    "separator": "/",
    "encoding": "utf-8",
    "data_download_uri": "https://www.example.org/download",
    "graph_identifier": None,
    "namespace_placeholder": "http://abox-namespace-placeholder.org/",
    "remove_from_unit": ["[", "]", '"', " "],
    "mapping_csv_separator": ";",
    "remove_from_datafile": ['"', "\r", "\n"],
    "suppress_file_description": False,
}
```
