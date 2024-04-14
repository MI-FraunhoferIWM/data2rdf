import os
import unittest

from data2rdf.csv_parser import CSVParser
from data2rdf.data2rdf.pipelines.annotation_pipeline import AnnotationPipeline

test_folder = os.path.dirname(os.path.abspath(__file__))
working_folder = os.path.join(test_folder, "input")

output_folder = os.path.join(test_folder, "output")

template = os.path.join(
    working_folder,
    "method-graph",
    "tensile_test_method_v6.mod.ttl",
)
mapping_file = os.path.join(
    working_folder, "mapping", "tensile_test_mapping.xlsx"
)
raw_data = os.path.join(working_folder, "data", "DX56_D_FZ2_WR00_43.TXT")
expected = os.path.join(output_folder, "output_csv_parser.ttl")

parser = "csv"
parser_args = {"header_sep": "\t", "column_sep": "\t", "header_length": 20}


class TestAnnotationPipelineCSV(unittest.TestCase):
    def setUp(self):
        self.pipeline = AnnotationPipeline(
            raw_data,
            parser,
            parser_args,
            mapping_file,
            output_folder,
            template=template,
        )

        self.pipeline.run_pipeline()

    # TODO: update test
