import json

import pandas as pd
from rdflib import Graph

from data2rdf.annotation_confs import annotations
from data2rdf.emmo_lib import emmo_utils


def split_prefix_suffix(iri):
    if "#" in iri:
        separator = "#"
    elif "/" in iri:
        separator = "/"
    else:
        raise ValueError(f"`{iri}` does not contain '#' or '/' separator")

    parts = iri.split(separator)
    suffix = parts[-1]

    return suffix


def is_integer(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


class RDFGenerator:

    """
    Transforms the generic excel sheet to RDF
    """

    def __init__(self, f_path, mapping_file, file_uri, data_download_iri):
        self.file_uri = file_uri
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

        self.mapping = pd.read_excel(
            mapping_file,
            sheet_name="sameas",
            engine="openpyxl",
        )

        self.json = {}

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
            "dcterms": "http://purl.org/dc/terms/",
        }

        self.json["@context"]["fileid"] = self.file_uri

        # #add dcat file description
        self.json["@id"] = "fileid:dataset"
        self.json["@type"] = "dcat:Dataset"

        self.json["dcat:downloadURL"] = self.file_meta_df.loc[
            "server_file_path", "value"
        ]

    def generate_meta_json(self):
        # all meta data is stored using the notes relation of the file
        self.json[annotations["hasMetaData"]] = []

        ##############################
        # add description meta data to the json
        ##############################

        meta_quantity_df = self.meta.loc[~(self.meta["unit"].isna()), :]
        meta_description_df = self.meta.loc[(self.meta["unit"].isna()), :]

        for idx, meta_desc in meta_description_df.iterrows():
            datum = {
                "rdfs:label": meta_desc["index"],
                "@type": annotations["meta_data_type"],
                annotations["meta_data_value_annotation"]: {
                    # all meta data as string
                    "@value": meta_desc["value"],
                    "@type": "xsd:string",
                },
            }
            self._make_identifier_and_annotation(datum, meta_desc)
            if not datum.get("@id"):
                datum["@id"] = f"fileid:metadata-{idx}"
            self.json[annotations["hasMetaData"]].append(datum)

        ##############################
        # add quantity meta data to the json
        ##############################
        for idx, meta_desc in meta_quantity_df.iterrows():
            if is_float(meta_desc["value"]):
                dtype = "xsd:float"
                value = float(meta_desc["value"])
            elif is_integer(meta_desc["value"]):
                dtype = "xsd:integer"
                value = int(meta_desc["value"])
            else:
                dtype = "xsd:string"
                value = meta_desc["value"]

            datum = {
                "rdfs:label": meta_desc["index"],
                "@type": [
                    annotations["quantity_class"],
                    annotations["meta_data_type"],
                ],
                annotations["meta_data_quantity_annotation"]: {
                    "@type": annotations[
                        "numeric_class"
                    ],  # could also be float or any other class
                    "@id": f"fileid:numeric-{idx}",
                    annotations["meta_data_numeric_annotation"]: {
                        "@value": value,
                        "@type": dtype,
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
            self._make_identifier_and_annotation(datum, meta_desc)
            if not datum.get("@id"):
                datum["@id"] = f"fileid:metadata-{idx}"
            self.json[annotations["hasMetaData"]].append(datum)

    def generate_column_json(self):
        # self.json["hasMetaData"] = []
        # currently use same relation for columns and meta data since datamodel
        # ontology -> http://emmo.info/datamodel#composition

        for idx, col_desc in self.column_meta.iterrows():
            if self.data_download_iri:
                download_url = self.data_download_iri + "/" + f"column-{idx}"
            else:
                download_url = None

            datum = {
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
                ],
            }
            self._make_identifier_and_annotation(datum, col_desc)
            if not datum.get("@id"):
                datum["@id"] = f"fileid:column-{idx}"
            self.json[annotations["hasMetaData"]].append(datum)

    def _make_identifier_and_annotation(self, datum, description):
        row = self.mapping.loc[
            self.mapping["Key"]
            == (description.get("index") or description.get("title"))
        ]
        if not row.empty:
            class_type = str(row["Class type"].values[0])
            value_annotation = row["Annotation"].values[0]
            value = description["value"]
            dcterms_annotations = [class_type]
            if not value_annotation and value:
                dcterms_annotations += [value_annotation + "/" + value]
            suffix = split_prefix_suffix(class_type)
            datum["dcterms:type"] = dcterms_annotations
            datum["@id"] = f"fileid:{suffix}"

    def to_json_ld(self, f_path):
        with open(f_path, "w") as output_file:
            json.dump(self.json, output_file, indent=4)

    def to_ttl(self, f_path):
        g = Graph()
        graph = g.parse(data=json.dumps(self.json), format="json-ld")
        graph.serialize(f_path, format="ttl")
