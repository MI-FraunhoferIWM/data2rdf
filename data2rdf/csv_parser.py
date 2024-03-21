import io

import magic
import pandas as pd

from data2rdf.parser import DataParser


class CSVParser(DataParser):
    """
    Generates the excel input sheet that can be used
    as input for abox skeleton files.

    Attributes:
        f_path (str): The file path for the csv file used as input for the
        # parser. This path gets also stored as dcat:downloadURL attribute for the created dcat:Dataset individual by the rdf_generation class.
        header_sep (str): separator (e.g.: ,,;\t) for the header metadata.
        column_sep (str): separator (e.g.: ,,;\t) for the column data.
        header_length (int): Number of rows of the metadata header.
        server_f_path (str): By default the file path for the csv file (f_path) gets used as dcat:downloadURL attribute for the created dcat:Dataset individual. On a server the actual download url of the file should be used (e.g. on the DSMS https://127.0.0.1/api/knowledge/data-files/764f6e51-a244-42f9-a754-c3e2861f63e4/raw_data/excel_file.xlsx).
        data_storage_path (str): Optional different storage location for the hdf5 file holding the data. Default is the same location as the input file.
        data_storage_group_name (str): Name of the group in the hdf5 to store the data. Using the data_storage_path and the data_storage_group_name multiple datasets can be stored in the same hdf5 file.
        namespace (str): The namespace that will be used by the rdf_generation class to construct the abox individuals.

    """

    def __init__(
        self,
        f_path,
        header_sep,
        column_sep,
        header_length,
        # when a file is stored on a server it makes sense to store this path
        # (e.g. http access) instead of the local path
        server_f_path=None,
        # the columns get stored in a dedicated format (hdf5 by default)
        data_storage_path=None,
        # one hdf5 store is probably enough for our current setup (use
        # different groups (folders), for each file)
        data_storage_group_name="df",
        namespace="http://www.test.de",
    ):
        super().__init__(
            f_path,
            server_f_path,
            data_storage_path,
            data_storage_group_name,
            namespace,
        )

        self.header_sep = header_sep
        self.column_sep = column_sep
        self.header_length = header_length

    def parser_data(self):
        self.get_file_encoding()
        self.load_file()
        self.generate_file_uuid()
        self.parse_meta_data()
        self.split_meta_df()
        self.parse_table()
        self.generate_column_df()
        self.generate_file_meta_df()
        self.clean_table_df()

    def get_file_encoding(self):
        """
        Get file encoding
        """
        rawdata = open(self.f_path, "rb").read()
        buffered = magic.open(magic.MAGIC_MIME_ENCODING)
        buffered.load()
        self.encoding = buffered.buffer(rawdata)

    def load_file(self):
        with open(self.f_path, encoding=self.encoding) as file:
            self.file = file.read()

    def parse_meta_data(self):
        """
        Parser the header of a csv file that looks like that:
        meta data-1; meta data value-1; unit-1
        meta data-2; meta data value-2; unit-2
        ...
        meta data-n; meta data value-n; unit-n

        And stores in pd DataFrame
        """
        header = ["index", "value", "unit"]

        meta_df = pd.DataFrame(columns=header, index=range(self.header_length))

        # needs specific parsing
        # load the header as an own table until the header length ends
        # TODO automate detection of header end encoding -> Mat-O-Lab
        # with open(self.f_path, 'r', encoding=self.encoding) as file:
        buf = io.StringIO(self.file)

        for l_count, line in enumerate(buf):
            for i_count, item in enumerate(line.split(self.header_sep)):
                meta_df.iloc[l_count, i_count] = str(item.strip("\n"))

            if l_count == self.header_length - 1:
                break

        meta_df.fillna("", inplace=True)
        self.meta_df = meta_df.apply(lambda s: s.str.replace('"', ""))
        # self.meta_df.index.name = 'index'
        self.meta_df.set_index("index", inplace=True)

    def split_meta_df(self):
        """
        Split the meta data into basic description and quantities
        """
        self.meta_quantity_df = self.meta_df.loc[
            (self.meta_df["unit"] != ""), :
        ]
        self.meta_description_df = self.meta_df.loc[
            (self.meta_df["unit"] == ""), :
        ]

    def parse_table(self):
        self.df_table = pd.read_csv(
            self.f_path,
            encoding=self.encoding,
            sep=self.column_sep,
            skiprows=self.header_length,
        )

    def generate_column_df(self):
        self.column_df = pd.DataFrame(self.df_table.iloc[0, :])
        self.column_df.columns = ["unit"]
        self.column_df["titles"] = self.column_df.index
        self.column_df.index.name = "index"

    def clean_table_df(self):
        self.df_table = self.df_table.iloc[1:, :]

    def generate_excel_spreadsheet(self, output_path):
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            self.file_meta_df.to_excel(writer, "file")
            self.column_df.to_excel(writer, "column_meta")
            self.meta_df.to_excel(writer, "meta")

    def generate_data_storage(self):
        self.df_table.to_hdf(
            self.data_storage_path, key=self.data_storage_group_name
        )
