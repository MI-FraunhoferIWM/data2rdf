"""Data2RDF Pipeline Modes"""

from enum import Enum


class PipelineMode(str, Enum):
    """Pipeline modelling modes for data2rdf"""

    TBOX = "tbox"
    ABOX = "abox"
