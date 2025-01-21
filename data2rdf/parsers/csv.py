"""CSV Parser for data2rdf"""

import os
import warnings
from io import StringIO
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import numpy as np
import pandas as pd
from pydantic import AliasChoices, Field

from data2rdf.models.graph import PropertyGraph, QuantityGraph
from data2rdf.utils import make_prefix
from data2rdf.warnings import MappingMissmatchWarning, ParserWarning

from .base import ABoxBaseParser, BaseFileParser, TBoxBaseParser
from .utils import _make_tbox_classes, _make_tbox_json_ld, _strip_unit

from data2rdf.models.mapping import (  # isort:skip
    ABoxBaseMapping,
    TBoxBaseMapping,
)


def _replace(value: Optional[str], to_be_replaced: List[str]) -> Any:
    """Replace char in string"""
    if isinstance(value, str):
        for char in to_be_replaced:
            value = value.replace(char, "")
    return value


def _load_data_file(self: "Union[CSVTBoxParser, CSVABoxParser]") -> StringIO:
    """Load csv file"""
    if isinstance(self.raw_data, str):
        if os.path.isfile(self.raw_data):
            with open(self.raw_data, encoding=self.config.encoding) as file:
                content = StringIO(file.read())
        else:
            content = StringIO(self.raw_data)
    else:
        raise TypeError(
            f"`raw_data` must be of type `str`, not `{type(self.raw_data)}`"
        )
    return content


class CSVTBoxParser(TBoxBaseParser):
    """
    CSV file parser in tbox mode
    """

    # OVERRIDE
    mapping: Union[str, List[TBoxBaseMapping]] = Field(
        ...,
        description="""File path to the mapping file to be parsed or
        a list with the mapping.""",
    )
    column_sep: Optional[str] = Field(",", description="Data column separator")
    header_length: int = Field(
        1, description="Length of the header of the CSV sheet", ge=1
    )

    fillna: Optional[Any] = Field(
        "", description="Value to fill NaN values in the parsed dataframe."
    )

    # OVERRIDE
    @property
    def mapping_model(self) -> TBoxBaseMapping:
        """TBox Mapping Model for CSV Parser"""
        return TBoxBaseMapping

    # OVERRIDE
    @property
    def json_ld(self) -> "Dict[str, Any]":
        """Make the json-ld if pipeline is in abox-mode"""
        return _make_tbox_json_ld(self)

    # OVERRIDE
    @classmethod
    def _run_parser(
        cls,
        self: "CSVTBoxParser",
        datafile: StringIO,
        mapping: "List[TBoxBaseMapping]",
    ) -> None:
        """
        Class method for running the CSVTBoxParser. This method reads a CSV file
        into a pandas DataFrame and then uses the provided mapping to create TBox
        classes.

        Parameters:
            self (CSVTBoxParser): The instance of the parser.
            datafile (StringIO): The CSV file to be parsed.
            mapping (List[TBoxBaseMapping]): The list of mappings to be applied.

        Returns:
            None
        """

        df = pd.read_csv(datafile, sep=self.column_sep)
        _make_tbox_classes(self, df, mapping)

    # OVERRIDE
    @classmethod
    def _load_data_file(cls, self: "CSVTBoxParser") -> StringIO:
        """Load CSV file"""
        return _load_data_file(self)


