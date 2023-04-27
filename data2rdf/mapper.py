import os
from string import Template

import pandas as pd
from openpyxl.styles import Font
from rdflib import Graph, URIRef
from rdflib.namespace import OWL, RDFS, SKOS

from data2rdf.annotation_confs import annotations

# from data2rdf.key_map_prediction import prediction_key_map_based_on_db


def merge_same_as_individuals(graph, convert_data_label_to_alt_label=True):
    """
    The mapper creates an OWL.sameAs relation between the data individuals and the method individuals.
    In some cases it is better to merge the individuals into one. This makes it simpler to navigate the graph.
    The merging is done by copying all relation from and to the data individuals onto the representative method individual.

    Explanation: In the mat-o-lab pipeline the data and method individuals are separated, however this makes the generated graph rather difficult to navigate.


    Example:
    Input:
    >>>
    fileid:column-0 a ns3:DataInstance ;
        rdfs:label "Force" ;
        ns11:EMMO_67fc0a36_8dcb_4ffa_9a43_31074efa3296 fileid:unit-0,
            fileid:unitliteral-0 ;
        owl:sameAs sdi:TimeSeries_X_Individual .

    sdi:TimeSeries_X_Individual a owl:NamedIndividual ;
        rdfs:label "TimeSeries_X_Individual" .
    <<<

    Output:
    >>>
    sdi:TimeSeries_X_Individual a ns3:DataInstance,
        owl:NamedIndividual ;
    rdfs:label "TimeSeries_X_Individual" ;
    ns11:EMMO_67fc0a36_8dcb_4ffa_9a43_31074efa3296 fileid:unit-0,
        fileid:unitliteral-0 ;
    ns6:altLabel "Force" .
    <<<

    Args:
        graph (rdflib.Graph): The graph to convert
        convert_data_label_to_alt_label (bool): To avoid two RDFS.label for the method individual it is convenient to change the data label to SKOS.altLabel
    """

    for data_individual, p, method_individual in graph.triples(
        (None, OWL.sameAs, None)
    ):
        # transfer all ingoing relations from data to method
        for s, p, _o in graph.triples((None, None, data_individual)):
            graph.add((s, p, method_individual))
            graph.remove((s, p, data_individual))

        # transfer all outgoing triples from data to method
        for _s, p, o in graph.triples((data_individual, None, None)):
            # the data label is used as altLabel for the method individual
            if convert_data_label_to_alt_label:
                if p == RDFS.label:
                    p = SKOS.altLabel

            if p != OWL.sameAs:  # avoid sameAs pointing to itself
                graph.add((method_individual, p, o))
            graph.remove((data_individual, p, o))

    return graph


def assign_namespace(entity, namespace_mapping_dict):
    """
    Generates new entity with extended namespace
    If no namespace is defeined return the same entity

    Args:
        entity (str): prefix:relation
        namespace_mapping_dict (str): dict with prefix as key and namespace as value

    Returns:

        new_entity: (str): namespace#relation

    """
    if ":" in entity:
        namespace = entity.split(":")[0]
        relation = entity.split(":")[1]
        new_entity = f"{namespace_mapping_dict[namespace]}{relation}"
        return new_entity
    else:
        return entity


def mapping_file2df(mapping_file, worksheet):
    """
    Generates a dataframe from the mapping file.
    Assigns the prefixes to the relations

    Args:
        mapping_file (str): Path to the mapping file (xlsx)

    Returns:

        df: (pd.DataFrame): Dataframe with assigned prefixes

    """

    df = pd.read_excel(
        open(mapping_file, "rb"), sheet_name=worksheet, engine="openpyxl"
    )

    namespace_mapping_df = df.loc[:, ["Prefixes", "Namespaces"]]
    namespace_mapping_df = namespace_mapping_df.dropna()

    namespace_mapping_df = namespace_mapping_df.set_index(
        "Prefixes", drop=True
    )
    namespace_mapping_dict = namespace_mapping_df.to_dict()["Namespaces"]

    mapping_df = df.loc[
        :, ["Data Individual Labels", "Relations", "Method Individual Class"]
    ]
    mapping_df = mapping_df.dropna()

    mapping_df = mapping_df.applymap(
        lambda x: assign_namespace(x, namespace_mapping_dict)
    )

    return mapping_df


