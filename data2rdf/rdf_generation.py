import json
import re

import pandas as pd
from rdflib import Graph

from data2rdf.qudt_utils import _check_qudt_mapping


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

        file_path = self.file_meta_df.loc["server_file_path", "value"]

        media_type = (
            "https://www.iana.org/assignments/media-types/application/vnd.ms-excel"
            if "xls" in file_path
            else "http://www.iana.org/assignments/media-types/text/csv"
        )

        self.meta_table = {
            "@type": "csvw:Table",
            "rdfs:label": "Metadata",
            "csvw:row": [],
        }

        self.column_schema = {"@type": "csvw:Schema", "csvw:column": []}

        self.json = {
            "@context": {
                "fileid": self.file_uri,
                "csvw": "http://www.w3.org/ns/csvw#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "dcat": "http://www.w3.org/ns/dcat#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
                "dcterms": "http://purl.org/dc/terms/",
                "qudt": "http://qudt.org/schema/qudt/",
                "csvw": "http://www.w3.org/ns/csvw#",
                "foaf": "http://xmlns.com/foaf/spec/",
            },
            "@id": "fileid:dataset",
            "@type": "dcat:Dataset",
            "dcat:distribution": {
                "@type": "dcat:Distribution",
                "dcat:mediaType": {
                    "@type": "xsd:anyURI",
                    "@value": media_type,
                },
                "dcat:accessURL": {
                    "@type": "xsd:anyURI",
                    "@value": file_path,
                },
            },
            "dcterms:hasPart": {
                "@id": "fileid:tableGroup",
                "@type": "csvw:TableGroup",
                "csvw:table": [
                    self.meta_table,
                    {
                        "@type": "csvw:Table",
                        "rdfs:label": "Time series data",
                        "csvw:tableSchema": self.column_schema,
                    },
                ],
            },
        }

    def generate_meta_json(self):
        ##############################
        # add description meta data to the json
        ##############################

        meta_quantity_df = self.meta.loc[~(self.meta["unit"].isna()), :]
        meta_description_df = self.meta.loc[(self.meta["unit"].isna()), :]

        for idx, meta_desc in meta_description_df.iterrows():
            row = {
                "@type": "csvw:Row",
                "csvw:titles": {
                    "@type": "xsd:string",
                    "@value": meta_desc["index"],
                },
                "csvw:rownum": {"@type": "xsd:integer", "@value": idx},
                "csvw:describes": {
                    **self._make_types_and_id(meta_desc),
                    "rdfs:label": meta_desc["value"],
                },
            }
            self.meta_table["csvw:row"].append(row)

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
                raise ValueError(
                    f"""Datatype not recognized for key
                    `{meta_desc['index']}` with value:
                    `{meta_desc['value']}`"""
                )

            row = {
                "@type": "csvw:Row",
                "csvw:titles": {
                    "@type": "xsd:string",
                    "@value": meta_desc["index"],
                },
                "csvw:rownum": {"@type": "xsd:integer", "@value": idx},
                "qudt:quantity": {
                    "qudt:value": {
                        "@type": dtype,
                        "@value": value,
                    },
                    **self._make_types_and_id(meta_desc),
                    **_check_qudt_mapping(meta_desc["unit"]),
                },
            }
            self.meta_table["csvw:row"].append(row)

    def generate_column_json(self):
        for idx, col_desc in self.column_meta.iterrows():
            if self.data_download_iri:
                download_url = {
                    "dcterms:identifier": {
                        "@type": "xsd:anyURI",
                        "@value": f"{self.data_download_iri}/column-{idx}",
                    }
                }
            else:
                download_url = {}

            column = {
                "@type": "csvw:Column",
                "csvw:titles": {
                    "@type": "xsd:string",
                    "@value": col_desc["index"],
                },
                "qudt:quantity": {
                    **self._make_types_and_id(col_desc),
                    **_check_qudt_mapping(col_desc["unit"]),
                },
                "foaf:page": {
                    "@type": "foaf:Document",
                    "dcterms:format": {
                        "@type": "xsd:anyURI",
                        "@value": "https://www.iana.org/assignments/media-types/application/json",
                    },
                    "dcterms:type": {
                        "@type": "xsd:anyURI",
                        "@value": "http://purl.org/dc/terms/Dataset",
                    },
                    **download_url,
                },
            }
            self.column_schema["csvw:column"].append(column)

    def _make_types_and_id(self, description):
        row = self.mapping.loc[
            self.mapping["Key"]
            == (description.get("index") or description.get("title"))
        ]
        if not row.empty:
            class_type = str(row["Class type"].values[0])
            value_annotation = row["Annotation"].values[0]
            value = description.get("value")
            types = [class_type]
            if not value_annotation and value:
                types += [value_annotation + "/" + value]
            suffix = split_prefix_suffix(class_type)
            return {"@type": types, "@id": f"fileid:{suffix}"}
        else:
            identifier = re.sub(
                r"[^A-Za-z0-9]+",
                "",
                description.get("index") or description.get("title"),
            )
            return {"@type": "skos:Concept", "@id": identifier}

    def to_json_ld(self, f_path):
        with open(f_path, "w") as output_file:
            json.dump(self.json, output_file, indent=4)

    def to_ttl(self, f_path):
        g = Graph()
        graph = g.parse(data=json.dumps(self.json), format="json-ld")
        graph.serialize(f_path, format="ttl")
