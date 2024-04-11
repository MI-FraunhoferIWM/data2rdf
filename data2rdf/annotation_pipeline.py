import os
from pathlib import Path

import pandas as pd
from rdflib import Graph

from data2rdf.abox_template_generation import convert_abox_namespace
from data2rdf.config import config
from data2rdf.csv_parser import CSVParser
from data2rdf.excel_parser import ExcelParser
from data2rdf.rdf_generation import RDFGenerator

parser_choice = {
    "csv": CSVParser,
    "excel": ExcelParser,
}


class AnnotationPipeline:

    """
    Generates an output folder and runs the complete data2rdf pipeline.
    The mapping is updated. Hence the already created mapping is kept, only the mapping choices are renewed.

    Attributes:
        input_file (str): The file path for the file used as input for the pipeline. Must be a file that can be processed with the provided parser (e.g. csv / excel).
        parser(str): The parser used to read the meta data and column data from the file (csv or excel).
        parser_args(dict): A dict with specific arguments for the parser. Is passed to the parser as kwargs.
        mapping_file(str): The file path for the mapping_file (in .xlsx excel format).
        output(str): The path for the output folder. This is where all the output files will be stored. The folder will be created.
        template(str, optional): The file path for the abox template (in .ttl format).
        base_iri(str): An iri used as base for the generated graph entities. The base will be extended by an automatically generated uuid such as: base_iri/uuid#entity
        mapping_db(str, optional): The file path for a mapping database. Can be used to predict possible mappings based on the mapping_file
        only_use_base_iri (bool): In some cases it is not good to automatically add an UUID to the iri. E.g. mapping of the iri to the generated file IDs of the DSMS.
        data_download_iri (str): Download location of the columns. E.g.: https://127.0.0.1/id. This will be added as downloadURL to the created columns. This url can than be used to serve the columns e.g. as json. The DSMS rest-api uses this url.
    """

    def __init__(
        self,
        input_file,
        parser,
        parser_args,
        mapping_file,
        output,
        template=None,
        mapping_db=None,
        base_iri=config.base_iri,
        only_use_base_iri=True,
        data_download_iri=None,
    ):
        self.input_file = input_file

        self.parser = parser_choice[parser]
        self.parser_args = parser_args
        # set base
        # iri for
        # the parsed
        # meta data
        self.parser_args["namespace"] = base_iri

        self.template = template
        self.mapping_file = mapping_file
        self.output = output

        self.base_iri = base_iri
        self.mapping_db = mapping_db
        self.only_use_base_iri = only_use_base_iri
        self.data_download_iri = data_download_iri

    def create_output(self):
        """
        Generates an output folder (will overwrite existing folders) and paths
        for the output files. All files are generated in the
        output folder.
        """
        os.makedirs(self.output, exist_ok=True)

        self.input_file_name = Path(self.input_file).stem
        self.generic_output = os.path.join(
            self.output, f"{self.input_file_name}.generic.xlsx"
        )
        self.data_storage_path = os.path.join(
            self.output, f"{self.input_file_name}.datastorage.hdf5"
        )
        self.data_graph = os.path.join(
            self.output, f"{self.input_file_name}.metadata.ttl"
        )

        self.mapping_prediction = os.path.join(
            self.output, f"{self.input_file_name}.predicted-mapping.csv"
        )

        self.unique_abox_template = os.path.join(
            self.output, f"{self.input_file_name}.abox.ttl"
        )

    def parse_data(self):
        """
        Parses the data using the provided parser class (csv or excel) and its kwargs.
        Stores the generic data description (file data, meta data, column data) as excel.
        Also stores the bulk data (time series) as a HDF file.
        The columns in the HDF5 file are related to the column data in the excel file and can be used to
        extract the data from the HDF5 file.
        """

        self.parser = self.parser(
            self.input_file,
            data_storage_path=self.data_storage_path,
            **self.parser_args,
        )

        self.parser.parser_data()
        self.parser.generate_excel_spreadsheet(self.generic_output)
        self.parser.generate_data_storage()

    def generate_file_uri(self):
        """Get the file uri to be used as prefix in the knowledge graph."""
        file_meta_df = pd.read_excel(
            self.generic_output, sheet_name="file", engine="openpyxl"
        )
        file_meta_df.set_index("index", inplace=True)

        if self.only_use_base_iri:
            self.file_uri = file_meta_df.loc["namespace", "value"] + "/"
        else:
            self.file_uri = (
                "/".join(
                    [
                        file_meta_df.loc["namespace", "value"],
                        file_meta_df.loc["uuid", "value"],
                    ]
                )
                + "#"
            )

    def write_rdf(self):
        """
        Generates a RDF graph representation of the parsed data. This graph uses a generic data model.
        Each meta data point and column creates one OWL individual.
        The quantities are described using EMMO and EMMO units.
        The graph itself is not yet interoperable. It is only a conversion of the data to RDF.
        Interoperability is achieved when the created individuals are mapped to
        individuals of the process graph (created with the abox template).
        """

        self.writer = RDFGenerator(
            self.generic_output,
            self.mapping_file,
            self.file_uri,
            self.data_download_iri,
        )

        self.writer.generate_file_json()
        self.writer.generate_meta_json()
        self.writer.generate_column_json()

        self.writer.to_ttl(self.data_graph)

    def convert_abox_template(self):
        """
        Converts the abox template to the process graph. This means, that the individuals describing the
        process in general are converted into unique individuals representing the specific process. This is simply
        achieved by changing the namespace to a unique namespace.
        """

        convert_abox_namespace(
            self.template, self.unique_abox_template, unique_uri=self.file_uri
        )

    def run_pipeline(self):
        """
        Runs the complete pipeline with all required steps.
        """

        self.create_output()
        self.parse_data()
        self.generate_file_uri()
        self.write_rdf()
        if self.template:
            self.convert_abox_template()

    def export_graph(self):
        """
        Exports a merged rdflib graph of the data, process and mapping output.
        Can be used e.g. to load the data into a triple store using rdflib.
        """

        g = Graph(identifier=self.base_iri)
        if self.template:
            g.parse(self.unique_abox_template, format="ttl")
        g.parse(self.data_graph, format="ttl")

        return g

    def export_ttl(self, f_path):
        """
        Exports a merged .ttl file graph of the data, process and mapping output.
        Can be used e.g. to load the data into a triple store using the stores file upload functionality
        (e.g. AllegroGraph).
        """

        g = self.export_graph()
        g.serialize(f_path, format="ttl")
