import os

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
expected = os.path.join(output_folder, "output_pipeline.ttl")

parser_args = {"header_sep": "\t", "column_sep": "\t", "header_length": 20}


def test_csv_pipeline() -> None:
    from data2rdf import AnnotationPipeline

    pipeline = AnnotationPipeline(
        raw_data=raw_data,
        mapping=mapping_file,
        parser="csv",
        parser_args=parser_args,
        extra_triples=template,
    )
