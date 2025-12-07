"""
Bid Optimizer MCP Tool - Layer 4 Activation Playground

Expose the bid optimization engine as a standalone MCP-compatible tool.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict
from typing import Dict

import gradio as gr

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.activation import ActivationContext, IntentAwareBidOptimizer, IntentSignal, PersonaProfile
from src.intent import IntentTaxonomy
from src.utils.context_builder import ContextBuilder

CONTEXT_BUILDER = ContextBuilder()
TAXONOMY = IntentTaxonomy.from_domain("ecommerce")
INTENT_CHOICES = TAXONOMY.get_all_intent_labels()
OPTIMIZER = IntentAwareBidOptimizer(taxonomy=TAXONOMY)


def _percent_to_ratio(value: float) -> float:
    return max(0.0, min(1.0, value / 100.0))


def optimize_bid(
    channel: str,
    intent_label: str,
    intent_confidence: float,
    persona_name: str,
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
) -> Dict[str, object]:
    """Return bid guidance for provided context + persona signals."""
    context_preview = CONTEXT_BUILDER.build_context(
        user_query=user_query,
        page_type=page_type,
        previous_actions=previous_actions,
        time_on_page=time_on_page,
        session_history=session_history,
    )

    stage = (TAXONOMY.get_intent_definition(intent_label) or {}).get("stage")
    intent_signal = IntentSignal(
        label=intent_label,
        confidence=max(0.0, min(1.0, intent_confidence)),
        stage=stage,
        evidence=["MCP tool input"],
        metadata={"source": "mcp_tool"},
    )

    persona_profile = PersonaProfile(
        name=persona_name or "Activation Persona",
        description="Provided via bid optimizer MCP tool",
        size=int(persona_size or 0),
        share=_percent_to_ratio(persona_share_percent),
        intent_distribution={intent_label: 1.0},
        metrics={
            "conversion_rate": _percent_to_ratio(persona_conversion_percent),
            "ltv_index": persona_ltv_index or 1.0,
        },
    )

    metrics = {
        "historical_cvr": _percent_to_ratio(historical_cvr_percent),
        "recent_roas": recent_roas,
    }

    activation_context = ActivationContext(
        intents=[intent_signal],
        persona=persona_profile,
        metrics=metrics,
        metadata={"channel": channel, "context_preview": context_preview},
    )

    recommendation = OPTIMIZER.recommend(activation_context)
    payload = {
        "intent": asdict(intent_signal),
        "persona": asdict(persona_profile),
        "context_preview": context_preview,
        "recommendation": asdict(recommendation),
    }
    return payload


demo = gr.Interface(
    fn=optimize_bid,
    inputs=[
        gr.Dropdown(
            label="Channel",
            choices=["default", "google_ads", "meta_ads"],
            value="google_ads",
        ),
        gr.Dropdown(
            label="Intent Label",
            choices=INTENT_CHOICES,
            value=INTENT_CHOICES[0] if INTENT_CHOICES else "ready_to_purchase",
        ),
        gr.Slider(label="Intent Confidence", minimum=0.0, maximum=1.0, value=0.8, step=0.01),
        gr.Textbox(label="Persona Name", value="High-Intent Deal Seekers"),
        gr.Number(label="Persona Size (# users)", value=120),
        gr.Slider(label="Persona Share (%)", minimum=0, maximum=100, value=20, step=1),
        gr.Slider(label="Persona Conversion Rate (%)", minimum=0, maximum=100, value=55, step=1),
        gr.Number(label="Persona LTV Index", value=1.1),
        gr.Slider(label="Historical CVR (%)", minimum=0, maximum=100, value=38, step=1),
        gr.Number(label="Recent ROAS", value=3.5),
        gr.Textbox(label="User Query / Prompt", value="discount code for pegasus 40"),
        gr.Dropdown(
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
        ),
        gr.Textbox(
            label="Previous Actions",
            value="viewed_product,read_reviews,checked_shipping",
        ),
        gr.Slider(label="Time on Page (seconds)", minimum=0, maximum=600, value=180, step=5),
        gr.Textbox(
            label="Session History JSON",
            value='[{"intent": "compare_options", "timestamp": "2025-01-02T12:00:00"}]',
        ),
    ],
    outputs=gr.JSON(label="Bid Recommendation"),
    title="Layer 4 Bid Optimizer MCP Tool",
    description="Generate bid modifiers + pacing guidance using Layer 4 activation logic.",
)


if __name__ == "__main__":
    demo.launch()
