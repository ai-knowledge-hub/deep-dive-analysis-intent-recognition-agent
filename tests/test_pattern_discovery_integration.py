"""
Integration Tests for Pattern Discovery Pipeline.

Tests the full flow:
1. Data Parsing
2. Embeddings (Mocked)
3. Clustering (Mocked/Real)
4. Analysis (Mocked LLM)
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, patch
from src.utils.data_parsers import parse_user_histories_from_csv, parse_user_histories_from_json
from src.patterns.embedder import BehavioralEmbedder
from src.patterns.clustering import PatternClusterer
from src.patterns.analyzer import PatternAnalyzer

# Sample Data
SAMPLE_CSV = """user_id,session_intent,confidence,timestamp,channel,engagement_level,has_budget_constraint,has_time_constraint,has_knowledge_gap,urgency_level,expertise_level
user_1,research,0.9,2025-01-01,organic,high,false,false,false,low,novice
user_1,compare,0.8,2025-01-02,organic,high,false,false,false,low,novice
user_2,buy,0.95,2025-01-01,direct,medium,true,true,false,high,expert
"""

SAMPLE_JSON = """[
    {
        "user_id": "user_1",
        "history": [
            {"intent": "research", "confidence": 0.9},
            {"intent": "compare", "confidence": 0.8}
        ]
    },
    {
        "user_id": "user_2",
        "history": [
            {"intent": "buy", "confidence": 0.95}
        ]
    }
]"""

def test_csv_parsing():
    histories, user_ids = parse_user_histories_from_csv(SAMPLE_CSV)
    assert len(histories) == 2
    assert user_ids == ["user_1", "user_2"]
    assert len(histories[0]) == 2  # user_1 has 2 sessions
    assert histories[0][0]["intent"] == "research"

def test_json_parsing():
    histories, user_ids = parse_user_histories_from_json(SAMPLE_JSON)
    assert len(histories) == 2
    assert user_ids == ["user_1", "user_2"]
    assert len(histories[0]) == 2
    assert histories[0][0]["intent"] == "research"

@patch("src.patterns.embedder.SentenceTransformer")
def test_embedder(mock_transformer):
    # Mock the transformer to return fixed embeddings
    mock_model = MagicMock()
    mock_model.get_sentence_embedding_dimension.return_value = 384
    mock_model.encode.return_value = np.zeros(384)
    mock_transformer.return_value = mock_model

    embedder = BehavioralEmbedder()
    histories, _ = parse_user_histories_from_csv(SAMPLE_CSV)
    
    embeddings = embedder.create_batch_embeddings(histories)
    
    # Check shape: (n_users, total_dim)
    # total_dim = 384 + 15 + 5 + 5 = 409
    assert embeddings.shape == (2, 409)

@patch("src.patterns.clustering.HDBSCAN")
def test_clustering(mock_hdbscan):
    # Mock HDBSCAN
    mock_instance = MagicMock()
    mock_instance.labels_ = np.array([0, 1])
    mock_instance.probabilities_ = np.array([0.9, 0.8])
    mock_instance.outlier_scores_ = np.array([0.1, 0.2])
    mock_hdbscan.return_value = mock_instance

    clusterer = PatternClusterer(min_cluster_size=2, min_samples=1)
    embeddings = np.random.rand(2, 409)
    
    # Disable PCA for small sample size
    labels, _ = clusterer.discover_patterns(embeddings, use_pca=False, create_visualization=False)
    
    assert len(labels) == 2
    assert labels[0] == 0
    assert labels[1] == 1

@patch("src.patterns.analyzer.BaseLLMProvider")
def test_analyzer(mock_llm_provider):
    # Mock LLM
    mock_llm = MagicMock()
    mock_llm.generate_sync.return_value = """
    {
        "persona_name": "Test Persona",
        "description": "A test persona",
        "key_characteristics": ["Test"],
        "motivations": ["Testing"],
        "pain_points": ["Bugs"],
        "marketing_insights": ["Fix bugs"],
        "recommended_strategies": ["Unit tests"],
        "content_preferences": ["Logs"],
        "conversion_approach": "Green build",
        "estimated_ltv_multiplier": 1.2,
        "recommended_bid_modifier": 0.1
    }
    """
    
    analyzer = PatternAnalyzer(llm_provider=mock_llm)
    
    # Create fake cluster data
    labels = np.array([0, 0, 1])
    histories = [[{"intent": "buy"}], [{"intent": "buy"}], [{"intent": "browse"}]]
    
    personas = analyzer.analyze_all_clusters(labels, histories)
    
    assert len(personas) == 2  # Clusters 0 and 1
    assert personas[0]["persona"]["persona_name"] == "Test Persona"