def map_data2method(
    data_graph_file, method_graph_file, mapping_file, worksheet
):
    """
    Generates a Dataframe where the individuals of the data graph are mapped to
    the individuals of the method graph based on the mapping defined in the mapping file.
    The mapping of the data individuals is based on their label or their csvw title relation (rdfs:label|csvw:title).
    The mapping of the method graph is based on the class relation (rdf:type).

    Although the terms data graph and method graph are used this function can be
    used to match any two graphs with each other. Provided the mapping is given in the mapping_file.

    Note:
    1) A even more generic approach would allow to define the relations used for the mapping.
    2) Since data_graph_file, method_graph_file are only used to fetch the graphs, the mapping could also be adjusted to
    work on other sparql endpoints (e.g. for files that are already in a tripplestore)

    Args:
        data_graph_file (str): Path to the data graph (ttl)
        method_graph_file (str): Path to the method graph (ttl)
        mapping_file (str): Path to the mapping file (xlsx)
        worksheet (str): the worksheet in the mapping file that should be used for the mapping

    Returns:

        merged_mapping: (pd.DataFrame): Dataframe with mappings. Inner join of all data graph, method graph and mapping.

    """

    data_graph = Graph()
    data_graph.parse(data_graph_file, format="ttl")

    method_graph = Graph()
    method_graph.parse(method_graph_file, format="ttl")

    # mapping_df = mapping_file2df(mapping_file, worksheet)
    mapping_df = pd.read_excel(
        open(mapping_file, "rb"), sheet_name=worksheet, engine="openpyxl"
    )

    mapping_df = mapping_df.astype(str)  # merge needs same dtype

    # of the data graph
    # from the data we take only meta_data and column_data
    data_label_query_template = Template(
        """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX csvw: <http://www.w3.org/ns/csvw#>

    SELECT distinct ?ind ?label
    WHERE {
    {?ind rdf:type <$meta>} UNION {?ind rdf:type <$column>} .
    ?ind rdfs:label ?label
    }
    """
    )

    data_label_query = data_label_query_template.substitute(
        column=annotations["column_class"], meta=annotations["meta_data_type"]
    )

    # from the method we take all named individuals
    method_label_query = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX csvw: <http://www.w3.org/ns/csvw#>

    SELECT distinct ?ind ?label
    WHERE {
    ?ind rdf:type <http://www.w3.org/2002/07/owl#NamedIndividual> .
    ?ind rdfs:label ?label .
    filter(?ind != <http://www.w3.org/2002/07/owl#NamedIndividual>)
    }
    """

    # convert method query to df
    qres = method_graph.query(method_label_query)
    method_ind_df = pd.DataFrame(
        qres, columns=["Method Individuals", "Method Label Match"]
    )

    # literals can not be matched using pandas merge
    # method_ind_df = method_ind_df.astype(str)
    # Pandas version above 1.1.5 doesn't convert literals to string using astype properly
    method_ind_df = method_ind_df.applymap(str)

    # convert the data individuals and their labels to df
    qres = data_graph.query(data_label_query)
    data_ind_df = pd.DataFrame(
        qres, columns=["Data Individuals", "Data Label Match"]
    )

    # literals can not be matched using pandas merge
    # data_ind_df = data_ind_df.astype(str)
    # Pandas version above 1.1.5 doesn't convert literals to string using astype properly
    data_ind_df = data_ind_df.applymap(str)

    # use left join (left means the rows of the mapping file are preserved, see SQL join)
    # this allows to observe where the mapping is incomplete

    # merge mapping with data individuals
    merged_mapping = pd.merge(
        mapping_df, data_ind_df, how="left", on=["Data Label Match"]
    )

    # merge mapping with method individuals
    merged_mapping = pd.merge(
        merged_mapping, method_ind_df, how="left", on=["Method Label Match"]
    )

    return merged_mapping


def convert_mapping2graph(merged_mapping, mapping_output_file):
    """
    Converts the data frame with mappings to a graph and exports the serialization.

    Args:
        merged_mapping: (pd.DataFrame): DataFrame with mappings. Inner join of all data graph, method graph and mapping.
        mapping_output_file: (str): Path to the ttl file of the graph

    """

    # only the rows where the mapping worked are used
    merged_mapping_reduced = merged_mapping.dropna()

    # generate mapping graph (data individual -> relation -> method individual)
    mapping_graph = Graph()
    for _, mapping in merged_mapping_reduced.iterrows():
        mapping_graph.add(
            (
                URIRef(mapping["Data Individuals"]),
                OWL.sameAs,
                URIRef(mapping["Method Individuals"]),
            )
        )

    mapping_graph.serialize(mapping_output_file, format="ttl")


def create_mapping_template(
    data_graph_file, method_graph_file, mapping_output, worksheet="sameas"
):
    data_graph = Graph()
    data_graph.parse(data_graph_file, format="ttl")

    method_graph = Graph()
    method_graph.parse(method_graph_file, format="ttl")

    # from the data we take only meta_data and column_data
    data_label_query_template = Template(
        """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX csvw: <http://www.w3.org/ns/csvw#>

    SELECT distinct ?label
    WHERE {
    {?ind rdf:type <$meta>} UNION {?ind rdf:type <$column>} .
    ?ind rdfs:label ?label
    }
    """
    )

    data_label_query = data_label_query_template.substitute(
        column=annotations["column_class"], meta=annotations["meta_data_type"]
    )

    # from the method we take all named individuals
    method_class_query = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX csvw: <http://www.w3.org/ns/csvw#>

    SELECT distinct ?label
    WHERE {
    ?ind rdf:type <http://www.w3.org/2002/07/owl#NamedIndividual> .
    ?ind rdfs:label ?label .
    filter(?ind != <http://www.w3.org/2002/07/owl#NamedIndividual>)
    }
    """

    # convert method query to df
    qres = method_graph.query(method_class_query)
    method_ind_df = pd.DataFrame(qres, columns=["Method Labels"])
    method_ind_df = method_ind_df.astype(str)
    # literals can not be matched using pandas merge
    # method_ind_df.sort_values(by = "Method Labels", inplace=True)
    # convert the data individuals and their labels to df
    qres = data_graph.query(data_label_query)
    data_ind_df = pd.DataFrame(qres, columns=["Data Labels"])
    data_ind_df = data_ind_df.astype(
        str
    )  # literals can not be matched using pandas merge
    # data_ind_df.sort_values(by = "Data Labels", inplace=True)

    # merge options and choices
    match_table_df = pd.concat([method_ind_df, data_ind_df], axis=1)
    match_table_df.columns = ["Method Label Choice", "Data Label Choice"]
    # match_table_df.sort_values(by = ["Method Label Choice","Data Label Choice"], inplace=True)
    # print(match_table_df)

    for col in match_table_df:
        match_table_df[col] = match_table_df[col].sort_values(
            ignore_index=True
        )

    writer = pd.ExcelWriter(mapping_output, engine="openpyxl")
    match_table_df.to_excel(writer, sheet_name=worksheet, index=False)

    sheet = writer.sheets[worksheet]

    # add column header
    sheet["D1"] = "Data Label Match"
    sheet["D1"].font = Font(bold=True)
    sheet["C1"] = "Method Label Match"
    sheet["C1"].font = Font(bold=True)

    # end_choice = len(match_table_df.index) + 2

    for col in "ABCD":
        sheet.column_dimensions[col].width = 30

    writer.save()


# FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))
# TT_EXAMPLE_PATH = os.path.join(FOLDER_PATH, "tests/tensile_test_example_excel")

# FILE_PATH = os.path.join(TT_EXAMPLE_PATH,"AFZ1-Fz-S1Q.xlsm")
# LOCATION_MAPPING_FILE_PATH =
# os.path.join(TT_EXAMPLE_PATH,"location_mapping.xlsx") #the cell
# locations of meta data and column data in the excel file need to be
# supplied

# OUTPUT_PATH = os.path.join(TT_EXAMPLE_PATH,"AFZ1-Fz-S1Q.generic.xlsx")
# RDF_OUTPUT_PATH = os.path.join(TT_EXAMPLE_PATH,"AFZ1-Fz-S1Q.metadata.ttl")
# JSON_OUTPUT_PATH = os.path.join(TT_EXAMPLE_PATH,"AFZ1-Fz-S1Q.metadata.json")

# DATA_GRAPH_FILE_PATH_TTL_OUTPUT = os.path.join(TT_EXAMPLE_PATH,"AFZ1-Fz-S1Q.metadata.ttl")
# # FOLDER_PATH = os.path.dirname(os.path.abspath("__file__"))
# # TT_EXAMPLE_PATH = os.path.join(FOLDER_PATH, "tests", "tensile_test_example")
# # DATA_GRAPH_FILE_PATH_TTL_OUTPUT = os.path.join(TT_EXAMPLE_PATH,"DX56_D_FZ2_WR00_43.metadata.ttl")
# METHOD_GRAPH_FILE_PATH_OUTPUT = os.path.join(TT_EXAMPLE_PATH,"tensile_test_method_v6.ttl")

# MAPPING_FILE_PATH = os.path.join(TT_EXAMPLE_PATH,"AFZ1-Fz-S1Q_mapping_mod.xlsx")

# create_mapping_template(DATA_GRAPH_FILE_PATH_TTL_OUTPUT, METHOD_GRAPH_FILE_PATH_OUTPUT, MAPPING_FILE_PATH)


def report_merge_result(merged_mapping_df):
    """
    Report the number of successfully mapped data individuals.
    """

    data_count = merged_mapping_df["Data Label Choice"].dropna().count()
    mapping_count = len(merged_mapping_df.dropna())

    print(
        f"Of {data_count} data individuals, {mapping_count} were successfully mapped to the method. See the data.mapping-result.xlsx file for mapping results."
    )


class Mapper:
    def __init__(self, data_graph_path, method_graph_path, mapping_path):
        self.data_graph_path = data_graph_path
        self.method_graph_path = method_graph_path
        self.mapping_path = mapping_path

    def create_mapping_template(self, worksheet="sameas"):
        if os.path.isfile(self.mapping_path):
            raise FileExistsError(
                "Mapping file exists, use update_mapping_template to update the choices but keep matches"
            )

        create_mapping_template(
            self.data_graph_path,
            self.method_graph_path,
            self.mapping_path,
            worksheet,
        )

    def update_mapping_template(self, worksheet="sameas"):
        # if the mapping does not exist create it
        if not os.path.isfile(self.mapping_path):
            self.create_mapping_template()
            return True

        mappings_to_keep = pd.read_excel(
            open(self.mapping_path, "rb"),
            sheet_name=worksheet,
            engine="openpyxl",
        )

        create_mapping_template(
            self.data_graph_path,
            self.method_graph_path,
            self.mapping_path,
            worksheet,
        )
        # self.create_mapping_template()

        mappings_to_change = pd.read_excel(
            open(self.mapping_path, "rb"),
            sheet_name=worksheet,
            engine="openpyxl",
        )

        mappings_to_change.loc[
            :, ["Method Label Match", "Data Label Match"]
        ] = mappings_to_keep.loc[:, ["Method Label Match", "Data Label Match"]]

        writer = pd.ExcelWriter(self.mapping_path, engine="openpyxl")
        mappings_to_change.to_excel(writer, sheet_name=worksheet, index=False)

        sheet = writer.sheets[worksheet]

        for col in "ABCD":
            sheet.column_dimensions[col].width = 30

        writer.save()

    #   def predict_mapping(self, prediction_path, key_map_db, worksheet="sameas"):
    #      prediction_key_map_based_on_db(
    #           self.mapping_path, prediction_path, key_map_db, worksheet
    #      )

    def map_data_and_abox(self, worksheet="sameas"):
        self.merged_mapping_df = map_data2method(
            self.data_graph_path,
            self.method_graph_path,
            self.mapping_path,
            worksheet,
        )
        report_merge_result(self.merged_mapping_df)

    def export_merged_mapping_table(self, output_file):
        self.merged_mapping_df.to_excel(
            output_file, sheet_name="data2method-mapping"
        )

    def export_mapping_as_ttl(self, output_file):
        convert_mapping2graph(self.merged_mapping_df, output_file)
