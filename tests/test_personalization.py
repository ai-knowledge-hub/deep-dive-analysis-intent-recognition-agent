from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.activation import ActivationContext, IntentSignal, PersonaProfile
from src.activation.personalization import (
    ContentPersonalizationEngine,
    RecommendationSelector,
    TriggeredEmailPlanner,
)


def _mock_context(intent_label: str = "ready_to_purchase") -> ActivationContext:
    intent = IntentSignal(label=intent_label, confidence=0.8, stage="decision")
    persona = PersonaProfile(
        name="Test Persona",
        description="Sample persona for tests",
        size=100,
        share=0.2,
        intent_distribution={intent_label: 0.9},
        metrics={"ltv_index": 1.2},
    )
    metadata = {
        "channel": "web",
        "personalization_context": {"constraints": {"budget": True}},
    }
    return ActivationContext(intents=[intent], persona=persona, metadata=metadata)


def test_content_personalization_returns_slots_and_offer():
    engine = ContentPersonalizationEngine()
    result = engine.run(_mock_context())

    slot_actions = [a for a in result.actions if a.get("type") == "content_slot"]
    assert slot_actions, "Expected at least one content slot recommendation."
    offer_actions = [a for a in result.actions if a.get("type") == "offer"]
    assert offer_actions, "Offer should be suggested for high LTV persona."


def test_content_personalization_respects_available_slots():
    engine = ContentPersonalizationEngine()
    context = _mock_context("compare_options")
    context.metadata.setdefault("personalization_context", {})["available_slots"] = ["proof_bar"]
    result = engine.run(context)
    slot_actions = [a for a in result.actions if a.get("type") == "content_slot"]
    assert slot_actions
    assert all(action.get("slot") == "proof_bar" for action in slot_actions)


def test_recommendation_selector_uses_intent_rules():
    selector = RecommendationSelector()
    result = selector.run(_mock_context("compare_options"))

    assert result.actions, "Recommendations should be produced."
    assert result.actions[0]["category"] in {"comparison", "content_hub"}


def test_triggered_email_planner_uses_playbook_defaults():
    planner = TriggeredEmailPlanner()
    result = planner.run(_mock_context("deal_seeking"))

    assert result.actions, "Email playbook action should be present."
    payload = result.actions[0]
    assert payload["type"] == "email_playbook"
    assert payload["steps"], "Playbook must include steps."
