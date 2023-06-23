import difflib

import pandas as pd
from rdflib import Graph
from rdflib.namespace import OWL, RDF, RDFS, SKOS
from sqlalchemy import create_engine

label_choice = [
    SKOS.altLabel,
    SKOS.prefLabel,
    RDFS.label,
]


def update_key_map_using_ontology(source, key_map_db):
    g = Graph()
    g.parse(source, format="turtle")

    key_map_df = pd.DataFrame()

    for s, _p, o in g.triples((None, RDF.type, OWL.Class)):
        onto_concept = str(s).split("#")[-1]

        for label in label_choice:
            for _s, _p, o in g.triples((s, label, None)):
                key_map = {"ontology_key": onto_concept, "data_key": o}
                key_map_df = key_map_df.append(key_map, ignore_index=True)

    engine = create_engine(f"sqlite:///{key_map_db}", echo=False)
    key_map_df.to_sql(con=engine, name="key_map", if_exists="append")

    # remove duplicated mappings
    df = pd.read_sql_table("key_map", con=engine, index_col="index")
    df = df.drop_duplicates()
    df = df.reset_index(drop=True)
    print(df)
    df.to_sql(con=engine, name="key_map", if_exists="replace")


def update_key_map_using_mapping(source, key_map_db, worksheet="sameas"):
    mappings = pd.read_excel(
        open(source, "rb"), sheet_name=worksheet, engine="openpyxl"
    )

    mappings = mappings.dropna()

    key_map_df = pd.DataFrame()
    key_map_df[["ontology_key", "data_key"]] = mappings[
        ["Method Label Match", "Data Label Match"]
    ]

    engine = create_engine(f"sqlite:///{key_map_db}", echo=False)
    key_map_df.to_sql(con=engine, name="key_map", if_exists="append")

    # remove dupliacted mappings
    df = pd.read_sql_table("key_map", con=engine, index_col="index")
    df = df.drop_duplicates()
    df = df.reset_index(drop=True)
    df.to_sql(con=engine, name="key_map", if_exists="replace")


def prediction_key_map_based_on_db(
    mapping_path, prediction_path, key_map_db, worksheet="sameas"
):
    engine = create_engine(f"sqlite:///{key_map_db}", echo=False)
    key_map_db = pd.read_sql_table("key_map", con=engine, index_col="index")

    mapping_choices = pd.read_excel(
        open(mapping_path, "rb"), sheet_name=worksheet, engine="openpyxl"
    )

    result_mapping_df = pd.DataFrame()

    for _, row in mapping_choices.iterrows():
        # go trough all possible data labels
        data_name = row["Data Label Choice"]

        if not isinstance(data_name, str):
            continue

        # get similarity of all data word with the db mapping pairs
        scores = key_map_db["data_key"].apply(
            lambda match_word: difflib.SequenceMatcher(
                None, data_name.lower(), match_word.lower()
            ).ratio()
        )
        best_score_idx = scores.idxmax()
        best_data_score = scores.max()
        best_scoring_data_name = key_map_db.loc[best_score_idx, "data_key"]

        # get all mapping pairs of the data match
        data_matches = key_map_db.loc[
            (key_map_db["data_key"] == best_scoring_data_name), :
        ]

        best_matches = pd.DataFrame()
        for _, row in data_matches.iterrows():
            method_name = row["ontology_key"]

            # print(method_name)

            method_choice = mapping_choices["Method Label Choice"].dropna()

            # get similarity of all method words with the possible method
            # choices
            scores = method_choice.apply(
                lambda match_word: difflib.SequenceMatcher(
                    None, method_name.lower(), match_word.lower()
                ).ratio()
            )

            best_score_idx = scores.idxmax()
            best_method_score = scores.max()

            best_scoring_method_choice = method_choice.loc[best_score_idx]

            best_scoring_method = {
                "method_match": method_name,
                "method_choice": best_scoring_method_choice,
                "score": best_method_score,
            }
            best_matches = best_matches.append(
                best_scoring_method, ignore_index=True
            )

        best_score_idx = best_matches["score"].idxmax()
        best_scoring_method_choice_name = best_matches.loc[
            best_score_idx, "method_choice"
        ]
        best_scoring_method_match_name = best_matches.loc[
            best_score_idx, "method_match"
        ]
        best_method_score = best_matches.loc[best_score_idx, "score"]

        result_mapping = {
            "Method Label Match": best_scoring_method_choice_name,
            "Data Label Match": data_name,
            "Method Mapping-DB Match": best_scoring_method_match_name,
            "Data Mapping-DB Match": best_scoring_data_name,
            "Method Score": best_method_score,
            "Data Score": best_data_score,
        }

        result_mapping_df = result_mapping_df.append(
            result_mapping, ignore_index=True
        )

    result_mapping_df.sort_values(
        by=["Method Score", "Data Score"], inplace=True, ascending=False
    )
    result_mapping_df = result_mapping_df[
        [
            "Data Label Match",
            "Method Label Match",
            "Data Mapping-DB Match",
            "Method Mapping-DB Match",
            "Data Score",
            "Method Score",
        ]
    ]
    result_mapping_df.to_csv(prediction_path)


# ontology_path = os.path.join("../tests/key_map_generation/stahl_digital_v23.09.2021.ttl")
# key_map_db = os.path.join("../tests/key_map_generation/key_map.db")
# example_mapping = os.path.join("../tests/key_map_generation/mapping.xlsx")
# prediction_path = os.path.join("../tests/key_map_generation/predicted_mapping.csv")

# update_key_map_using_mapping(example_mapping, key_map_db)
# update_key_map_using_ontology(ontology_path, key_map_db)
# prediction_key_map_based_on_db(example_mapping, prediction_path, key_map_db)
