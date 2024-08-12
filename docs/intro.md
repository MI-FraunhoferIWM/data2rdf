# Data2RDF

## In a nutshell

Breaking this package down to the basic functionalities, one can describe it with the following bulletpoints:

**With _Data2RDF_ we want to...**

* express information available as:

    * metadata (key-value-pairs)
    * metadata of time series (tabular data)

    ... from a data source (file or Python-`dict`) into **OWL/RDF**.

* parse the metadata and time series of this data source and make it available to other 3rd party software for further data storage and processing.

* express the SI-units of certain quantities through the **QUDT** ontology.

**For the _OWL/RDFS_ generation we consider**:

* to express the content of the data file/ Python `dict` in a dedicated subgraph (called _data graph_ here) using established ontologies (like **PROVO** or **CSVW** ). This _data graph_ is created on the fly while parsing the data source

* to add additional information about the dataset on top of this _data graph_ by adding further triples and using an ontology of your choice (called _method graph_ here).

**For this RDF generation we need ...**

* either a file in the following media types:
    * csv/tsv
    * json
    * xlsx/xls
    * Python-`dict`

* a curated ontology or vocabulary with OWL/RDFS classes describing the concepts in our metadata source

* need a 1:1 mapping of value locations (metadata and/or time series) for the creation of the _data graph_ (explained above).

* optionally a mapping for the SI-Units of the individually mapped concepts, either coming from a certain location in the file or by leaving a statement of a IRI (e.g. **qudt**)

* optionally an OWL/RDF with additional triples for the _method graph_ (explained above).



## Limitations (Read before using the pipeline !)

- The pipeline can only convert data that can be parsed by the provided parsers. The parsers currently support xlsx/xls, csv/tsv, json and Python `dict` objects.
- We consider that only one dataset is expressed through the resulting OWL/RDFS of pipeline. Hence, if you have multiple datasets stored in one file, you would need to either split up the file or run the pipeline multiple times over this file with multiple mappings.


## Installation

### From source

- `git clone git@github.com/MI-FraunhoferIWM/data2rdf`
- `cd data2rdf`
- `pip install .`

### From pypi

```
pip install data2rdf
```

## Improvements

If there is something unclear in this docs please provide feedback using [the GitHub issue system](https://github.com/MI-FraunhoferIWM/data2rdf/issues).
