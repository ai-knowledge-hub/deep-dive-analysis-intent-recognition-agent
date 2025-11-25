import json
from pathlib import Path

import pandas as pd

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.patterns.discovery import (  # noqa: E402
    deserialize_uploaded_data,
    build_feature_dataframe,
    run_pattern_discovery,
)
from src.intent import IntentTaxonomy  # noqa: E402


def test_deserialize_uploaded_data_handles_json(tmp_path):
    sample = [{"user_query": "test", "page_type": "product_detail"}]
    file_path = tmp_path / "sample.json"
    file_path.write_text(json.dumps(sample), encoding="utf-8")

    records = deserialize_uploaded_data(str(file_path), file_path.read_bytes())
    assert len(records) == 1
    assert records[0]["user_query"] == "test"


def test_build_feature_dataframe_creates_numeric_columns():
    records = [
        {
            "user_query": "running shoes",
            "page_type": "product_detail",
            "previous_actions": "viewed_product,read_reviews",
            "time_on_page": 120,
        }
    ]
    df = build_feature_dataframe(records)
    assert isinstance(df, pd.DataFrame)
    assert "time_on_page" in df.columns
    assert "engagement_score" in df.columns


def test_run_pattern_discovery_returns_summary_and_personas():
    records = [
        {
            "name": "User A",
            "user_query": "cheap running shoes",
            "page_type": "search_results",
            "previous_actions": "filtered_by_price",
            "time_on_page": 60,
        },
        {
            "name": "User B",
            "user_query": "best marathon shoes",
            "page_type": "product_detail",
            "previous_actions": "read_reviews,checked_shipping",
            "time_on_page": 200,
        },
    ]
    taxonomy = IntentTaxonomy.from_domain("ecommerce")
    summary_df, persona_json, markdown = run_pattern_discovery(
        records=records,
        cluster_count=2,
        taxonomy=taxonomy,
    )

    assert not summary_df.empty
    personas = json.loads(persona_json)
    assert len(personas) >= 1
    assert isinstance(markdown, str)
