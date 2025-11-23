"""
Tests for the Pattern Discovery Engine.
"""

import json
import tempfile
from pathlib import Path

import pandas as pd
from src.patterns.discovery import (
    deserialize_uploaded_data,
    build_feature_dataframe,
    run_pattern_discovery,
    _persona_name_from_signals
)

# Mock data
SAMPLE_RECORDS = [
    {
        "user_query": "best running shoes",
        "page_type": "category",
        "previous_actions": "viewed_product,read_reviews",
        "time_on_page": 120,
        "session_history": '[{"intent": "research_category"}]',
        "expected_intent": "research_category"
    },
    {
        "user_query": "cheap sneakers",
        "page_type": "search_results",
        "previous_actions": "filter_price_low",
        "time_on_page": 45,
        "session_history": "",
        "expected_intent": "price_discovery"
    },
    {
        "user_query": "buy nike pegasus now",
        "page_type": "product_detail",
        "previous_actions": "add_to_cart",
        "time_on_page": 300,
        "session_history": "",
        "expected_intent": "ready_to_purchase"
    }
]

def test_deserialize_json():
    """Test deserializing JSON data."""
    data = json.dumps(SAMPLE_RECORDS)
    records = deserialize_uploaded_data(None, data.encode("utf-8"))
    assert len(records) == 3
    assert records[0]["user_query"] == "best running shoes"

def test_deserialize_csv():
    """Test deserializing CSV file."""
    df = pd.DataFrame(SAMPLE_RECORDS)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        df.to_csv(f, index=False)
        temp_path = f.name
    
    try:
        records = deserialize_uploaded_data(temp_path)
        assert len(records) == 3
        assert records[0]["user_query"] == "best running shoes"
    finally:
        Path(temp_path).unlink()

def test_build_feature_dataframe():
    """Test feature extraction."""
    df = build_feature_dataframe(SAMPLE_RECORDS)
    
    assert not df.empty
    assert len(df) == 3
    assert "engagement_score" in df.columns
    assert "budget_flag" in df.columns
    
    # Check specific feature logic
    # "cheap sneakers" should have budget flag
    budget_row = df[df["user_query"] == "cheap sneakers"].iloc[0]
    assert budget_row["budget_flag"] == 1

def test_persona_naming():
    """Test persona naming logic."""
    df = pd.DataFrame([
        {"budget_flag": 1, "time_flag": 0, "engagement_score": 1},
        {"budget_flag": 1, "time_flag": 0, "engagement_score": 1}
    ])
    name = _persona_name_from_signals("test_intent", df)
    assert "Value-Driven" in name

def test_run_pattern_discovery():
    """Test full pipeline."""
    # Need at least 2 records for clustering
    records = SAMPLE_RECORDS * 2
    
    summary_df, persona_json, markdown = run_pattern_discovery(records, cluster_count=2)
    
    assert not summary_df.empty
    assert len(summary_df) <= 2  # Should have at most 2 clusters
    assert "cluster_id" in summary_df.columns
    
    personas = json.loads(persona_json)
    assert isinstance(personas, list)
    assert len(personas) > 0
    assert "persona_name" in personas[0]
    
    assert markdown.startswith("**Cluster")
