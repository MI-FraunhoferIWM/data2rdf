import os
from enum import Enum
from pathlib import Path

from rdflib import Graph

from data2rdf.config import Config
from data2rdf.csv_parser import CSVParser
from data2rdf.excel_parser import ExcelParser

parser = Enum(
    "Parser",
    {
        "csv": CSVParser,
        "excel": ExcelParser,
    },
)

from pydantic import BaseModel


class AnnotationPipeline(BaseModel):

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
