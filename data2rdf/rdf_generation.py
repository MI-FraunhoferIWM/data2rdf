import json

import pandas as pd
from rdflib import Graph

from data2rdf.annotation_confs import annotations
from data2rdf.emmo_lib import emmo_utils


class RDFGenerator:

    """
    Transforms the generic excel sheet to RDF
    """

    def __init__(self, f_path, only_use_base_iri, data_download_iri):
        self.file_meta_df = pd.read_excel(
            f_path, sheet_name="file", engine="openpyxl"
        )

        self.file_meta_df.set_index("index", inplace=True)
        self.column_meta = pd.read_excel(
            f_path, sheet_name="column_meta", engine="openpyxl"
        )
        # self.column_meta.set_index("index", inplace = True)
        self.meta = pd.read_excel(f_path, sheet_name="meta", engine="openpyxl")

        self.meta["value"] = self.meta["value"].astype(
            str
        )  # solves bug, when datetime is not rendered as string
        self.column_meta["unit"] = self.column_meta["unit"].fillna(
            ""
        )  # nan triggers error for simple_unit_lookup

        self.json = {}

        self.only_use_base_iri = only_use_base_iri
        self.data_download_iri = data_download_iri

    def generate_file_json(self):
        """
        Generates the basic json-ld data model schema
        """

        # schema
        self.json["@context"] = {
            "csvw": "http://www.w3.org/ns/csvw#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "dcat": "http://www.w3.org/ns/dcat#",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
        }

        if self.only_use_base_iri:
            file_uri = self.file_meta_df.loc["namespace", "value"] + "/"
        else:
            file_uri = (
                "/".join(
                    [
                        self.file_meta_df.loc["namespace", "value"],
                        self.file_meta_df.loc["uuid", "value"],
                    ]
                )
                + "#"
            )
        self.json["@context"]["fileid"] = file_uri

        # #add dcat file description
        self.json["@id"] = "fileid:dataset"
        self.json["@type"] = "dcat:Dataset"

        self.json["dcat:downloadURL"] = self.file_meta_df.loc[
            "server_file_path", "value"
        ]

        return file_uri  # return file uri to be used for the abox template

    def generate_meta_json(self):
        # all meta data is stored using the notes relation of the file
        self.json[annotations["hasMetaData"]] = []

        ##############################
        # add description meta data to the json
        ##############################

        meta_quantity_df = self.meta.loc[~(self.meta["unit"].isna()), :]
        meta_description_df = self.meta.loc[(self.meta["unit"].isna()), :]

        for idx, meta_desc in meta_description_df.iterrows():
            row_id = meta_desc[
                "index"
            ]  # idx for increasing id of individuals, row_id for labels

            self.json[annotations["hasMetaData"]].append(
                {
                    "@id": f"fileid:metadata-{idx}",
                    "rdfs:label": row_id,
                    "@type": annotations["meta_data_type"],
                    annotations["meta_data_value_annotation"]: {
                        # all meta data as string
                        "@value": meta_desc["value"],
                        "@type": "xsd:string",
                    },
                }
            )

        ##############################
        # add quantity meta data to the json
        ##############################
        for idx, meta_desc in meta_quantity_df.iterrows():
            row_id = meta_desc[
                "index"
            ]  # idx for increasing id of individuals, row_id for labels

            self.json[annotations["hasMetaData"]].append(
                {
                    "@id": f"fileid:metadata-{idx}",
                    "rdfs:label": row_id,
                    "@type": [
                        annotations["quantity_class"],
                        annotations["meta_data_type"],
                    ],
                    annotations["meta_data_quantity_annotation"]: {
                        "@type": annotations[
                            "numeric_class"
                        ],  # could also be float or any other class
                        "@id": f"fileid:numeric-{idx}",
                        annotations[
                            "meta_data_numeric_annotation"
                        ]: {  # todo use different relation depending on the data type
                            "@value": meta_desc[
                                "value"
                            ],  # todo function that detects the data type (assume float atm)
                            "@type": "xsd:float",
                        },
                        annotations["meta_data_unit_annotation"]: [
                            emmo_utils.generate_unit_individuals(
                                meta_desc["unit"], idx
                            ),  # function that assigns EMMO units
                            {
                                # Additional to the EMMO Unit system, a UnitLiteral is added, this helper individual just stores the
                                # Name of the unit, allows for simple query construction
                                "@id": f"fileid:unitliteral-{idx}",
                                "@type": annotations["UnitLiteral"],
                                annotations["meta_data_value_annotation"]: {
                                    "@value": meta_desc["unit"],
                                    "@type": "xsd:string",
                                },
                            },
                        ]
                        # {
                        # "@value":meta_desc['Unit'] #todo add function that assigns EMMO unit
                        # }
                    },
                }
            )

    def generate_column_json(self):
        # self.json["hasMetaData"] = []
        # currently use same relation for columns and meta data since datamodel
        # ontology -> http://emmo.info/datamodel#composition

        for idx, col_desc in self.column_meta.iterrows():
            if self.data_download_iri:
                download_url = self.data_download_iri + "/" + f"column-{idx}"
            else:
                download_url = None

            # col_id = col_desc["index"]

            self.json[annotations["hasMetaData"]].append(
                {
                    "@id": f"fileid:column-{idx}",
                    "@type": annotations["column_class"],
                    "rdfs:label": col_desc["titles"],
                    "dcat:downloadURL": download_url,
                    annotations["meta_data_unit_annotation"]: [
                        emmo_utils.generate_unit_individuals(
                            col_desc["unit"], idx
                        ),  # function that assigns EMMO units
                        {
                            # Additional to the EMMO Unit system, a UnitLiteral is added, this helper individual just stores the
                            # Name of the unit, allows for simple query construction
                            "@id": f"fileid:unitliteral-{idx}",
                            "@type": annotations["UnitLiteral"],
                            annotations["meta_data_unit_annotation"]: {
                                "@value": col_desc["unit"],
                                "@type": "xsd:string",
                            },
                        },
                    ]
                    # {
                    #     "@value":unit #todo add function that assings EMMO unit
                    #     }
                }
            )

    def to_json_ld(self, f_path):
        with open(f_path, "w") as output_file:
            json.dump(self.json, output_file, indent=4)

    def to_ttl(self, f_path):
        g = Graph()
        graph = g.parse(data=json.dumps(self.json), format="json-ld")
        graph.serialize(f_path, format="ttl")
