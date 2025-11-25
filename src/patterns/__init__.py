"""Pattern discovery module - Layer 3 of the CCIA system."""

from .embedder import BehavioralEmbedder
from .clustering import PatternClusterer
from .analyzer import PatternAnalyzer
from .discovery import (
    deserialize_uploaded_data,
    build_feature_dataframe,
    run_pattern_discovery,
)
from .visualizer import (
    plot_clusters,
    plot_cluster_statistics,
    create_pattern_summary_text
)

__all__ = [
    "BehavioralEmbedder",
    "PatternClusterer",
    "PatternAnalyzer",
    "deserialize_uploaded_data",
    "build_feature_dataframe",
    "run_pattern_discovery",
    "plot_clusters",
    "plot_cluster_statistics",
    "create_pattern_summary_text",
]
