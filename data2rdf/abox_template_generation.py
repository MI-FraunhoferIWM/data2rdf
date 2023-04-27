import logging
import os
from pathlib import Path

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import OWL, RDF, RDFS, SKOS

from data2rdf.emmo_lib import chowlk_utils


def run_chowlk(inputfile, outputfile):
    from chowlk.transformations import transform_ontology
    from chowlk.utils import read_drawio_xml

    logging.info(
        f"Launching chowlk for transforming the ontology: {inputfile}"
    )

    root = read_drawio_xml(inputfile)
    ontology_turtle, ontology_xml, namespaces, errors = transform_ontology(
        root
    )

    with open(outputfile, mode="w") as file:
        file.write(ontology_turtle)
    logging.info(f"Writing chowlk output to path: {outputfile}")

    if errors:
        logging.info(f"Chowlk exited with the following errors: {errors}")


def convert_abox_namespace(
    abox_template_graph_file_input,
    abox_template_graph_file_output,
    unique_uri="http://test.org#",
    abox_method_tag="http://abox-namespace-placeholder.org/",
):
    # simple replace the namespace, did not work so far using rdflib
    with open(abox_template_graph_file_input) as input_file:
        file_text = input_file.read()
        new_file_text = file_text.replace(abox_method_tag, unique_uri)

    with open(abox_template_graph_file_output, "w") as output_file:
        output_file.write(new_file_text)


def add_abox_individuals_to_ontology(
    ontology_ttl_input,
    ontology_ttl_output,
    placeholder_namespace="http://abox-namespace-placeholder.org/",
):
    """
    Most ontologies only contain classes. In order to have individuals that can be used in the ontopanel workflow
    this function generates for each class an individual instance. It also adds the label of the class as label of the individual.
    """

    graph = Graph()
    graph.parse(ontology_ttl_input, format="ttl")

    for s, _p, _o in graph.triples((None, None, OWL.Class)):
        if "#" in str(
            s
        ):  # works for uri/name and uri#name -> adapt if other cases exist
            name = str(s).split("#")[-1]
        else:
            name = str(s).split("/")[-1]

        graph.add((URIRef(f"{placeholder_namespace}{name}"), RDF.type, s))

        for _s2, _p2, o2 in graph.triples((s, SKOS.prefLabel, None)):
            graph.add(
                (URIRef(f"{placeholder_namespace}{name}"), RDFS.label, o2)
            )

        for _s2, _p2, o2 in graph.triples((s, RDFS.label, None)):
            graph.add(
                (URIRef(f"{placeholder_namespace}{name}"), RDFS.label, o2)
            )

    graph.serialize(ontology_ttl_output, format="ttl")


# def add_class_labels_to_individuals(ontology_ttl_input, ontology_ttl_output):
#     """
#     In order to allow the development of abox templates using ontopanel it is crucial, that the individuals have meaningful
#     labels annotated with RDFS.label. This utility function adds the
#     """


# def add_uuid_to_individuals(
#     ABox_template_graph_file_input,
#     ABox_template_graph_file_output,
#     )

#     graph = Graph()
#     graph.parse(ABox_template_graph_file_input, format="ttl")

#     for s, p, o in graph.triples((None, None, OWL.NamedIndividual)):
#         label = str(s).split("#")[-1]
#         graph.add((s, RDFS.label, Literal(label)))


def add_individual_labels(
    abox_template_graph_file_input,
    abox_template_graph_file_output,
):
    graph = Graph()
    graph.parse(abox_template_graph_file_input, format="ttl")

    for s, _p, _o in graph.triples((None, None, OWL.NamedIndividual)):
        if "#" in str(
            s
        ):  # works for uri/name and uri#name -> adapt if other cases exist
            name = str(s).split("#")[-1]
        else:
            name = str(s).split("/")[-1]

        graph.add((s, RDFS.label, Literal(name)))

    graph.serialize(abox_template_graph_file_output, format="ttl")


def merge_graphs(graph_01, graph_02, merged_graph):
    """
    Merges both graphs into merged_graph
    """
    graph = Graph()
    graph.parse(graph_01, format="ttl")
    graph.parse(graph_02, format="ttl")
    graph.serialize(merged_graph, format="ttl")


class ABoxScaffoldPipeline:
    def __init__(
        self,
        xml_path,
        mod_xml_path=None,
        ttl_path=None,
    ):
        self.xml_path = xml_path
        self.mod_xml_path = mod_xml_path
        self.ttl_path = ttl_path

        self.base_file_name = Path(self.xml_path).stem

        # filename = pathlib.Path(self.xml_path).name

        # self.mod_xml_path = os.path.join(out_path, filename.replace(".xml",".mod.xml"))
        # self.ttl_path = os.path.join(out_path, filename.replace('.xml','.ttl'))
        # self.ttl_path_ns = os.path.join(out_path, filename.replace('.xml','.ns.ttl'))

    def xml_conversion(self):
        chowlk_utils.add_emmo_name_to_diagrams(
            self.xml_path, self.mod_xml_path
        )

    def run_chowlk(self):
        run_chowlk(self.mod_xml_path, self.ttl_path)

    def add_individual_labels(self):
        add_individual_labels(self.ttl_path, self.ttl_path)

    def change_namespace(self, ttl_path_ns, unique_uri="http://test.org#"):
        convert_abox_namespace(self.ttl_path, ttl_path_ns)

    def run_pipeline(self):
        try:
            self.xml_conversion()
        except Exception as e:
            logging.error(e, exc_info=True)

        try:
            self.run_chowlk()
        except Exception as e:
            logging.error(e, exc_info=True)

        try:
            self.add_individual_labels()
        except Exception as e:
            logging.error(e, exc_info=True)
        # self.change_namespace()python logging function wrapper

    def set_output_paths(self, output_folder):
        self.mod_xml_path = os.path.join(
            output_folder, self.base_file_name + ".mod.xml"
        )
        self.ttl_path = os.path.join(
            output_folder, self.base_file_name + ".mod.ttl"
        )

    def create_output_next_to_file(self):
        top_folder_path = os.path.dirname(os.path.abspath(self.xml_path))
        folder_path = os.path.join(top_folder_path, self.base_file_name)
        os.makedirs(folder_path, exist_ok=True)
        self.set_output_paths(folder_path)

        self.run_pipeline()


# FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))
# TT_EXAMPLE_PATH = os.path.join(FOLDER_PATH, "tests", "tensile_test_example")
# XML_FILE_PATH = os.path.join(TT_EXAMPLE_PATH,"tensile_test_method_v6.xml")
# OUTPUT_PATH = os.path.join(TT_EXAMPLE_PATH)

# abox_pipeline = ABoxScaffoldPipeline(XML_FILE_PATH, OUTPUT_PATH)
# abox_pipeline.run_pipeline()
