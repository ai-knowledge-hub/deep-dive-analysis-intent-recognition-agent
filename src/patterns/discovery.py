"""
Pattern Discovery Engine - Layer 3 of the architecture.

This module handles the clustering of behavioral sessions to identify latent personas.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from sklearn.cluster import KMeans

from src.intent import IntentTaxonomy
from src.utils import ContextBuilder

# Initialize shared components
CONTEXT_BUILDER = ContextBuilder()

def deserialize_uploaded_data(file_obj_name: Optional[str], file_content: Optional[bytes] = None) -> List[Dict[str, Any]]:
    """
    Parse uploaded file (JSON or CSV) into a list of records.
    
    Args:
        file_obj_name: Name/path of the file (used for extension check or CSV reading)
        file_content: Bytes content of the file (for JSON)
        
    Returns:
        List of dict records
    """
    if not file_obj_name and not file_content:
        return []

    # If content provided (e.g. from Gradio file object read), try JSON
    if file_content:
        try:
            parsed = json.loads(file_content.decode("utf-8"))
            if isinstance(parsed, list):
                return parsed
            if isinstance(parsed, dict):
                return [parsed]
        except json.JSONDecodeError:
            pass

    # Try CSV fallback or file path read
    try:
        path = Path(file_obj_name) if file_obj_name else None
        if path is not None and path.exists():
            if path.suffix.lower() == ".json":
                try:
                    content = path.read_text(encoding="utf-8")
                    parsed = json.loads(content)
                    if isinstance(parsed, list):
                        return parsed
                    if isinstance(parsed, dict):
                        return [parsed]
                except json.JSONDecodeError:
                    pass

            df = pd.read_csv(path)
            records = df.to_dict(orient="records")
            normalized: List[Dict[str, Any]] = []
            for row in records:
                normalized.append({str(k): v for k, v in row.items()})
            return normalized
    except Exception:
        pass
        
    return []


def build_feature_dataframe(records: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Transform raw records into a feature DataFrame for clustering.
    """
    rows: List[Dict[str, Any]] = []

    for record in records:
        # Use ContextBuilder to normalize signals
        context = CONTEXT_BUILDER.build_context(
            user_query=record.get("user_query", ""),
            page_type=record.get("page_type", ""),
            previous_actions=record.get("previous_actions", ""),
            time_on_page=int(record.get("time_on_page", 0) or 0),
            session_history=record.get("session_history", ""),
        )

        behavioral = context["behavioral_signals"]
        constraints = context["constraint_signals"]

        rows.append(
            {
                "name": record.get("name", ""),
                "user_query": record.get("user_query", ""),
                "page_type": record.get("page_type", ""),
                "time_on_page": behavioral.get("time_on_page_seconds", 0),
                "actions_count": len(behavioral.get("actions_taken", [])),
                "engagement_level": behavioral.get("engagement_level", "unknown"),
                "has_budget_constraint": constraints.get("has_budget_constraint", False),
                "has_time_constraint": constraints.get("has_time_constraint", False),
                "has_knowledge_gap": constraints.get("has_knowledge_gap", False),
                "expected_intent": record.get("expected_intent", record.get("intent", "")),
            }
        )

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    # Numerical encoding for clustering
    engagement_map = {"very_low": 0, "low": 1, "medium": 2, "high": 3, "very_high": 4}
    df["engagement_score"] = df["engagement_level"].map(engagement_map).fillna(0)
    df["budget_flag"] = df["has_budget_constraint"].astype(int)
    df["time_flag"] = df["has_time_constraint"].astype(int)
    df["knowledge_flag"] = df["has_knowledge_gap"].astype(int)

    return df


def _persona_name_from_signals(intent: str, subset: pd.DataFrame) -> str:
    """Generate a descriptive name for the persona based on dominant signals."""
    intent = intent or "unknown"
    adjective = "Contextual"
    if subset["budget_flag"].mean() > 0.5:
        adjective = "Value-Driven"
    elif subset["time_flag"].mean() > 0.5:
        adjective = "Urgency-Focused"
    elif subset["engagement_score"].mean() > 2.5:
        adjective = "Research-Heavy"
    return f"{adjective} {intent.replace('_', ' ').title()}"


def run_pattern_discovery(
    records: List[Dict[str, Any]],
    cluster_count: int,
    taxonomy: Optional[IntentTaxonomy] = None
) -> Tuple[pd.DataFrame, str, str]:
    """
    Cluster behavioral sessions and return summaries + persona JSON.
    
    Args:
        records: List of session records
        cluster_count: Number of clusters to find
        taxonomy: Optional taxonomy for recommendations
        
    Returns:
        Tuple of (summary_dataframe, persona_json_string, markdown_summary)
    """
    if not records:
        return pd.DataFrame(), "No data provided.", ""

    df = build_feature_dataframe(records)
    if df.empty:
        return pd.DataFrame(), "Unable to parse data.", ""

    numeric_cols = ["time_on_page", "actions_count", "engagement_score", "budget_flag", "time_flag", "knowledge_flag"]
    # Ensure columns exist
    for col in numeric_cols:
        if col not in df.columns:
            df[col] = 0
            
    feature_matrix = df[numeric_cols].to_numpy(dtype=float)

    k = min(max(2, cluster_count), len(df))
    if len(df) < 2:
        return df, "Need at least two sessions to detect patterns.", ""

    model = KMeans(n_clusters=k, n_init="auto", random_state=42)
    labels = model.fit_predict(feature_matrix)
    df["cluster"] = labels

    summary_rows: List[Dict[str, Any]] = []
    personas: List[Dict[str, Any]] = []

    for cluster_id in sorted(df["cluster"].unique()):
        subset = df[df["cluster"] == cluster_id]
        
        # Find dominant intent safely
        dominant_intent = "unknown"
        if "expected_intent" in subset.columns and not subset["expected_intent"].dropna().empty:
            dominant_intent = subset["expected_intent"].mode().iloc[0]
            
        persona_name = _persona_name_from_signals(dominant_intent, subset)
        
        summary_rows.append(
            {
                "cluster_id": int(cluster_id),
                "sessions": len(subset),
                "avg_time_on_page": float(subset["time_on_page"].mean()),
                "avg_actions": float(subset["actions_count"].mean()),
                "engagement_mode": subset["engagement_level"].mode().iloc[0] if not subset["engagement_level"].empty else "unknown",
                "dominant_intent": dominant_intent,
            }
        )

        personas.append(
            {
                "persona_name": persona_name,
                "dominant_intent": dominant_intent,
                "sessions": len(subset),
                "key_signals": {
                    "engagement": subset["engagement_level"].mode().iloc[0] if not subset["engagement_level"].empty else "unknown",
                    "budget_focus": float(subset["budget_flag"].mean()),
                    "urgency": float(subset["time_flag"].mean()),
                },
                "recommended_actions": taxonomy.get_recommended_actions(dominant_intent) if taxonomy else [],
            }
        )

    summary_df = pd.DataFrame(summary_rows)
    persona_json = json.dumps(personas, indent=2)
    
    markdown = "\n".join(
        f"**Cluster {row['cluster_id']} – {row['dominant_intent'] or 'unknown'}**: "
        f"{row['sessions']} sessions, avg actions {row['avg_actions']:.1f}, "
        f"engagement {row['engagement_mode']}"
        for row in summary_rows
    )

    return summary_df, persona_json, markdown
