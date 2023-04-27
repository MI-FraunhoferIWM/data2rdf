# Intro

This pipeline allows for the conversion of different datasets into the RDF graph format. Currently supported formats are csv and excel.
The pipeline aims to convert all metadata (data about the dataset) into RDF. Additionally the actual data (e.g. time series of a measurement) is also made accessible. Therefore an OWL individual representing each measurement is created, that represents the actual data. The data itself is stored as HDF5.
The data stored in the HDF5 file can be accessed when the pipeline is used together with the DSMS (see [DSMS integration](./dsms-integration.md))

The workflow of the pipeline is shown in [Workflow](./workflow.md).

# Limitations (Read before using the pipeline !)

- The pipeline can only convert data that can be parsed by the provided parsers. The parsers currently support excel and csv.
- The data must be composed only of meta data and column data. Other more complex data types would require the development of an adapted parser.
- The data is converted into RDF using a data model build upon: dcat, owl, rdfs and EMMO (to define quantities) and the EMMO Data Model Ontology. However, it can be mapped to any other Ontology and is therefore not limited to EMMO.
- The pipeline only works with individual experiments. If you have multiple experiments stored in one file, they need to be split up and converted with the pipeline individually using a divide-and-conquer strategy. That means split each experiment in a file that can be parsed by the pipeline (csv or excel) and process it with the pipeline. Then connect the experiment e.g. using a SPARQL construct query or rdflib.
An example of this strategy is shown in <https://gitlab.cc-asp.fraunhofer.de/kupferdigital/rdf-pipelines/rp-hardness-test-bam/-/tree/main/dsms-profile>

# What does the user need to do to run the pipeline ?

The pipeline requires 3 inputs from the user:

- The dataset. See [Parser](./workflow.md#Parser) for a description of how the data must be structured.
- The abox template. See [ABox Template](./workflow.md#abox-skeleton) for a tutorial of how to generate this template.
- The mapping file. See [Mapper](./workflow.md#data-method-mapping) for a tutorial of how to generate the mapping.

This seems like a lot of work ! But keep in mind, that the abox template only needs to be created ones for a particular type of experiment and can then be reused for the same experiments. It can even be exchanged between excel and csv files.

The same applies for the mapping file. Ones an experiment with a specific naming convention is mapped to a method graph, experiments with the same naming convention can also be processed.
Furthermore, a database system is currently implemented, that collects all mappings and therefore can predict mappings for new datasets as well. See [Mapper](./workflow.md#data-method-mapping) for an example of the mapping prediction logic.

# Installation

Tested on Ubuntu machines.
Install in your git folder (or any folder you like).

- `git clone git@gitlab.cc-asp.fraunhofer.de:rdf-pipeline/data2rdf.git`
- `cd data2rdf`
- `git submodule update --init --recursive`
- `pip install .`

# Improvements

If there is something unclear in this docs please provide feedback using the issue system: [GitLab Issues](https://gitlab.cc-asp.fraunhofer.de/rdf-pipeline/data2rdf/-/issues)
