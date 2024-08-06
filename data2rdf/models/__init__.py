"""Data2RDF models"""

from .graph import PropertyGraph, QuantityGraph
from .mapping import ABoxBaseMapping, BasicConceptMapping

__all__ = [
    "QuantityGraph",
    "PropertyGraph",
    "ABoxBaseMapping",
    "BasicConceptMapping",
]
