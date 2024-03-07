import pandas as pd
from rdflib import Graph
from rdflib.namespace import SKOS

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)


def get_qudt_label_mapping(
    qudt_ontology="https://github.com/qudt/qudt-public-repo/blob/main/vocab/unit/VOCAB_QUDT-UNITS-ALL-v2.1.ttl",
):
    g = Graph()
    g.parse(qudt_ontology, format="ttl")

    # get mapping between QUDT labels and class/relation URIs
    label_map = list(g.triples((None, SKOS.prefLabel, None)))
    df = pd.DataFrame(label_map, columns=["uris", "relation", "skos label"])

    df["name"] = df["uris"].apply(lambda x: x.rsplit("/", 1)[-1])
    # otherwise pandas stores them in the natice rdflib datatype
    df = df.astype(str)

    print(df)


df = get_qudt_label_mapping()
