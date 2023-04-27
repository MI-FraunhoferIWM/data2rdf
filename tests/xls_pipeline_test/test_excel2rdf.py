import os
import shutil
import unittest

from data2rdf.annotation_pipeline import AnnotationPipeline

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

mapping_file = os.path.join(working_folder, "mapping", "mapping.xlsx")
raw_data = os.path.join(working_folder, "data", "AFZ1-Fz-S1Q.xlsm")
location_mapping = os.path.join(
    working_folder, "mapping", "location_mapping.xlsx"
)

parser = "excel"
parser_args = {
    "location_mapping_f_path": location_mapping,
}

pipeline = AnnotationPipeline(
    raw_data,
    parser,
    parser_args,
    template,
    mapping_file,
    output_folder,
    base_iri="http://www.test4.de",
)


class TestAnnotationPipelineExcel(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
