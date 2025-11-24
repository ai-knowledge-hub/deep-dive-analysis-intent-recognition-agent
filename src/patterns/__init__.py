"""Pattern discovery module - Layer 3 of the CCIA system."""

from .embedder import BehavioralEmbedder
from .clustering import PatternClusterer
from .analyzer import PatternAnalyzer
from .visualizer import (
    plot_clusters,
    plot_cluster_statistics,
    create_pattern_summary_text
)

__all__ = [
    "BehavioralEmbedder",
    "PatternClusterer",
    "PatternAnalyzer",
    "plot_clusters",
    "plot_cluster_statistics",
    "create_pattern_summary_text",
]
