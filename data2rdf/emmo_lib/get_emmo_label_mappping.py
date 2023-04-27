import pandas as pd
from rdflib import Graph
from rdflib.namespace import SKOS

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)


def get_emmo_label_mapping(
    emmo_ontology="https://emmo-repo.github.io/versions/1.0.0-alpha2/emmo.ttl",
):
    g = Graph()
    g.parse(emmo_ontology, format="ttl")

    # get mapping between emmo labels and class/relation uris
    label_map = list(g.triples((None, SKOS.prefLabel, None)))
    df = pd.DataFrame(label_map, columns=["uris", "relation", "skos label"])
    df["name"] = df["uris"].apply(lambda x: x.split("#")[1])
    # otherwise pandas stores them in the natice rdflib datatype
    df = df.astype(str)

    print(df)


df = get_emmo_label_mapping()
