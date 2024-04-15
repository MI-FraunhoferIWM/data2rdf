"""Data2rdf pipelines"""

from .abox_scaffolding_pipeline import ABoxScaffoldPipeline
from .annotation_pipeline import AnnotationPipeline

__all__ = ["AnnotationPipeline", "ABoxScaffoldPipeline"]
