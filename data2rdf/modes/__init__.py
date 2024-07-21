"""Data2RDF Pipeline Modes"""

from enum import Enum


class PipelineMode(str, Enum):
    """Pipeline modelling modes for data2rdf"""

    tbox = "T Box Modelling"
    abox = "A Box Modelling"
