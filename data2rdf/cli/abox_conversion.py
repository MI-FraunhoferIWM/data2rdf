import argparse
import os

from data2rdf.abox_template_generation import ABoxScaffoldPipeline
from data2rdf.pipeline_logging import set_global_logger


def run_abox_pipeline_for_folder(top_folder):
    filepath = os.path.join(top_folder, "conversion.log")
    set_global_logger(filepath)

    for file in os.listdir(top_folder):
        if ".xml" in file:
            file_path = os.path.join(top_folder, file)
            pipeline = ABoxScaffoldPipeline(file_path)
            pipeline.create_output_next_to_file()


def terminal():
    parser = argparse.ArgumentParser(
        description="Convert all .xml file into .ttl files."
    )

    parser.add_argument(
        "-f",
        "--folder_path",
        help="Path of the folder with the xml files",
        required=True,
    )

    args = parser.parse_args()

    run_abox_pipeline_for_folder(args.folder_path)


if __name__ == "__main__":
    terminal()
