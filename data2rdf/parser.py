import uuid
from abc import ABC, abstractmethod


class DataParser(ABC):
    """
    generic parser abstract class with common parser attrubutes and functionalities
    Attributes:
        f_path (str): The file path for the csv file used as input for the
        server_f_path (str): By default the file path for the csv file (f_path) gets used as
        dcat:downloadURL attribute for the created dcat:Dataset individual. On a server the actual download url of the file should be used
        (e.g. on the DSMS https://127.0.0.1/api/knowledge/data-files/764f6e51-a244-42f9-a754-c3e2861f63e4/raw_data/excel_file.xlsx).
        data_storage_path (str): Optional different storagelocation for the hdf5 file holding the data. Default is the same location as the input file.
        data_storage_group_name (str): Name of the group in the hdf5 to store the data. Using the data_storage_path and the data_storage_group_name multiple datasets can be stored in the same hdf5 file.
        namespace (str): The namespace that will be used by the rdf_generation class to construct the abox individuals.
    """

    def __init__(
        self,
        f_path,
        server_f_path=None,
        data_storage_path=None,
        data_storage_group_name="df",
        namespace="http://www.test.de",
    ):
        self.f_path = f_path
        self.server_f_path = server_f_path if server_f_path else f_path
        self.data_storage_path = (
            data_storage_path
            if data_storage_path
            else f"{f_path}.datastorage.hdf5"
        )
        self.data_storage_group_name = data_storage_group_name
        self.namespace = namespace
        self.id_uuid = str(uuid.uuid4())

    @abstractmethod
    def load_file(self):
        pass

    @abstractmethod
    def parse_meta_data(self):
        pass

    # def generate_file_meta_df(self):
    #     self.file_meta_df = pd.DataFrame(
    #         {
    #             "value": [
    #                 self.f_path,
    #                 self.server_f_path,
    #                 self.namespace,
    #                 self.id_uuid,
    #             ]
    #         },
    #         index=["file_path", "server_file_path", "name_space", "uuid"],
    #     )
    #     self.file_meta_df.index.name = "index"

    @abstractmethod
    def generate_file_meta_df(self):
        pass

    @abstractmethod
    def generate_data_storage(self):
        pass

    def generate_file_uuid(self):
        self.id_uuid = str(uuid.uuid4())