class CSVABoxParser(ABoxBaseParser):
    """
    CSV file parser in abox mode
    """

    metadata_sep: Optional[str] = Field(
        None, description="Metadata column separator"
    )
    metadata_length: int = Field(..., description="Length of the metadata")
    dataframe_sep: Optional[str] = Field(
        None,
        description="Column separator of the dataframe header",
        alias=AliasChoices("dataframe_sep", "time_series_sep"),
    )
    dataframe_header_length: int = Field(
        2,
        description="Length of header of the dataframe",
        alias=AliasChoices(
            "dataframe_header_length", "time_series_header_length"
        ),
    )
    fillna: Optional[Any] = Field(
        "", description="Value to fill NaN values in the parsed dataframe."
    )
    # OVERRIDE
    mapping: Union[str, List[ABoxBaseMapping]] = Field(
        ...,
        description="""File path to the mapping file to be parsed or
        a list with the mapping.""",
    )

    # OVERRIDE
    @property
    def mapping_model(self) -> ABoxBaseMapping:
        """ABox Mapping Model for CSV Parser"""
        return ABoxBaseMapping

    # OVERRIDE
    @property
    def json_ld(self) -> "Dict[str, Any]":
        """
        Returns a JSON-LD representation of the CSV data in ABox mode.

        This method generates a JSON-LD object that describes the CSV data,
        including its metadata, dataframe data, and relationships between them.

        The returned JSON-LD object is in the format of a csvw:TableGroup,
        which contains one or more csvw:Table objects. Each csvw:Table object
        represents a table in the CSV data, and contains information about its
        columns, rows, and relationships to other tables.

        The JSON-LD object also includes context information, such as namespace
        prefixes and base URLs, to help with serialization and deserialization.

        Returns:
        Dict[str, Any]: A JSON-LD object representing the CSV data in ABox mode.
        """

        if not self.config.suppress_file_description:
            tables = []

            if self.general_metadata:
                meta_table = {
                    "@type": "csvw:Table",
                    "rdfs:label": "Metadata",
                    "csvw:row": [],
                }

                for n, mapping in enumerate(self.general_metadata):
                    if isinstance(mapping, QuantityGraph):
                        row = {
                            "@type": "csvw:Row",
                            "csvw:titles": {
                                "@type": "xsd:string",
                                "@value": mapping.key,
                            },
                            "csvw:rownum": {
                                "@type": "xsd:integer",
                                "@value": n,
                            },
                            "qudt:quantity": mapping.json_ld,
                        }
                        meta_table["csvw:row"].append(row)
                    elif isinstance(mapping, PropertyGraph):
                        row = {
                            "@type": "csvw:Row",
                            "csvw:titles": {
                                "@type": "xsd:string",
                                "@value": mapping.key,
                            },
                            "csvw:rownum": {
                                "@type": "xsd:integer",
                                "@value": n,
                            },
                            "csvw:describes": mapping.json_ld,
                        }
                        meta_table["csvw:row"].append(row)
                    else:
                        raise TypeError(
                            f"Mapping must be of type {QuantityGraph} or {PropertyGraph}, not {type(mapping)}"
                        )
                tables += [meta_table]

            if self.dataframe_metadata:
                column_schema = {"@type": "csvw:Schema", "csvw:column": []}
                tables += [
                    {
                        "@type": "csvw:Table",
                        "rdfs:label": "Dataframe",
                        "csvw:tableSchema": column_schema,
                    }
                ]
                for idx, mapping in enumerate(self.dataframe_metadata):
                    if isinstance(mapping, QuantityGraph):
                        entity = {"qudt:quantity": mapping.json_ld}
                    elif isinstance(mapping, PropertyGraph):
                        entity = {"dcterms:subject": mapping.json_ld}
                    else:
                        raise TypeError(
                            f"Mapping must be of type {QuantityGraph} or {PropertyGraph}, not {type(mapping)}"
                        )

                    if self.config.data_download_uri:
                        download_url = {
                            "dcterms:identifier": {
                                "@type": "xsd:anyURI",
                                "@value": urljoin(
                                    str(self.config.data_download_uri),
                                    f"column-{idx}",
                                ),
                            }
                        }
                    else:
                        download_url = {}

                    column = {
                        "@type": "csvw:Column",
                        "csvw:titles": {
                            "@type": "xsd:string",
                            "@value": mapping.key,
                        },
                        **entity,
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
                    column_schema["csvw:column"].append(column)

            # flatten list if only one value exists
            if len(tables) == 1:
                tables = tables.pop()
            # make relation to csvw:table property
            if tables:
                csvw_tables = {"csvw:table": tables}
            else:
                csvw_tables = {}

            json_ld = {
                "@context": {
                    f"{self.config.prefix_name}": make_prefix(self.config),
                    "csvw": "http://www.w3.org/ns/csvw#",
                    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                    "dcat": "http://www.w3.org/ns/dcat#",
                    "xsd": "http://www.w3.org/2001/XMLSchema#",
                    "dcterms": "http://purl.org/dc/terms/",
                    "qudt": "http://qudt.org/schema/qudt/",
                    "csvw": "http://www.w3.org/ns/csvw#",
                    "foaf": "http://xmlns.com/foaf/spec/",
                },
                "@id": f"{self.config.prefix_name}:tableGroup",
                "@type": "csvw:TableGroup",
                **csvw_tables,
            }
        else:
            json_ld = {
                "@graph": [model.json_ld for model in self.general_metadata]
                + [model.json_ld for model in self.dataframe_metadata]
            }
        return json_ld

    # OVERRIDE
    @classmethod
    def _run_parser(
        cls,
        self: "CSVParser",
        datafile: StringIO,
        mapping: "List[ABoxBaseMapping]",
    ) -> None:
        """
        This function is responsible for parsing metadata, dataframe metadata, and dataframe data from a CSV file.

        It takes in three parameters:
        - `self`: The CSVParser instance.
        - `datafile`: The StringIO object containing the CSV data.
        - `mapping`: A list of ABoxBaseMapping instances that map the CSV data to the desired output format.

        The function returns None, but it populates the following instance variables:
        - `self._general_metadata`: A list of PropertyGraph or QuantityGraph instances representing the general metadata.
        - `self._dataframe_metadata`: A list of QuantityGraph instances representing the dataframe metadata.
        - `self._dataframe`: A pandas DataFrame containing the dataframe data.

        The function also raises ValueError if the `metadata_length` is greater than 0 but `metadata_sep` is not set.
        It raises TypeError if the unit for a key is not a string.
        It raises MappingMissmatchWarning if no match is found in the mapping for a key.
        """

        for model in mapping:
            if model.custom_relations:
                raise RuntimeError(
                    "Custom relations for CSV parser is currently not supported"
                )

        mapping = {model.key: model for model in mapping}

        dataframe: Union[pd.DataFrame, List[None]] = cls._parse_dataframe(
            self, datafile
        )
        if self.dropna:
            dataframe.dropna(inplace=True)
        datafile.seek(0)

        # iterate over general metadata
        self._general_metadata = []
        if self.metadata_length > 0:
            if not self.metadata_sep:
                raise ValueError(
                    "`metadata_length` is > 0 but `metadata_sep` is not set"
                )
            metadata = pd.read_csv(
                datafile,
                sep=self.metadata_sep,
                nrows=self.metadata_length,
                names=["key", "value", "unit"],
                header=None,
            )
            # remove unneeded characters
            metadata = metadata.map(
                lambda value: _replace(value, self.config.remove_from_datafile)
            )
            metadata.replace({np.nan: self.fillna}, inplace=True)
            for i, metadatum in metadata.iterrows():
                # get the match from the mapping
                mapping_match = mapping.get(metadatum.key)

                # only map the data if a match is found
                if mapping_match:
                    # get unit
                    unit = mapping_match.unit or metadatum.unit or None
                    if unit:
                        if not isinstance(unit, str):
                            raise TypeError(
                                f"""Unit `{unit}` for key `{metadatum.key}` is not a string.
                                Is it a bad mapping?"""
                            )
                        unit = _strip_unit(unit, self.config.remove_from_unit)

                    # instanciate model
                    model_data = {
                        "key": metadatum.key,
                        "value": metadatum.value,
                        "unit": unit,
                        "iri": mapping_match.iri,
                        "suffix": mapping_match.suffix,
                        "annotation": mapping_match.annotation or None,
                        "config": self.config,
                    }
                    if mapping_match.value_relation:
                        model_data[
                            "value_relation"
                        ] = mapping_match.value_relation
                    if model_data.get("unit"):
                        if mapping_match.unit_relation:
                            model_data[
                                "unit_relation"
                            ] = mapping_match.unit_relation
                        model = QuantityGraph(**model_data)
                    else:
                        model = PropertyGraph(**model_data)
                    self._general_metadata.append(model)
                else:
                    warnings.warn(
                        f"No match found in mapping for key `{metadatum.key}`",
                        MappingMissmatchWarning,
                    )

        # parse dataframe data and meta data
        self._dataframe_metadata = []
        self._dataframe = {}

        for key in dataframe:
            # get matching mapping
            mapping_match = mapping.get(key)

            if mapping_match:
                # get unit
                unit = (
                    mapping_match.unit
                    or (
                        dataframe[key].iloc[0]
                        if self.dataframe_header_length == 2
                        else None
                    )
                    or None
                )

                if unit:
                    if not isinstance(unit, str):
                        raise TypeError(
                            f"""Unit `{unit}` for key `{key}` is not a string.
                            Is it a bad mapping?"""
                        )
                    unit = _strip_unit(unit, self.config.remove_from_unit)

                # assign model
                model = QuantityGraph(
                    key=key,
                    unit=unit,
                    iri=mapping_match.iri,
                    suffix=mapping_match.suffix,
                    annotation=mapping_match.annotation or None,
                    config=self.config,
                )
                if mapping_match.unit_relation:
                    model.unit_relation = mapping_match.unit_relation

                # append model
                self.dataframe_metadata.append(model)

                # assign dataframe data
                self._dataframe[model.suffix] = dataframe[key][
                    self.dataframe_header_length - 1 :
                ].to_list()

            else:
                warnings.warn(
                    f"No match found in mapping for key `{key}`",
                    MappingMissmatchWarning,
                )
        # set dataframe as pd dataframe
        self._dataframe = pd.DataFrame.from_dict(
            self._dataframe, orient="index"
        ).transpose()
        # check if drop na:
        if self.dropna:
            self._dataframe.dropna(how="all", inplace=True)

    # OVERRIDE
    @classmethod
    def _load_data_file(cls, self: "CSVABoxParser") -> StringIO:
        """Load csv file"""
        return _load_data_file(self)

    @classmethod
    def _parse_dataframe(
        cls, self: "CSVParser", datafile: "StringIO"
    ) -> Union[pd.DataFrame, List[None]]:
        if self.dataframe_sep:
            response = pd.read_csv(
                datafile,
                encoding=self.config.encoding,
                sep=self.dataframe_sep,
                skiprows=self.metadata_length,
            )
            response = response.map(
                lambda value: _replace(value, self.config.remove_from_datafile)
            )
            response.columns = [
                _replace(column, self.config.remove_from_datafile)
                for column in response.columns
            ]
        else:
            warnings.warn(
                "`dataframe_sep` is not set. Any potential dataframe in the data file will be skipped.",
                ParserWarning,
            )
            response = []
        return response


class CSVParser(BaseFileParser):
    """Parser for CSV/TSV files"""

    # OVERRIDE
    @property
    def _abox_parser(self) -> CSVABoxParser:
        """Pydantic Model for CSV ABox parser"""
        return CSVABoxParser

    # OVERRIDE
    @property
    def _tbox_parser(self) -> CSVTBoxParser:
        """Pydantic Model for CSV TBox parser"""
        return CSVTBoxParser

    # OVERRIDE
    @property
    def media_type(self) -> str:
        """IANA Media type definition of the resource to be parsed."""
        return "http://www.iana.org/assignments/media-types/text/csv"
