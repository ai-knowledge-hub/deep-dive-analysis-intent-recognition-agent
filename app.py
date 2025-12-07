"""Gradio application for the Context-Conditioned Intent Recognition Agent.

This UI mirrors the architecture in docs/article.md by exposing:
1. Intent Analyzer – interactive playground for CCIA intent recognition
2. Pattern Discovery – lightweight clustering of behavioral sessions
3. MCP/API Guide – how to use the Track 1 MCP server + future integrations
"""

from __future__ import annotations

import json
import os
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import gradio as gr
from dotenv import load_dotenv

from src.activation import (
    ActivationContext,
    IntentSignal,
    IntentAwareBidOptimizer,
    PersonaProfile,
    AudienceCohort,
    default_audience_manager,
    ActivationError,
)
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
BID_OPTIMIZER: Optional[IntentAwareBidOptimizer] = None
BID_OPTIMIZER_ERROR: Optional[str] = None
AUDIENCE_MANAGER = None
AUDIENCE_MANAGER_ERROR: Optional[str] = None

try:
    llm_provider = LLMProviderFactory.create_from_env()
    TAXONOMY = IntentTaxonomy.from_domain("ecommerce")
    ENGINE = IntentRecognitionEngine(llm_provider=llm_provider, taxonomy=TAXONOMY)
except Exception as exc:  # noqa: BLE001 - surface config errors to UI
    ENGINE_ERROR = (
        "Unable to initialize the Intent Recognition Engine.\n\n" \
        f"Details: {exc}\n\nSet ANTHROPIC_API_KEY, OPENAI_API_KEY, or OPENROUTER_API_KEY in your environment."
    )

if TAXONOMY is not None:
    try:
        BID_OPTIMIZER = IntentAwareBidOptimizer(taxonomy=TAXONOMY)
    except Exception as exc:
        BID_OPTIMIZER_ERROR = f"Unable to initialize bid optimizer: {exc}"
else:
    BID_OPTIMIZER_ERROR = "Intent taxonomy not loaded; bid optimizer unavailable."

try:
    AUDIENCE_MANAGER = default_audience_manager()
except Exception as exc:  # noqa: BLE001
    AUDIENCE_MANAGER_ERROR = f"Audience connectors unavailable: {exc}"


SAMPLE_CONTEXT_PATH = Path("data/sample_contexts.json")
PATTERN_SAMPLE_PATH = Path("data/sample_user_histories.csv")
ARTICLE_URL = "https://ai-news-hub.performics-labs.com/analysis/geometry-of-intention-llms-human-goals-marketing"
LLM_PROVIDER_CHOICES = ["anthropic", "openai", "openrouter"]
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


