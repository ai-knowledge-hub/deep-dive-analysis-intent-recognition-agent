"""Gradio application for the Context-Conditioned Intent Recognition Agent.

This UI mirrors the architecture in docs/article.md by exposing:
1. Intent Analyzer – interactive playground for CCIA intent recognition
2. Pattern Discovery – lightweight clustering of behavioral sessions
3. MCP/API Guide – how to use the Track 1 MCP server + future integrations
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import gradio as gr
from dotenv import load_dotenv

from src.intent import IntentRecognitionEngine, IntentTaxonomy, LLMProviderFactory
from src.utils import ContextBuilder
from tools.pattern_discovery_mcp import discover_behavioral_patterns


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
        f"Details: {exc}\n\nSet ANTHROPIC_API_KEY, OPENAI_API_KEY, or OPENROUTER_API_KEY in your environment."
    )


SAMPLE_CONTEXT_PATH = Path("data/sample_contexts.json")
PATTERN_SAMPLE_PATH = Path("data/sample_user_histories.csv")
ARTICLE_URL = "https://ai-news-hub.performics-labs.com/analysis/geometry-of-intention-llms-human-goals-marketing"
CONTEXT_BUILDER = ContextBuilder()


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

def summarize_context_layers(context: Dict[str, Any]) -> str:
    """Create a human-readable summary of the context builder output."""
    identity = context.get("identity_context", {})
    historical = context.get("historical_context", {})
    situational = context.get("situational_context", {})
    behavioral = context.get("behavioral_signals", {})
    temporal = context.get("temporal_signals", {})
    constraints = context.get("constraint_signals", {})

    def bool_to_str(val: Any) -> str:
        return "Yes" if val else "No"

    sections = [
        f"**Identity**: role = `{identity.get('inferred_role', 'unknown')}`, "
        f"device = `{identity.get('device_type', 'unknown')}`, "
        f"returning = {bool_to_str(identity.get('is_returning_user'))}",
        f"**History**: {historical.get('previous_session_count', 0)} prior sessions, "
        f"actions this session = {historical.get('action_count', 0)}, "
        f"past intents = {', '.join(historical.get('past_intents', []) or ['n/a'])}",
        f"**Situation**: page = `{situational.get('page_type', 'unknown')}`, "
        f"channel = `{situational.get('channel', 'unknown')}`, "
        f"traffic = `{situational.get('traffic_source', 'unknown')}`",
        f"**Behavior**: query = `{behavioral.get('current_query', '') or 'n/a'}`, "
        f"engagement = `{behavioral.get('engagement_level', 'unknown')}`, "
        f"actions taken = {len(behavioral.get('actions_taken', []))}",
        f"**Temporal**: session #{temporal.get('session_number', 1)}, "
        f"hour = {temporal.get('hour_of_day', 'n/a')}, "
        f"is weekend = {bool_to_str(temporal.get('is_weekend'))}",
        f"**Constraints**: budget = {bool_to_str(constraints.get('has_budget_constraint'))}, "
        f"time = {bool_to_str(constraints.get('has_time_constraint'))}, "
        f"knowledge gap = {bool_to_str(constraints.get('has_knowledge_gap'))}",
    ]

    return "\n".join(sections)


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
) -> Tuple[str, str, Dict[str, Any], str]:
    """Run the intent recognition engine and return JSON + markdown summary + context."""

    if ENGINE is None:
        error_json = json.dumps({"error": True, "message": ENGINE_ERROR or ""}, indent=2)
        return error_json, ENGINE_ERROR or "", {}, ""

    # Build context preview (Layer 1)
    context_view = CONTEXT_BUILDER.build_context(
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
    context_summary = summarize_context_layers(context_view)

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
        error_payload = json.dumps({"error": True, "message": str(exc)}, indent=2)
        return error_payload, f"Engine error: {exc}", context_view, context_summary

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

    return json.dumps(result, indent=2), "\n".join(summary), context_view, context_summary


# ---------------------------------------------------------------------------
# Pattern discovery helpers (MCP-aligned)
# ---------------------------------------------------------------------------

def _resolve_dataset_path(use_sample: bool, uploaded_path: Optional[str]) -> Optional[str]:
    """Pick the CSV path to send into the MCP pipeline."""
    if use_sample or not uploaded_path:
        if PATTERN_SAMPLE_PATH.exists():
            return str(PATTERN_SAMPLE_PATH)
        return None
    if uploaded_path and Path(uploaded_path).exists():
        return uploaded_path
    return None


def _apply_dataset_preset(preset: str) -> Tuple[int, int]:
    """Map dataset presets to recommended HDBSCAN parameters."""
    if "Full Traffic" in preset:
        return 40, 10
    return 12, 4


def run_pattern_discovery_full(
    csv_file_path: Optional[str],
    use_sample_csv: bool,
    min_cluster_size: int,
    min_samples: int,
    use_llm_personas: bool,
    llm_provider: str,
) -> Tuple[str, Any, Optional[str], Optional[str]]:
    """
    Execute the full behavioral pattern discovery pipeline used by the MCP tool.

    Returns:
        summary_markdown, personas_json_obj, cluster_plot_path, stats_plot_path
    """
    resolved_path = _resolve_dataset_path(use_sample_csv, csv_file_path)
    if not resolved_path:
        return (
            "❌ Provide a CSV file or enable the bundled sample dataset.",
            [],
            None,
            None,
        )

    try:
        summary, personas_json, cluster_plot, stats_plot = discover_behavioral_patterns(
            csv_file=resolved_path,
            min_cluster_size=min_cluster_size,
            min_samples=min_samples,
            use_llm_personas=use_llm_personas,
            llm_provider=llm_provider,
        )
    except Exception as exc:  # noqa: BLE001
        return (f"❌ Pattern discovery failed:\n\n{exc}", [], None, None)

    try:
        personas_obj = json.loads(personas_json) if personas_json else []
    except json.JSONDecodeError:
        personas_obj = {"raw": personas_json or "[]"}

    return summary, personas_obj, (cluster_plot or None), (stats_plot or None)

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
                gr.Markdown(
                    f"[Layer 2: Intent Recognition]({ARTICLE_URL}) — research deep dive on how structured context activates LLM intent prediction.",
                    elem_classes=["doc-link"],
                )

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
            with gr.Row():
                context_json = gr.JSON(label="Layer 1 Context (5D capture)")
                context_summary = gr.Markdown(
                    label="Context Highlights",
                    value="Run an analysis to preview the structured context feeding the LLM.",
                )

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
                outputs=[intent_json, intent_summary, context_json, context_summary],
            )

        with gr.Tab("Pattern Discovery"):
            gr.Markdown(
                "Run the same Layer 3 pipeline used by the MCP tool: CSV → behavioral embeddings → HDBSCAN → LLM personas."
            )
            gr.Markdown(
                f"[Layer 3: Pattern Discovery]({ARTICLE_URL}) — see how embeddings + HDBSCAN uncover intentional archetypes.",
                elem_classes=["doc-link"],
            )
            csv_input = gr.File(
                label="Upload User Sessions CSV",
                file_types=[".csv"],
                file_count="single",
                type="filepath",
                interactive=True,
            )
            use_sample_csv = gr.Checkbox(
                label="Use bundled sample data (40 users, 3 patterns)",
                value=True,
                info="Disable to rely solely on your uploaded CSV.",
            )

            dataset_preset = gr.Radio(
                label="Data Size Preset",
                choices=["Small Sample (≤200 users)", "Full Traffic (1000+ users)"],
                value="Small Sample (≤200 users)",
                info="Presets adjust min_cluster_size / min_samples to match your dataset scale.",
            )

            min_cluster_size = gr.Slider(
                label="Minimum Cluster Size",
                minimum=5,
                maximum=100,
                step=5,
                value=12,
                info="Lower values = more clusters (recommended for the sample CSV).",
            )
            min_samples = gr.Slider(
                label="Minimum Samples",
                minimum=1,
                maximum=20,
                step=1,
                value=4,
                info="Higher values = stricter, more stable clusters.",
            )

            use_llm_personas = gr.Checkbox(
                label="Generate LLM Personas",
                value=True,
                info="Requires ANTHROPIC_API_KEY, OPENAI_API_KEY, or OPENROUTER_API_KEY.",
            )
            llm_provider = gr.Radio(
                label="LLM Provider",
                choices=["anthropic", "openai", "openrouter"],
                value="anthropic",
            )

            discover_button = gr.Button("🚀 Run Pattern Pipeline", variant="primary")

            summary_output = gr.Markdown("Upload data and click run to see CCIA personas.")
            personas_output = gr.JSON(label="Generated Personas")
            cluster_plot = gr.Image(
                label="Cluster Visualization",
                type="filepath",
                interactive=False,
            )
            stats_plot = gr.Image(
                label="Pattern Statistics",
                type="filepath",
                interactive=False,
            )

            dataset_preset.change(
                fn=_apply_dataset_preset,
                inputs=dataset_preset,
                outputs=[min_cluster_size, min_samples],
            )

            discover_button.click(
                fn=run_pattern_discovery_full,
                inputs=[
                    csv_input,
                    use_sample_csv,
                    min_cluster_size,
                    min_samples,
                    use_llm_personas,
                    llm_provider,
                ],
                outputs=[summary_output, personas_output, cluster_plot, stats_plot],
            )

        with gr.Tab("Activation Playbooks"):
            gr.Markdown(
                """
                ### Layer 4 – Activation

                Turn Layer 2 + Layer 3 insights into marketing actions. These playbooks map directly to the CCIA research article and highlight how to operationalize intent + pattern signals.
                """
            )
            gr.Markdown(
                f"[Layer 4: Activation Guidance]({ARTICLE_URL}) — scroll to the activation section of the article for the full strategy.",
            )
            with gr.Row():
                gr.Markdown(
                    """
                    #### 🎯 Bid & Budget Modifiers
                    - Tie `primary_intent` confidence to bid uplifts or suppressions.
                    - Pair persona-level conversion probabilities with budget caps.
                    - Export persona cohorts to ad platforms for intent-aware bidding.
                    """,
                    elem_id="activation-bids",
                )
                gr.Markdown(
                    """
                    #### 👥 Audience Segmentation
                    - Promote resilient patterns (>30% stability) into always-on audiences.
                    - Sync personas to CRM/CDP segments for cross-channel orchestration.
                    - Monitor cluster drift weekly using the MCP pattern tool.
                    """,
                    elem_id="activation-audiences",
                )
            with gr.Row():
                gr.Markdown(
                    """
                    #### 🧩 Content Personalization
                    - Map behavioral evidence to modular creatives (guides, demos, offers).
                    - Use constraint signals (budget/time/knowledge) to swap callouts.
                    - Trigger onsite personalization via the same context payload surfaced above.
                    """,
                    elem_id="activation-content",
                )
                gr.Markdown(
                    """
                    #### 🔁 Next-Best Actions
                    - Feed predicted next actions into marketing automation journeys.
                    - Combine persona intents with channel preference (situational context) to choose push/email/ad cadence.
                    - Record feedback loops: did the suggested action happen? retrain heuristics monthly.
                    """,
                    elem_id="activation-next",
                )

        with gr.Tab("MCP & API Guide"):
            gr.Markdown(
                """
                ### MCP + API Guide

                Monitor and launch the standalone MCP servers used for Track 1 submissions. Each server exposes a Gradio MCP endpoint compatible with Cursor, Claude Desktop, and ChatGPT (OpenAI Apps).
                """
            )

            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### Intent Recognition MCP (port 7860)")
                    gr.Markdown(
                        "- Script: `python tools/intent_recognition_mcp.py`\n"
                        "- Tool name: `recognize_intent`\n"
                        "- Endpoint: `http://localhost:7860/gradio_api/mcp/sse`"
                    )
                with gr.Column():
                    gr.Markdown("#### Pattern Discovery MCP (port 7861)")
                    gr.Markdown(
                        "- Script: `python tools/pattern_discovery_mcp.py`\n"
                        "- Tool name: `discover_behavioral_patterns`\n"
                        "- Endpoint: `http://localhost:7861/gradio_api/mcp/sse`"
                    )

            gr.Markdown("#### Cursor / Claude Config Snippets")
            config_tabs = gr.Tabs()
            with config_tabs:
                with gr.TabItem("Cursor JSON"):
                    cursor_config = gr.Code(
                        value="""
{
  "mcpServers": {
    "intent-recognition": {
      "url": "http://localhost:7860/gradio_api/mcp/sse"
    },
    "pattern-discovery": {
      "url": "http://localhost:7861/gradio_api/mcp/sse"
    }
  }
}
""".strip(),
                        language="json",
                        interactive=False,
                        label="cursor.json snippet",
                    )
                with gr.TabItem("Claude Desktop"):
                    claude_config = gr.Code(
                        value="""
{
  "mcpServers": {
    "intent-recognition": {
      "command": "python",
      "args": ["tools/intent_recognition_mcp.py"],
      "port": 7860
    },
    "pattern-discovery": {
      "command": "python",
      "args": ["tools/pattern_discovery_mcp.py"],
      "port": 7861
    }
  }
}
""".strip(),
                        language="json",
                        interactive=False,
                        label="claude_desktop_config.json snippet",
                    )

            gr.Markdown(
                """
                1. Start each MCP server (or click the buttons in your terminal session).
                2. Paste the snippet into your IDE/assistant configuration.
                3. Use the named tools (`recognize_intent`, `discover_behavioral_patterns`) directly inside Cursor, Claude Desktop, or ChatGPT (post-hackathon).
                """
            )


if __name__ == "__main__":
    demo.launch()
