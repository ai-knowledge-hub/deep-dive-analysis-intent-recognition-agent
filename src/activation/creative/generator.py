"""Creative brief generation helper."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from ..base import ActivationComponent, ActivationContext, ActivationError, ActivationResult
from ...intent.llm_provider import BaseLLMProvider, LLMProviderFactory


class CreativeBriefGenerator(ActivationComponent):
    """Turns intents/personas into creative briefs, optionally using an LLM."""

    component_name = "creative_brief_generator"

    def __init__(
        self,
        *,
        config_path: str = "config/activation/creative.yaml",
        llm_provider: Optional[BaseLLMProvider] = None,
        use_llm: bool = True,
        enabled: bool = True,
    ) -> None:
        super().__init__(enabled=enabled)
        self.config_path = config_path
        self._config = self._load_config(config_path)
        self._sections = self._config.get("brief_template", {}).get("sections", {})
        self._llm_config = self._config.get("llm", {})
        self._asset_preferences = self._config.get("asset_preferences", {})
        self._llm_provider = llm_provider
        self._use_llm = use_llm

    def execute(self, context: ActivationContext) -> ActivationResult:
        if not context.intents:
            raise ActivationError("Creative brief generator requires an intent signal.")

        primary_intent = context.intents[0]
        sections = self._sections or {}
        asset_pref = self._asset_preferences.get(primary_intent.label, {})

        if not sections:
            return ActivationResult(
                diagnostics=["No creative template configured; skipping."],
                metadata={"intent": primary_intent.label},
            )

        brief_sections = (
            self._generate_with_llm(context, sections)
            if self._should_use_llm()
            else self._generate_from_template(sections)
        )

        action = {
            "type": "creative_brief",
            "intent": primary_intent.label,
            "sections": brief_sections,
            "asset_preferences": asset_pref,
        }
        diagnostics = [
            f"Creative brief ready for intent '{primary_intent.label}' using "
            f"{'LLM' if self._should_use_llm() else 'template'} mode."
        ]
        metadata = {"intent": primary_intent.label, "mode": "llm" if self._should_use_llm() else "template"}
        return ActivationResult(actions=[action], diagnostics=diagnostics, metadata=metadata)

    # Internal ----------------------------------------------------------------
    def _should_use_llm(self) -> bool:
        return bool(self._llm_config.get("enabled") and self._use_llm and self._provider_available())

    def _provider_available(self) -> bool:
        if self._llm_provider is not None:
            return True
        try:
            self._llm_provider = LLMProviderFactory.create_from_env()
        except Exception:  # noqa: BLE001 - fallback to template mode
            self._llm_provider = None
        return self._llm_provider is not None

    def _generate_with_llm(self, context: ActivationContext, sections: Dict[str, Any]) -> Dict[str, str]:
        if self._llm_provider is None:
            return self._generate_from_template(sections)

        payload = self._context_payload(context)
        prompt = self._build_prompt(payload, sections)
        try:
            raw = self._llm_provider.generate_sync(
                prompt=prompt,
                system_prompt="You are a senior creative director creating concise marketing briefs.",
                max_output_tokens=self._llm_config.get("max_tokens", 400),
                temperature=self._llm_config.get("temperature", 0.3),
            )
            return self._parse_llm_response(raw, sections)
        except Exception:  # noqa: BLE001 - degrade gracefully
            return self._generate_from_template(sections)

    @staticmethod
    def _generate_from_template(sections: Dict[str, Any]) -> Dict[str, str]:
        return {name: cfg.get("prompt") for name, cfg in sections.items()}

    @staticmethod
    def _parse_llm_response(raw: str, sections: Dict[str, Any]) -> Dict[str, str]:
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                return {k: str(v) for k, v in data.items()}
        except json.JSONDecodeError:
            pass
        # fallback: return single block of text mapped onto sections
        return {name: raw for name in sections}

    def _context_payload(self, context: ActivationContext) -> Dict[str, Any]:
        persona = {
            "name": context.persona.name if context.persona else None,
            "description": context.persona.description if context.persona else None,
            "metrics": context.persona.metrics if context.persona else None,
        }
        metadata = context.metadata or {}
        return {
            "intent": {
                "label": context.intents[0].label,
                "confidence": context.intents[0].confidence,
                "evidence": context.intents[0].evidence,
            },
            "persona": persona,
            "metrics": context.metrics,
            "metadata": metadata,
        }

    @staticmethod
    def _build_prompt(payload: Dict[str, Any], sections: Dict[str, Any]) -> str:
        prompt_lines = [
            "Given the marketing context below, craft a JSON object where each key matches the requested section name.",
            "Context:",
            json.dumps(payload, indent=2),
            "Sections and guidance:",
        ]
        for name, cfg in sections.items():
            prompt_lines.append(f"- {name}: {cfg.get('prompt')}")
        prompt_lines.append("Respond ONLY with JSON (section -> text).")
        return "\n".join(prompt_lines)

    @staticmethod
    def _load_config(path_str: str) -> Dict[str, Any]:
        path = Path(path_str)
        if not path.exists():
            raise ActivationError(f"Creative configuration not found at {path_str}")
        with path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}
