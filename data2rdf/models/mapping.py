"""Mapping models for data2rdf"""
import json
import warnings
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

    def _make_suffix(cls) -> str:
        return str(cls.iri).split(cls.config.separator)[-1]


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
    time_series_end: Optional[str] = Field(
        None,
        description="Cell location for the end of the time series quantity",
    )
    worksheet: Optional[str] = Field(
        None,
        description="Name of the worksheet where the entity is located in the excel file",
    )


class QuantityMapping(BasicConceptMapping):
    """Mapping for a quantity without a discrete value.
    E.g. a quantity describing a column of a time series or table."""

    unit: Union[str, AnyUrl] = Field(
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
        return value

    @property
    def graph(cls) -> Graph:
        graph = Graph(identifier=cls.config.graph_identifier)
        suffix = cls._make_suffix()
        prefix = make_prefix(cls.config)
        model = {
            "@context": {
                "fileid": prefix,
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
                "qudt": "http://qudt.org/schema/qudt/",
            },
            "@id": f"fileid:{suffix}",
            "@type": str(cls.iri),
            **cls._get_unit_json(),
            **cls._get_value(),
        }
        graph.parse(data=json.dumps(model), format="json-ld")
        return graph

    def _get_unit_json(self) -> "Dict[str, Any]":
        if self.unit:
            value = {
                "qudt:hasUnit": {"@value": self.unit, "@type": "xsd:anyURI"}
            }
        else:
            value = {}
        return value

    def _get_value(self) -> "Dict[str, Any]":
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


class PropertyMapping(BasicConceptMapping):
    """Mapping for a non-quantitative property. E.g. the
    name of a tester or a testing facility."""

    value: str = Field(
        ..., description="Non-quantitative Value of the property"
    )
    annotation: Optional[AnyUrl] = Field(
        None, description="Base IRI with which the value shall be concatenated"
    )

    @property
    def graph(cls) -> Graph:
        graph = Graph(identifier=cls.config.graph_identifier)
        suffix = cls._make_suffix()
        prefix = make_prefix(cls.config)
        model = {
            "@context": {
                "fileid": prefix,
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
            },
            "@id": f"fileid:{suffix}",
            "@type": str(cls.iri),
            "rdfs:label": cls.value,
        }
        graph.parse(data=json.dumps(model), format="json-ld")
        return graph
