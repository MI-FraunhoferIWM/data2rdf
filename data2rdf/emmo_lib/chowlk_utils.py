import re

import pandas as pd
from rdflib import Graph
from rdflib.namespace import SKOS

# pd.set_option('display.max_colwidth', None)  # or 199
# pd.set_option('display.max_columns', None)  # or 1000


def add_emmo_name_to_diagrams(
    input_file,
    output_file,
    emmo_ontology="https://emmo-repo.github.io/versions/1.0.0-alpha2/emmo.ttl",
):
    """
    EMMO uses non-human readable uris to identify concepts.
    This is hard to use when working with draw.io as input for Chowlk.

    The concepts however are described by the skos.prefLabel.
    Unfortunatly Chowlk requires the usage of the concept uri.

    This function allows the user to design an ontology using the skos.prefLabel.
    Just write the concept as:

    prefix:skos.prefLabel
    e.g.:
    holistic:hasParticipant

    Then convert the concepts to actual EMMO concepts.

    Args:
    INPUT_FILE (str): Path to input XML file. Create with Draw.io -> Export as -> XML (choose not compressed)
    OUTPUT_FILE (str): Path to the output XML file. The same draw.io file with replaced concept names.
    EMMO_ONTOLOGY (str): A path to the EMMO file to find the skos.prefLabel's. Default: https://emmo-repo.github.io/versions/1.0.0-alpha2/emmo.ttl

    """

    g = Graph()
    g.parse(emmo_ontology, format="ttl")

    # get mapping between emmo labels and class/relation uris
    label_map = list(g.triples((None, SKOS.prefLabel, None)))
    df = pd.DataFrame(
        label_map, columns=["class/relation uris", "relation", "label"]
    )
    df["class/relation names"] = df["class/relation uris"].apply(
        lambda x: x.split("#")[1]
    )
    # otherwise pandas stores them in the natice rdflib datatype
    df = df.astype(str)

    with open(input_file) as input_file:
        # extract all abc:xyz patterns from the draw.io xml
        text = input_file.read()
        entities = re.findall(
            "[A-Za-z0-9][A-Za-z0-9]*:[A-Za-z0-9][A-Za-z0-9]*", text
        )

        for entity in entities:
            skos_label = entity.split(":")[1]
            # prefix = entity.split(":")[0]
            # todo: Check for emmo prefix !

            # check if matching label can be found in EMMO
            if not df.loc[(df["label"] == skos_label), :].empty:
                individual_name = df.loc[
                    (df["label"] == skos_label), ["class/relation names"]
                ].values[0][0]

                # create new label and add to XML
                new_entity = "{}:{}".format(
                    entity.split(":")[0], individual_name
                )
                text = text.replace(entity, new_entity)

    # store new XML
    with open(output_file, "w") as output_file:
        output_file.write(text)


# INPUT_FILE = os.path.join("method_graph","tensile_test_method.xml")
# OUTPUT_FILE = os.path.join("method_graph","tensile_test_method_conv.xml")
# EMMO_ONTOLOGY = os.path.join("emmo","emmo.ttl")

# add_emmo_name_to_diagrams(INPUT_FILE, OUTPUT_FILE, EMMO_ONTOLOGY)

# TODO: Take care, that only EMMO namespaces are converted !!
