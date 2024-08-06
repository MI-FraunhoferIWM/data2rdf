"""Data2RDF parsers."""

from enum import Enum

from .csv import CSVParser
from .excel import ExcelParser
from .json import JsonParser

Parser = Enum(
    "Parser",
    {"csv": CSVParser, "excel": ExcelParser, "json": JsonParser},
)

__all__ = ["Parser"]
