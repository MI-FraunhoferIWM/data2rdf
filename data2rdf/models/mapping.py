"""Mapping models for data2rdf"""
import json
import warnings
from abc import abstractmethod
from typing import Any, Dict, Optional, Union

from pydantic import AnyUrl, BaseModel, Field, ValidationInfo, field_validator
from rdflib import Graph

from data2rdf.config import Config
from data2rdf.qudt.utils import _get_query_match
from data2rdf.utils import is_float, is_integer, make_prefix


class BasicConceptMapping(BaseModel):
    """Basic mapping for any entity"""

    key: Optional[str] = Field(
        None, description="Key of the concept in the file"
    )
    iri: AnyUrl = Field(
        ..., description="Ontological class related to this concept"
    )
    config: Config = Field(
        default_factory=Config, description="Configuration object"
    )
    suffix: Optional[str] = Field(
        None,
        description="""Optional suffix of the individual
        which will be constructed. If not set, the suffix of the iri
        of the ontological class will be taken""",
        validate_default=True,
    )

    @field_validator("suffix")
    @classmethod
    def validate_suffix(
        cls, value: Optional[str], info: ValidationInfo
    ) -> str:
        """Return suffix for individal"""
        iri = info.data["iri"]
        config = info.data["config"]
        return value or str(iri).split(config.separator)[-1]

    @field_validator("config")
    @classmethod
    def validate_config(cls, value: Union[Dict[str, Any], Config]) -> Config:
        """Validate configuration"""
        if isinstance(value, dict):
            value = Config(**value)
        return value


class ClassConceptMapping(BasicConceptMapping):
    """Mapping for a concept coming from the mapping file"""

    unit: Optional[Union[str, AnyUrl]] = Field(
        None, description="Symbol or QUDT IRI for the mapping"
    )
    annotation: Optional[Union[str, AnyUrl]] = Field(
        None, description="Base IRI with which the value shall be concatenated"
    )

    @field_validator("annotation", mode="after")
    @classmethod
    def validate_annotation(
        cls, value: Optional[Union[str, AnyUrl]]
    ) -> Optional[AnyUrl]:
        if not (isinstance(value, str) and len(value) == 0) or isinstance(
            value, AnyUrl
        ):
            return value


class ExcelConceptMapping(ClassConceptMapping):
    """A special model for mapping from excel files to semantic concepts"""

    value_location: Optional[str] = Field(
        None, description="Cell location for the value of the quantity"
    )
    unit_location: Optional[str] = Field(
        None, description="Cell location for the unit of the quantity"
    )
    time_series_start: Optional[str] = Field(
        None,
        description="Cell location for the start of the time series quantity",
    )
    worksheet: Optional[str] = Field(
        None,
        description="Name of the worksheet where the entity is located in the excel file",
    )


class MergedConceptMapping(BasicConceptMapping):
    """Model for merged data of mapping and the data file"""

    @property
    @abstractmethod
    def json_ld(cls) -> Dict[str, Any]:
        """Return dict for json-ld of graph"""

    @property
    def graph(cls) -> Graph:
        """Return graph object based on json-ld"""
        graph = Graph(identifier=cls.config.graph_identifier)
        graph.parse(data=json.dumps(cls.json_ld), format="json-ld")
        return graph


class QuantityMapping(MergedConceptMapping):
    """Mapping for a quantity without a discrete value.
    E.g. a quantity describing a column of a time series or table."""

    unit: Optional[Union[str, AnyUrl]] = Field(
        ..., description="Symbol or QUDT IRI for the mapping"
    )
    value: Optional[Union[int, float]] = Field(
        None, description="Value of the quantity"
    )

    @field_validator("unit", mode="after")
    @classmethod
    def validate_unit(
        cls, value: Union[str, AnyUrl], info: ValidationInfo
    ) -> Optional[AnyUrl]:
        config = info.data.get("config")
        if isinstance(value, str):
            if not (value.startswith("https:") or value.startswith("http:")):
                match = _get_query_match(value, config.qudt_units)
                if len(match) == 0:
                    warnings.warn(
                        f"No QUDT Mapping found for unit with symbol `{value}`."
                    )
                    value = None
                elif len(match) > 1:
                    warnings.warn(
                        f"Multiple QUDT Mappings found for unit with symbol `{value}`."
                    )
                    value = match.pop()
                else:
                    value = match.pop()
        elif isinstance(value, AnyUrl):
            value = str(value)
        return value

    @property
    def json_ld(cls) -> Dict[str, Any]:
        """Return dict of json-ld for graph"""
        return {
            "@context": {
                "fileid": make_prefix(cls.config),
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
                "qudt": "http://qudt.org/schema/qudt/",
            },
            "@id": f"fileid:{cls.suffix}",
            "@type": str(cls.iri),
            **cls.unit_json,
            **cls.value_json,
        }

    @property
    def unit_json(self) -> "Dict[str, Any]":
        """Return json with unit definition"""
        if self.unit:
            value = {
                "qudt:hasUnit": {"@value": self.unit, "@type": "xsd:anyURI"}
            }
        else:
            value = {}
        return value

    @property
    def value_json(self) -> "Dict[str, Any]":
        """Return json with value definition"""
        if self.value:
            if is_float(self.value):
                dtype = "xsd:float"
                value = float(self.value)
            elif is_integer(self.value):
                dtype = "xsd:integer"
                value = int(self.value)
            else:
                raise ValueError(
                    f"""Datatype not recognized for key
                    `{self.key}` with value:
                    `{self.value}`"""
                )
            value = {"qudt:value": {"@type": dtype, "@value": value}}
        else:
            value = {}
        return value


class PropertyMapping(MergedConceptMapping):
    """Mapping for a non-quantitative property. E.g. the
    name of a tester or a testing facility."""

    value: str = Field(
        ..., description="Non-quantitative Value of the property"
    )
    annotation: Optional[AnyUrl] = Field(
        None, description="Base IRI with which the value shall be concatenated"
    )

    @property
    def json_ld(cls) -> Dict[str, Any]:
        """Return dict of json-ld for graph"""
        return {
            "@context": {
                "fileid": make_prefix(cls.config),
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
            },
            "@id": f"fileid:{cls.suffix}",
            "rdfs:label": cls.value,
            **cls.types_json,
        }

    @property
    def types_json(cls) -> "Dict[str, Any]":
        """Dict of json-ld for class types of the individual"""
        if cls.annotation:
            if str(cls.annotation).endswith(cls.config.separator):
                annotation = str(cls.annotation) + cls.value
            else:
                annotation = (
                    str(cls.annotation) + cls.config.separator + cls.value
                )
            types = {
                "@type": [
                    str(cls.iri),
                    annotation,
                ]
            }
        else:
            types = {"@type": str(cls.iri)}
        return types


class JsonConceptMapping(ClassConceptMapping):
    """A special model for mapping from json files to semantic concepts"""

    value_location: str = Field(
        ..., description="Json path for the value of the quantity or property"
    )
    unit_location: Optional[str] = Field(
        None, description="Json path to the unit of the property"
    )
