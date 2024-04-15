"""Data2RDF parsers."""

from enum import Enum

from .csv_parser import CSVParser
from .excel_parser import ExcelParser

Parser = Enum(
    "Parser",
    {
        "csv": CSVParser,
        "excel": ExcelParser,
    },
)

__all__ = ["Parser"]
