import os
import shutil
import unittest

from data2rdf.annotation_pipeline import AnnotationPipeline
from data2rdf.csv_parser import CSVParser

from .test_utils import check_file_identifier_in_folder

test_folder = os.path.dirname(os.path.abspath(__file__))
working_folder = os.path.join(test_folder, "input")

output_folder = os.path.join(test_folder, "output")

template = os.path.join(
    working_folder,
    "method-graph",
    "tensile_test_method_v6",
    "tensile_test_method_v6.mod.ttl",
)
mapping_file = os.path.join(
    working_folder, "mapping", "tensile_test_mapping.xlsx"
)
raw_data = os.path.join(working_folder, "data", "DX56_D_FZ2_WR00_43.TXT")

parser = "csv"
parser_args = {"header_sep": "\t", "column_sep": "\t", "header_length": 20}


class TestAnnotationPipelineCSV(unittest.TestCase):
    def setUp(self):
        self.pipeline = AnnotationPipeline(
            raw_data,
            parser,
            parser_args,
            template,
            mapping_file,
            output_folder,
        )

        shutil.rmtree(output_folder, ignore_errors=True)

        self.pipeline.run_pipeline()

    def test_file_exist(self):
        self.assertTrue(
            check_file_identifier_in_folder(self.pipeline.output, "abox.ttl")
        )
        self.assertTrue(
            check_file_identifier_in_folder(
                self.pipeline.output, "generic.xlsx"
            )
        )
        self.assertTrue(
            check_file_identifier_in_folder(
                self.pipeline.output, "mapping.ttl"
            )
        )
        self.assertTrue(
            check_file_identifier_in_folder(
                self.pipeline.output, "datastorage.hdf5"
            )
        )
        self.assertTrue(
            check_file_identifier_in_folder(
                self.pipeline.output, "metadata.ttl"
            )
        )


class TestCSVParser(unittest.TestCase):
    def setUp(self):
        self.parser = CSVParser(
            raw_data,
            header_sep="\t",
            column_sep="\t",
            header_length=20,
        )

        self.parser.parser_data()

    def test_basic_run(self):
        self.assertTrue(hasattr(self.parser, "file_meta_df"))
        self.assertTrue(hasattr(self.parser, "column_df"))
        self.assertTrue(hasattr(self.parser, "meta_df"))

    def test_dfs(self):
        self.assertFalse(self.parser.file_meta_df.empty)
        self.assertFalse(self.parser.column_df.empty)
        self.assertFalse(self.parser.meta_df.empty)


if __name__ == "__main__":
    unittest.main()
