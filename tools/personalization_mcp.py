"""
Personalization & Creative MCP Tool - Layer 4 Activation Playground.

Expose the personalization/creative playbook as a standalone MCP-compatible tool.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict
from typing import Any, Dict, List

import gradio as gr

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.activation import (
    ActivationContext,
    IntentSignal,
    Layer4ActivationPlaybook,
    PersonaProfile,
)
from src.intent import IntentTaxonomy
from src.utils.context_builder import ContextBuilder

TAXONOMY = IntentTaxonomy.from_domain("ecommerce")
CONTEXT_BUILDER = ContextBuilder()
PLAYBOOK = Layer4ActivationPlaybook(include_bidding=False)
CHANNEL_CHOICES = ["web", "app", "email"]
SLOT_CHOICES = sorted(("hero_banner", "proof_bar"))


def _build_persona_profile(
    name: str,
    description: str,
    size: float,
    share_percent: float,
    conversion_rate_percent: float,
    ltv_index: float,
    intent_label: str,
) -> PersonaProfile:
    metrics = {
        "conversion_rate": max(0.0, min(1.0, conversion_rate_percent / 100.0)),
        "ltv_index": ltv_index or 1.0,
    }
    return PersonaProfile(
        name=name or "Activation Persona",
        description=description or f"Persona derived from {intent_label}",
        size=int(size or 0),
        share=max(0.0, min(1.0, share_percent / 100.0)),
        intent_distribution={intent_label: 1.0},
        metrics=metrics,
    )


def run_personalization_playbook(
    channel: str,
    preferred_channels: List[str],
    available_slots: List[str],
    use_llm_brief: bool,
    intent_label: str,
    intent_confidence: float,
    persona_name: str,
    persona_description: str,
    persona_size: float,
    persona_share_percent: float,
    persona_conversion_percent: float,
    persona_ltv_index: float,
    has_budget_constraint: bool,
    has_time_constraint: bool,
    has_knowledge_gap: bool,
    user_query: str,
    page_type: str,
    previous_actions: str,
    time_on_page: int,
    session_history: str,
) -> Dict[str, Any]:
    """Return personalization + creative guidance for provided context."""
    context_preview = CONTEXT_BUILDER.build_context(
        user_query=user_query,
        page_type=page_type,
        previous_actions=previous_actions,
        time_on_page=time_on_page,
        session_history=session_history,
    )

    intent_def = TAXONOMY.get_intent_definition(intent_label) or {}
    intent_signal = IntentSignal(
        label=intent_label,
        confidence=max(0.0, min(1.0, intent_confidence)),
        stage=intent_def.get("stage"),
        evidence=["MCP tool input"],
    )
    persona = _build_persona_profile(
        persona_name,
        persona_description,
        persona_size,
        persona_share_percent,
        persona_conversion_percent,
        persona_ltv_index,
        intent_label,
    )
    metadata = {
        "channel": channel or "web",
        "preferred_channels": preferred_channels or [channel],
        "context_preview": context_preview,
        "personalization_context": {
            "available_slots": available_slots,
            "constraints": {
                "has_budget_constraint": has_budget_constraint,
                "has_time_constraint": has_time_constraint,
                "has_knowledge_gap": has_knowledge_gap,
            },
        },
        "creative_options": {"mode": "llm" if use_llm_brief else "template"},
    }
    activation_context = ActivationContext(
        intents=[intent_signal],
        persona=persona,
        metrics=None,
        metadata=metadata,
    )

    playbook = Layer4ActivationPlaybook(include_bidding=False, use_llm_brief=use_llm_brief)
    result = playbook.run(activation_context)
    slots = [action for action in result.actions if action.get("type") in ("content_slot", "offer")]
    recs = [action for action in result.actions if action.get("type") == "recommendation"]
    email = next((action for action in result.actions if action.get("type") == "email_playbook"), {})
    creative = next((action for action in result.actions if action.get("type") == "creative_brief"), {})

    return {
        "intent": asdict(intent_signal),
        "persona": asdict(persona),
        "context_preview": context_preview,
        "content_slots": slots,
        "recommendations": recs,
        "email_playbook": email,
        "creative_brief": creative,
        "diagnostics": result.diagnostics,
    }


demo = gr.Interface(
    fn=run_personalization_playbook,
    inputs=[
        gr.Dropdown(label="Primary Channel", choices=CHANNEL_CHOICES, value="web"),
        gr.CheckboxGroup(label="Preferred Channels", choices=CHANNEL_CHOICES, value=["web", "email"]),
        gr.CheckboxGroup(label="Available Slots", choices=SLOT_CHOICES, value=SLOT_CHOICES),
        gr.Checkbox(label="Use LLM for Creative Brief", value=True),
        gr.Dropdown(label="Intent Label", choices=TAXONOMY.get_all_intent_labels(), value="ready_to_purchase"),
        gr.Slider(label="Intent Confidence", minimum=0.0, maximum=1.0, value=0.85, step=0.01),
        gr.Textbox(label="Persona Name", value="High-Intent Researchers"),
        gr.Textbox(label="Persona Description", value="Needs proof before buying."),
        gr.Number(label="Persona Size (# users)", value=120),
        gr.Slider(label="Persona Share (%)", minimum=0, maximum=100, value=25, step=1),
        gr.Slider(label="Persona Conversion Rate (%)", minimum=0, maximum=100, value=52, step=1),
        gr.Number(label="Persona LTV Index", value=1.2),
        gr.Checkbox(label="Budget Constraint", value=False),
        gr.Checkbox(label="Time Constraint", value=False),
        gr.Checkbox(label="Knowledge Gap", value=False),
        gr.Textbox(label="User Query", value="nike pegasus discount code"),
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
        gr.Textbox(label="Previous Actions", value="viewed_product,read_reviews,checked_shipping"),
        gr.Slider(label="Time on Page (seconds)", minimum=0, maximum=600, value=200, step=5),
        gr.Textbox(
            label="Session History JSON",
            value='[{"intent": "compare_options", "timestamp": "2025-01-02T12:00:00"}]',
        ),
    ],
    outputs=gr.JSON(label="Personalization Output"),
    title="Layer 4 Personalization MCP Tool",
    description="Generate content slots, recommendations, email playbooks, and creative briefs based on intent + persona context.",
)


if __name__ == "__main__":
    demo.launch()
