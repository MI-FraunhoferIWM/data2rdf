import os
import shutil
import unittest

from data2rdf.cli.abox_conversion import run_abox_pipeline_for_folder

from .test_utils import check_file_identifier_in_folder

test_folder = os.path.dirname(os.path.abspath(__file__))
abox_folder_path = os.path.join(test_folder, "input", "method-graph")
output_folder = os.path.join(abox_folder_path, "tensile_test_method_v6")


class TestAboxPipeline(unittest.TestCase):
    def setUp(self):
        shutil.rmtree(output_folder, ignore_errors=True)
        run_abox_pipeline_for_folder(abox_folder_path)

    def test_file_exist(self):
        self.assertTrue(
            check_file_identifier_in_folder(output_folder, ".mod.ttl")
        )
        self.assertTrue(
            check_file_identifier_in_folder(output_folder, ".mod.xml")
        )


if __name__ == "__main__":
    unittest.main()
