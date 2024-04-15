"""Data2RDF parsers."""

from enum import Enum

from .csv import CSVParser
from .excel import ExcelParser

Parser = Enum(
    "Parser",
    {
        "csv": CSVParser,
        "excel": ExcelParser,
    },
)

__all__ = ["Parser"]
