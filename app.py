"""Gradio application for the Context-Conditioned Intent Recognition Agent.

This UI mirrors the architecture in docs/article.md by exposing:
1. Intent Analyzer – interactive playground for CCIA intent recognition
2. Pattern Discovery – lightweight clustering of behavioral sessions
3. MCP/API Guide – how to use the Track 1 MCP server + future integrations
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import gradio as gr
import pandas as pd
from dotenv import load_dotenv

from src.intent import IntentRecognitionEngine, IntentTaxonomy, LLMProviderFactory
from src.utils import ContextBuilder
from src.patterns import run_pattern_discovery, deserialize_uploaded_data


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------

load_dotenv()

ENGINE_ERROR: Optional[str] = None
ENGINE: Optional[IntentRecognitionEngine] = None
TAXONOMY: Optional[IntentTaxonomy] = None

try:
    llm_provider = LLMProviderFactory.create_from_env()
    TAXONOMY = IntentTaxonomy.from_domain("ecommerce")
    ENGINE = IntentRecognitionEngine(llm_provider=llm_provider, taxonomy=TAXONOMY)
except Exception as exc:  # noqa: BLE001 - surface config errors to UI
    ENGINE_ERROR = (
        "Unable to initialize the Intent Recognition Engine.\n\n" \
        f"Details: {exc}\n\nSet ANTHROPIC_API_KEY or OPENAI_API_KEY in your environment."
    )


CONTEXT_BUILDER = ContextBuilder()
SAMPLE_CONTEXT_PATH = Path("data/sample_contexts.json")


def _load_sample_contexts() -> List[Dict[str, Any]]:
    if not SAMPLE_CONTEXT_PATH.exists():
        return []
    with SAMPLE_CONTEXT_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


SAMPLE_CONTEXTS = _load_sample_contexts()
SAMPLE_LOOKUP = {sample["name"]: sample for sample in SAMPLE_CONTEXTS}


# ---------------------------------------------------------------------------
# Intent Analyzer helpers
# ---------------------------------------------------------------------------

def load_sample_values(sample_name: str) -> Tuple[str, str, str, int, str]:
    """Return field defaults for the selected sample scenario."""

    sample = SAMPLE_LOOKUP.get(sample_name)
    if not sample:
        return "", "product_detail", "", 90, ""

    return (
        sample.get("user_query", ""),
        sample.get("page_type", "product_detail"),
        sample.get("previous_actions", ""),
        int(sample.get("time_on_page", 60) or 0),
        sample.get("session_history", ""),
    )


def analyze_intent(
    user_query: str,
    page_type: str,
    previous_actions: str,
    time_on_page: int,
    session_history: str,
    device_type: str,
    traffic_source: str,
    scroll_depth: float,
    clicks_count: int,
) -> Tuple[str, str]:
    """Run the intent recognition engine and return JSON + markdown summary."""

    if ENGINE is None:
        return json.dumps({"error": True, "message": ENGINE_ERROR or ""}, indent=2), ENGINE_ERROR or ""

    try:
        result = ENGINE.recognize_intent(
            user_query=user_query,
            page_type=page_type,
            previous_actions=previous_actions,
            time_on_page=time_on_page,
            session_history=session_history,
            device_type=device_type,
            traffic_source=traffic_source,
            scroll_depth=scroll_depth,
            clicks_count=clicks_count,
        )
    except Exception as exc:  # noqa: BLE001
        return json.dumps({"error": True, "message": str(exc)}, indent=2), f"Engine error: {exc}"

    summary = [
        f"**Primary Intent:** {result.get('primary_intent', 'unknown').replace('_', ' ').title()}",
        f"**Confidence:** {result.get('confidence', 0.0):.0%}",
        f"**Bid Modifier:** {result.get('bid_modifier_suggestion', 0.0):+0.0%}",
        f"**Conversion Probability:** {result.get('conversion_probability', 0.0):.0%}",
    ]

    recs = result.get("recommended_marketing_actions", [])
    if recs:
        summary.append("\n**Recommended Actions:**" + "\n" + "\n".join(f"- {item}" for item in recs[:4]))

    nxt = result.get("predicted_next_actions", [])
    if nxt:
        summary.append("\n**Predicted Next Actions:**" + "\n" + "\n".join(f"- {item}" for item in nxt[:3]))

    return json.dumps(result, indent=2), "\n".join(summary)


# ---------------------------------------------------------------------------
# Pattern discovery helpers
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Pattern discovery helpers
# ---------------------------------------------------------------------------

def run_pattern_discovery_callback(
    uploaded_file: Optional[gr.File],
    include_sample_data: bool,
    cluster_count: int,
) -> Tuple[pd.DataFrame, str, str]:
    """Cluster behavioral sessions and return summaries + persona JSON."""

    records: List[Dict[str, Any]] = []

    if include_sample_data:
        records.extend(SAMPLE_CONTEXTS)

    if uploaded_file:
        try:
            file_path = Path(uploaded_file.name)
            file_bytes = file_path.read_bytes()
            records.extend(deserialize_uploaded_data(str(file_path), file_bytes))
        except Exception as e:  # noqa: BLE001
            return pd.DataFrame(), f"Error parsing file: {e}", ""

    if not records:
        return pd.DataFrame(), "No data provided. Upload JSON/CSV or include samples.", ""

    try:
        summary_df, persona_json, markdown = run_pattern_discovery(
            records=records,
            cluster_count=cluster_count,
            taxonomy=TAXONOMY,
        )
        return summary_df, persona_json, markdown
    except Exception as e:  # noqa: BLE001
        return pd.DataFrame(), f"Error during pattern discovery: {e}", ""

# ---------------------------------------------------------------------------
# Gradio Interface
# ---------------------------------------------------------------------------

with gr.Blocks(title="Context-Conditioned Intent Recognition", analytics_enabled=True) as demo:
    gr.Markdown(
        """
        # 🎯 Context-Conditioned Intent Recognition Agent
        Translate behavioral context into marketing intent insights. Built for the Gradio × Anthropic MCP Hackathon.
        """
    )

    if ENGINE_ERROR:
        gr.Markdown(f"⚠️ **Engine not initialized:** {ENGINE_ERROR}")

    with gr.Tabs():
        with gr.Tab("Intent Analyzer"):
            with gr.Row():
                sample_dropdown = gr.Dropdown(
                    choices=list(SAMPLE_LOOKUP.keys()),
                    label="Load Sample Scenario",
                    value=None,
                    interactive=True,
                )
                gr.Markdown("Select a sample to auto-fill the form, or enter custom signals below.")

            with gr.Row():
                user_query = gr.Textbox(label="User Query", lines=2)
                page_type = gr.Dropdown(
                    label="Page Type",
                    choices=[
                        "product_detail",
                        "category",
                        "search_results",
                        "cart",
                        "checkout",
                        "homepage",
                        "blog_post",
                        "comparison_page",
                    ],
                    value="product_detail",
                )

            previous_actions = gr.Textbox(
                label="Previous Actions",
                placeholder="viewed_product,read_reviews,clicked_size_guide",
            )
            time_on_page = gr.Slider(label="Time on Page (seconds)", minimum=0, maximum=600, step=5, value=120)
            session_history = gr.Textbox(
                label="Session History (JSON)", lines=3, placeholder='[{"intent": "compare_options"}]'
            )

            with gr.Accordion("Advanced Signals", open=False):
                device_type = gr.Dropdown(
                    label="Device Type", choices=["desktop", "mobile", "tablet"], value="desktop"
                )
                traffic_source = gr.Dropdown(
                    label="Traffic Source",
                    choices=["direct", "search_google", "social_meta", "email", "affiliate"],
                    value="direct",
                )
                scroll_depth = gr.Slider(label="Scroll Depth (%)", minimum=0, maximum=100, step=5, value=50)
                clicks_count = gr.Slider(label="Clicks This Session", minimum=0, maximum=20, step=1, value=3)

            analyze_button = gr.Button("Analyze Intent", variant="primary")
            intent_json = gr.JSON(label="Intent Analysis JSON")
            intent_summary = gr.Markdown(label="Summary")

            def _populate_sample(sample_name: str):  # noqa: ANN001
                return load_sample_values(sample_name)

            sample_dropdown.change(
                _populate_sample,
                inputs=[sample_dropdown],
                outputs=[user_query, page_type, previous_actions, time_on_page, session_history],
            )

            analyze_button.click(
                analyze_intent,
                inputs=[
                    user_query,
                    page_type,
                    previous_actions,
                    time_on_page,
                    session_history,
                    device_type,
                    traffic_source,
                    scroll_depth,
                    clicks_count,
                ],
                outputs=[intent_json, intent_summary],
            )

        with gr.Tab("Pattern Discovery"):
            gr.Markdown("Upload behavioral sessions or use our samples to surface latent personas.")
            upload = gr.File(label="Upload JSON/CSV of sessions", file_types=[".json", ".csv"], file_count="single")
            include_samples = gr.Checkbox(label="Include sample sessions", value=True)
            cluster_slider = gr.Slider(label="Cluster Count", minimum=2, maximum=6, step=1, value=3)
            cluster_button = gr.Button("Generate Patterns", variant="primary")
            cluster_df = gr.Dataframe(label="Cluster Summary", interactive=False)
            persona_json = gr.JSON(label="Persona JSON")
            persona_md = gr.Markdown()

            cluster_button.click(
                run_pattern_discovery_callback,
                inputs=[upload, include_samples, cluster_slider],
                outputs=[cluster_df, persona_json, persona_md],
            )

        with gr.Tab("MCP & API Guide"):
            gr.Markdown(API_MD)


if __name__ == "__main__":
    demo.launch()
