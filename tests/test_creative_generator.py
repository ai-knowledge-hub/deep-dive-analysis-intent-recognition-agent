from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json
from pathlib import Path
from typing import Optional

import yaml

from src.activation import ActivationContext, IntentSignal, PersonaProfile
from src.activation.creative import CreativeBriefGenerator
from src.intent.llm_provider import BaseLLMProvider


def build_context(intent_label: str = "compare_options") -> ActivationContext:
    intent = IntentSignal(label=intent_label, confidence=0.7, stage="consideration", evidence=["test"])
    persona = PersonaProfile(
        name="Persona",
        description="Description",
        size=50,
        share=0.1,
        intent_distribution={intent_label: 0.8},
        metrics={"ltv_index": 1.0},
    )
    metadata = {"context_preview": {"behavioral_signals": {"actions_taken": ["viewed_product"]}}}
    return ActivationContext(intents=[intent], persona=persona, metadata=metadata)


def _expected_template_sections() -> dict:
    config_path = Path("config/activation/creative.yaml")
    with config_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    sections = data.get("brief_template", {}).get("sections", {})
    return {name: cfg.get("prompt") for name, cfg in sections.items()}


def test_creative_brief_generator_template_mode_snapshot():
    generator = CreativeBriefGenerator(use_llm=False)
    result = generator.run(build_context())

    assert result.actions, "Creative brief should be returned even without LLM."
    brief = result.actions[0]
    assert brief["type"] == "creative_brief"
    sections = brief["sections"]
    expected_sections = _expected_template_sections()
    assert sections == expected_sections


class DummyLLMProvider(BaseLLMProvider):
    """Mock provider returning deterministic JSON."""

    def __init__(self) -> None:
        self.called_with_prompt: Optional[str] = None

    async def generate(self, prompt: str, system_prompt: str = "", **kwargs) -> str:
        return self.generate_sync(prompt, system_prompt=system_prompt)

    def generate_sync(
        self,
        prompt: str,
        *,
        system_prompt: Optional[str] = None,
        max_output_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        self.called_with_prompt = prompt
        payload = {
            "objective": "Drive confidence for product X.",
            "audience_insight": "Intent: compare options; persona: Persona.",
            "key_message": "Crystal clarity between top choices.",
            "proof_points": "1. Award-winning support. 2. 2-day delivery.",
            "tone_guidance": "Authoritative yet empathetic.",
            "call_to_action": "See side-by-side comparison",
        }
        return json.dumps(payload)


def test_creative_brief_generator_llm_mode_uses_provider():
    dummy = DummyLLMProvider()
    generator = CreativeBriefGenerator(llm_provider=dummy, use_llm=True)
    result = generator.run(build_context())

    assert dummy.called_with_prompt is not None, "LLM provider should be invoked when enabled."
    brief = result.actions[0]
    sections = brief["sections"]
    assert sections["objective"] == "Drive confidence for product X."
    assert sections["call_to_action"] == "See side-by-side comparison"