def _normalize_settings(llm_settings: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    settings = llm_settings or {}
    return {
        "enabled": bool(settings.get("enabled")),
        "provider": (settings.get("provider") or "openrouter").lower(),
        "api_key": (settings.get("api_key") or "").strip(),
        "model": (settings.get("model") or "").strip(),
    }


def _resolve_engine(llm_settings: Optional[Dict[str, Any]]) -> Tuple[Optional[IntentRecognitionEngine], Optional[str]]:
    """Use override settings if provided, otherwise return default engine."""
    settings = _normalize_settings(llm_settings)
    if settings["enabled"]:
        provider = settings["provider"] if settings["provider"] in LLM_PROVIDER_CHOICES else "openrouter"
        provider_kwargs: Dict[str, Any] = {}
        if settings["api_key"]:
            provider_kwargs["api_key"] = settings["api_key"]
        if settings["model"]:
            provider_kwargs["model"] = settings["model"]
        try:
            llm = LLMProviderFactory.create(provider_name=provider, **provider_kwargs)
            engine = IntentRecognitionEngine(llm_provider=llm, taxonomy=TAXONOMY)
            return engine, None
        except Exception as exc:
            return None, f"LLM override error: {exc}"

    return ENGINE, ENGINE_ERROR


@contextmanager
def _temporary_llm_env(llm_settings: Optional[Dict[str, Any]]):
    settings = _normalize_settings(llm_settings)
    if not settings["enabled"]:
        yield
        return

    provider = settings["provider"]
    api_key = settings["api_key"]
    model = settings["model"]

    env_map = {
        "anthropic": "ANTHROPIC_API_KEY",
        "openai": "OPENAI_API_KEY",
        "openrouter": "OPENROUTER_API_KEY",
    }
    model_map = {
        "anthropic": "ANTHROPIC_MODEL",
        "openai": "OPENAI_MODEL",
        "openrouter": "OPENROUTER_MODEL",
    }

    overrides: Dict[str, Optional[str]] = {}
    if api_key and provider in env_map:
        overrides[env_map[provider]] = api_key
    if model and provider in model_map:
        overrides[model_map[provider]] = model

    if not overrides:
        yield
        return

    previous = {key: os.environ.get(key) for key in overrides}
    try:
        for key, value in overrides.items():
            if value is not None:
                os.environ[key] = value
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _resolve_llm_provider_choice(llm_settings: Optional[Dict[str, Any]]) -> str:
    """Choose which provider to route persona generation through."""
    settings = _normalize_settings(llm_settings)
    if settings["enabled"] and settings["provider"]:
        return settings["provider"]
    if os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic"
    if os.getenv("OPENAI_API_KEY"):
        return "openai"
    if os.getenv("OPENROUTER_API_KEY"):
        return "openrouter"
    return settings.get("provider", "openrouter")


def _percent_to_ratio(value: Optional[float]) -> Optional[float]:
    """Convert 0-100 slider values to 0-1 ratios."""
    if value is None:
        return None
    return max(0.0, min(1.0, value / 100.0))


def _build_persona_profile(
    name: str,
    description: str,
    size: float,
    share_percent: float,
    conversion_rate_percent: Optional[float],
    ltv_index: Optional[float],
    intent_label: str,
) -> Optional[PersonaProfile]:
    """Build persona profile for bid optimizer inputs."""
    if not name and not description and not conversion_rate_percent and not ltv_index:
        return None

    metrics: Dict[str, float] = {}
    ratio_cvr = _percent_to_ratio(conversion_rate_percent)
    if ratio_cvr is not None:
        metrics["conversion_rate"] = ratio_cvr
    if ltv_index is not None and ltv_index > 0:
        metrics["ltv_index"] = ltv_index

    return PersonaProfile(
        name=name or "Activation Persona",
        description=description or f"Persona derived from {intent_label}",
        size=int(size or 0),
        share=_percent_to_ratio(share_percent) or 0.0,
        intent_distribution={intent_label: 1.0},
        metrics=metrics,
    )


def _parse_identifiers(raw_text: str) -> List[str]:
    """Turn textarea input into distinct user identifiers."""
    if not raw_text:
        return []
    tokens = []
    for chunk in raw_text.replace("\n", ",").split(","):
        cleaned = chunk.strip()
        if cleaned:
            tokens.append(cleaned)
    return tokens


def save_llm_settings(
    enable_custom: bool,
    provider: str,
    api_key: str,
    model: str,
) -> Tuple[Dict[str, Any], str]:
    """Persist LLM settings in a stateful dict."""
    settings = {
        "enabled": bool(enable_custom),
        "provider": (provider or "openrouter").lower(),
        "api_key": (api_key or "").strip(),
        "model": (model or "").strip(),
    }

    if settings["enabled"]:
        if not settings["api_key"]:
            status = "⚠️ Custom mode enabled. Enter an API key to avoid server defaults."
        else:
            status = f"✅ Using custom {settings['provider'].title()} credentials (stored only in this session)."
    else:
        status = "Using server/.env credentials. Enable custom mode to provide your own key."

    return settings, status


def clear_llm_settings() -> Tuple[Dict[str, Any], str]:
    default_settings = {
        "enabled": False,
        "provider": "openrouter",
        "api_key": "",
        "model": "",
    }
    status = "Cleared custom credentials. Falling back to server/.env settings."
    return default_settings, status


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
    llm_settings: Optional[Dict[str, Any]],
) -> Tuple[str, str, Dict[str, Any], str]:
    """Run the intent recognition engine and return JSON + markdown summary + context."""

    engine, engine_error = _resolve_engine(llm_settings)
    if engine is None:
        error_json = json.dumps({"error": True, "message": engine_error or "LLM not configured"}, indent=2)
        return error_json, engine_error or "", {}, ""

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
        result = engine.recognize_intent(
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
    llm_settings: Optional[Dict[str, Any]],
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

    provider_choice = _resolve_llm_provider_choice(llm_settings)

    try:
        with _temporary_llm_env(llm_settings):
            summary, personas_json, cluster_plot, stats_plot = discover_behavioral_patterns(
                csv_file=resolved_path,
                min_cluster_size=min_cluster_size,
                min_samples=min_samples,
                use_llm_personas=use_llm_personas,
                llm_provider=provider_choice,
            )
    except Exception as exc:  # noqa: BLE001
        return (f"❌ Pattern discovery failed:\n\n{exc}", [], None, None)

    try:
        personas_obj = json.loads(personas_json) if personas_json else []
    except json.JSONDecodeError:
        personas_obj = {"raw": personas_json or "[]"}

    return summary, personas_obj, (cluster_plot or None), (stats_plot or None)


def run_bid_optimizer_playbook(
    use_manual_intent: bool,
    manual_intent_label: str,
    manual_confidence: float,
    persona_name: str,
    persona_description: str,
    persona_size: float,
    persona_share_percent: float,
    persona_conversion_percent: float,
    persona_ltv_index: float,
    historical_cvr_percent: float,
    recent_roas: float,
    channel_choice: str,
    user_query: str,
    page_type: str,
    previous_actions: str,
    time_on_page: int,
    session_history: str,
    device_type: str,
    traffic_source: str,
    scroll_depth: float,
    clicks_count: int,
    llm_settings: Optional[Dict[str, Any]],
) -> Tuple[Any, Any, str]:
    """Run bid optimizer by either inferring intent via LLM or using manual override."""
    if BID_OPTIMIZER is None:
        msg = BID_OPTIMIZER_ERROR or "Bid optimizer not initialized."
        return {"error": msg}, {"error": msg}, f"❌ {msg}"

    intent_payload: Dict[str, Any]
    label: str
    confidence: float
    evidence: List[str]

    if use_manual_intent:
        label = manual_intent_label or "compare_options"
        confidence = max(0.0, min(1.0, manual_confidence or 0.55))
        evidence = ["Manual override"]
        intent_payload = {
            "primary_intent": label,
            "confidence": confidence,
            "source": "manual_override",
        }
    else:
        engine, engine_error = _resolve_engine(llm_settings)
        if engine is None:
            error_msg = engine_error or "Intent engine not configured."
            return {"error": error_msg}, {"error": error_msg}, f"❌ {error_msg}"
        try:
            intent_payload = engine.recognize_intent(
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
            return (
                {"error": str(exc)},
                {"error": str(exc)},
                f"❌ Intent analysis failed: {exc}",
            )
        label = intent_payload.get("primary_intent", manual_intent_label or "unknown")
        confidence = float(intent_payload.get("confidence", manual_confidence or 0.55))
        evidence = intent_payload.get("behavioral_evidence") or []

    intent_def = TAXONOMY.get_intent_definition(label) if TAXONOMY else {}
    stage = intent_def.get("stage") if intent_def else None

    intent_signal = IntentSignal(
        label=label,
        confidence=max(0.0, min(1.0, confidence)),
        stage=stage,
        evidence=evidence,
        metadata={"source": intent_payload.get("source", "engine")},
    )

    persona_profile = _build_persona_profile(
        persona_name,
        persona_description,
        persona_size,
        persona_share_percent,
        persona_conversion_percent,
        persona_ltv_index,
        intent_signal.label,
    )

    metrics: Dict[str, float] = {}
    hist_ratio = _percent_to_ratio(historical_cvr_percent)
    if hist_ratio is not None:
        metrics["historical_cvr"] = hist_ratio
    if recent_roas:
        metrics["recent_roas"] = recent_roas

    activation_context = ActivationContext(
        intents=[intent_signal],
        persona=persona_profile,
        metrics=metrics or None,
        metadata={
            "channel": channel_choice or "default",
            "context_preview": context_view,
        },
    )

    recommendation = BID_OPTIMIZER.recommend(activation_context)
    recommendation_dict = asdict(recommendation)

    summary_lines = [
        f"**Channel:** {channel_choice or 'default'}",
        f"**Intent Used:** {label.replace('_', ' ').title()} ({intent_signal.confidence:.0%})",
        f"**Bid Modifier:** {recommendation.bid_modifier:+.0%}",
        f"**Adjusted Bid:** ${recommendation.base_bid or 0:.2f}",
        f"**Pacing Guidance:** {recommendation.metadata.get('pacing', 'monitor')}",
        f"**Conversion Probability:** {recommendation.metadata.get('conversion_probability', 0.0):.0%}",
    ]

    return intent_payload, recommendation_dict, "\n".join(summary_lines)


def sync_audience_playbook(
    audience_channel: str,
    cohort_name: str,
    cohort_description: str,
    user_identifiers: str,
    dry_run: bool,
    use_manual_intent: bool,
    manual_intent_label: str,
    manual_confidence: float,
    persona_name: str,
    persona_description: str,
    persona_size: float,
    persona_share_percent: float,
    persona_conversion_percent: float,
    persona_ltv_index: float,
    historical_cvr_percent: float,
    recent_roas: float,
    user_query: str,
    page_type: str,
    previous_actions: str,
    time_on_page: int,
    session_history: str,
    device_type: str,
    traffic_source: str,
    scroll_depth: float,
    clicks_count: int,
    llm_settings: Optional[Dict[str, Any]],
) -> Tuple[Any, str]:
    """Sync provided cohort to selected channel using AudienceManager."""
    if AUDIENCE_MANAGER is None:
        msg = AUDIENCE_MANAGER_ERROR or "Audience manager not initialized."
        return {"error": msg}, f"❌ {msg}"

    identifiers = _parse_identifiers(user_identifiers)
    if not identifiers:
        return {"error": "No identifiers supplied."}, "❌ Provide email/customer IDs to sync."

    if use_manual_intent:
        label = manual_intent_label or "compare_options"
        confidence = max(0.0, min(1.0, manual_confidence or 0.55))
        evidence = ["Manual override"]
        intent_payload = {
            "primary_intent": label,
            "confidence": confidence,
            "source": "manual_override",
        }
    else:
        engine, engine_error = _resolve_engine(llm_settings)
        if engine is None:
            error_msg = engine_error or "Intent engine not configured."
            return {"error": error_msg}, f"❌ {error_msg}"
        try:
            intent_payload = engine.recognize_intent(
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
            return {"error": str(exc)}, f"❌ Intent analysis failed: {exc}"
        label = intent_payload.get("primary_intent", manual_intent_label or "unknown")
        confidence = float(intent_payload.get("confidence", manual_confidence or 0.55))
        evidence = intent_payload.get("behavioral_evidence") or []

    persona_profile = _build_persona_profile(
        persona_name,
        persona_description,
        persona_size,
        persona_share_percent,
        persona_conversion_percent,
        persona_ltv_index,
        label,
    )

    metrics: Dict[str, float] = {}
    hist_ratio = _percent_to_ratio(historical_cvr_percent)
    if hist_ratio is not None:
        metrics["historical_cvr"] = hist_ratio
    if recent_roas:
        metrics["recent_roas"] = recent_roas

    context = ActivationContext(
        intents=[
            IntentSignal(
                label=label,
                confidence=max(0.0, min(1.0, confidence)),
                stage=(TAXONOMY.get_intent_definition(label) or {}).get("stage") if TAXONOMY else None,
                evidence=evidence,
            )
        ],
        persona=persona_profile,
        metrics=metrics or None,
        metadata={"channel": audience_channel, "source": "bid_optimizer"},
    )

    cohort = AudienceCohort(
        name=cohort_name or f"{label}-cohort",
        description=cohort_description or f"Auto-synced from Bid Optimizer ({label})",
        user_ids=identifiers,
    )

    try:
        result = AUDIENCE_MANAGER.sync(audience_channel, cohort, context, dry_run=dry_run)
    except ActivationError as exc:
        return {"error": str(exc)}, f"❌ Audience sync failed: {exc}"

    summary_lines = [
        f"**Channel:** {audience_channel}",
        f"**Cohort:** {cohort.name} ({result.get('user_count', len(identifiers))} users)",
        f"**Status:** {result.get('status', 'unknown')}",
        f"**Dry Run:** {result.get('dry_run', dry_run)}",
    ]

    return result, "\n".join(summary_lines)

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

    if ENGINE is None:
        gr.Markdown(
            "ℹ️ **Bring your own API key:** Expand the LLM Settings panel below or set `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, or `OPENROUTER_API_KEY` in the Space secrets.",
            elem_id="no-server-keys",
        )

    llm_state = gr.State(
        {
            "enabled": False,
            "provider": "openrouter",
            "api_key": "",
            "model": "",
        }
    )

    with gr.Accordion("LLM Settings (stored in your browser session)", open=False):
        gr.Markdown(
            "Bring your own API key to avoid using the demo credits. These values live only in this browser tab and reset on refresh."
        )
        enable_custom = gr.Checkbox(label="Use custom credentials", value=False)
        provider_choice = gr.Dropdown(
            choices=LLM_PROVIDER_CHOICES,
            value="openrouter",
            label="Provider",
        )
        api_key_box = gr.Textbox(label="API Key", type="password", placeholder="sk-...")
        model_box = gr.Textbox(label="Preferred Model (optional)", placeholder="claude-3-sonnet-20240229")
        with gr.Row():
            save_llm_btn = gr.Button("Apply LLM Settings", variant="primary")
            clear_llm_btn = gr.Button("Clear", variant="secondary")
        default_status = (
            "Using server/.env credentials."
            if ENGINE is not None
            else "No server credentials detected. Enable custom mode and paste your API key below."
        )
        llm_status = gr.Markdown(default_status)

        save_llm_btn.click(
            fn=save_llm_settings,
            inputs=[enable_custom, provider_choice, api_key_box, model_box],
            outputs=[llm_state, llm_status],
        )
        clear_llm_btn.click(
            fn=clear_llm_settings,
            inputs=None,
            outputs=[llm_state, llm_status],
        )

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
                    llm_state,
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
                    llm_state,
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

        with gr.Tab("Bid Optimizer"):
            intent_choices = TAXONOMY.get_all_intent_labels() if TAXONOMY else []
            gr.Markdown(
                """
                ### Bid Optimizer Playground

                Run the Layer 4 optimizer to turn intents + personas into bid recommendations. Auto-detect intent with the engine or manually enter it for deterministic testing.
                """
            )
            channel_choice = gr.Dropdown(
                label="Channel",
                choices=["default", "google_ads", "meta_ads"],
                value="google_ads",
            )
            use_manual_intent = gr.Checkbox(
                label="Manual Intent Override",
                value=ENGINE is None,
                info="Enable if you want to skip the LLM and enter intent + confidence yourself.",
            )
            manual_intent_label = gr.Dropdown(
                label="Intent Label",
                choices=intent_choices,
                value=intent_choices[0] if intent_choices else "ready_to_purchase",
            )
            manual_confidence = gr.Slider(
                label="Intent Confidence (Manual Mode)",
                minimum=0.0,
                maximum=1.0,
                step=0.01,
                value=0.75,
            )

            gr.Markdown("#### Persona & Historical Signals")
            persona_name = gr.Textbox(label="Persona Name", placeholder="Research-Driven Comparers")
            persona_description = gr.Textbox(
                label="Persona Description",
                placeholder="Concise description used in creative + activation briefs.",
            )
            with gr.Row():
                persona_size = gr.Number(label="Persona Size (# users)", value=50)
                persona_share = gr.Slider(label="Persona Share (%)", minimum=0, maximum=100, step=1, value=15)
            with gr.Row():
                persona_conversion = gr.Slider(
                    label="Persona Conversion Rate (%)", minimum=0, maximum=100, step=1, value=48
                )
                persona_ltv = gr.Number(label="Persona LTV Index (1.0 = avg)", value=1.2)
            with gr.Row():
                historical_cvr = gr.Slider(
                    label="Historical Campaign CVR (%)", minimum=0, maximum=100, step=1, value=35
                )
                recent_roas = gr.Number(label="Recent ROAS", value=3.2)

            gr.Markdown("#### Context Inputs (mirrors Intent Analyzer)")
            bid_user_query = gr.Textbox(label="User Query", placeholder="nike pegasus discount code")
            bid_page_type = gr.Dropdown(
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
            bid_previous_actions = gr.Textbox(
                label="Previous Actions", placeholder="viewed_product,read_reviews,checked_shipping"
            )
            bid_time_on_page = gr.Slider(label="Time on Page (seconds)", minimum=0, maximum=600, step=5, value=180)
            bid_session_history = gr.Textbox(
                label="Session History JSON",
                placeholder='[{"intent": "compare_options", "timestamp": "2025-01-02T12:00:00"}]',
                lines=3,
            )
            with gr.Row():
                bid_device_type = gr.Dropdown(label="Device", choices=["desktop", "mobile", "tablet"], value="desktop")
                bid_traffic_source = gr.Dropdown(
                    label="Traffic Source",
                    choices=["direct", "search_google", "social_meta", "email", "affiliate"],
                    value="search_google",
                )
            with gr.Row():
                bid_scroll_depth = gr.Slider(label="Scroll Depth (%)", minimum=0, maximum=100, step=5, value=70)
                bid_clicks_count = gr.Slider(label="Clicks This Session", minimum=0, maximum=20, step=1, value=5)

            bid_button = gr.Button("Compute Bid Recommendation", variant="primary")
            bid_intent_json = gr.JSON(label="Intent Input Preview")
            bid_recommendation_json = gr.JSON(label="Bid Recommendation JSON")
            bid_summary = gr.Markdown("Run the optimizer to view guidance.")

            bid_button.click(
                fn=run_bid_optimizer_playbook,
                inputs=[
                    use_manual_intent,
                    manual_intent_label,
                    manual_confidence,
                    persona_name,
                    persona_description,
                    persona_size,
                    persona_share,
                    persona_conversion,
                    persona_ltv,
                    historical_cvr,
                    recent_roas,
                    channel_choice,
                    bid_user_query,
                    bid_page_type,
                    bid_previous_actions,
                    bid_time_on_page,
                    bid_session_history,
                    bid_device_type,
                    bid_traffic_source,
                    bid_scroll_depth,
                    bid_clicks_count,
                    llm_state,
                ],
                outputs=[bid_intent_json, bid_recommendation_json, bid_summary],
            )

            gr.Markdown("#### Audience Activation")
            with gr.Row():
                audience_channel = gr.Dropdown(
                    label="Sync Channel",
                    choices=["google_ads", "meta_ads"],
                    value="google_ads",
                )
                audience_dry_run = gr.Checkbox(
                    label="Dry Run (hash only, no upload)",
                    value=True,
                )
            cohort_name = gr.Textbox(label="Cohort Name", placeholder="High Intent Persona")
            cohort_description = gr.Textbox(
                label="Cohort Description",
                placeholder="Custom audience synced from Bid Optimizer",
            )
            cohort_identifiers = gr.Textbox(
                label="User Identifiers (emails or IDs)",
                placeholder="user@example.com, second@example.com",
                lines=3,
            )

            sync_button = gr.Button("Sync Audience", variant="secondary")
            sync_json = gr.JSON(label="Audience Sync Result")
            sync_summary = gr.Markdown("Provide identifiers and click sync to upload.")

            sync_button.click(
                fn=sync_audience_playbook,
                inputs=[
                    audience_channel,
                    cohort_name,
                    cohort_description,
                    cohort_identifiers,
                    audience_dry_run,
                    use_manual_intent,
                    manual_intent_label,
                    manual_confidence,
                    persona_name,
                    persona_description,
                    persona_size,
                    persona_share,
                    persona_conversion,
                    persona_ltv,
                    historical_cvr,
                    recent_roas,
                    channel_choice,
                    bid_user_query,
                    bid_page_type,
                    bid_previous_actions,
                    bid_time_on_page,
                    bid_session_history,
                    bid_device_type,
                    bid_traffic_source,
                    bid_scroll_depth,
                    bid_clicks_count,
                    llm_state,
                ],
                outputs=[sync_json, sync_summary],
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
                with gr.Column():
                    gr.Markdown("#### Bid Optimizer MCP (port 7862)")
                    gr.Markdown(
                        "- Script: `python tools/bid_optimizer_mcp.py`\n"
                        "- Tool name: `optimize_bid`\n"
                        "- Endpoint: `http://localhost:7862/gradio_api/mcp/sse`"
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
    },
    "bid-optimizer": {
      "url": "http://localhost:7862/gradio_api/mcp/sse"
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
    },
    "bid-optimizer": {
      "command": "python",
      "args": ["tools/bid_optimizer_mcp.py"],
      "port": 7862
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
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", os.environ.get("GRADIO_SERVER_PORT", 7860))),
    )
