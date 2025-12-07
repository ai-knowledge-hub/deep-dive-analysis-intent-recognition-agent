"""Recommendation selector for Layer 4."""

from __future__ import annotations

from typing import Any, Dict, List

from ..base import ActivationComponent, ActivationContext, ActivationError, ActivationResult
from .config_loader import load_personalization_config


class RecommendationSelector(ActivationComponent):
    """Returns next-best recommendations (products/guides/promotions)."""

    component_name = "recommendation_selector"

    def __init__(
        self,
        *,
        config_path: str = "config/activation/personalization.yaml",
        enabled: bool = True,
    ) -> None:
        super().__init__(enabled=enabled)
        self.config_path = config_path
        self._config = load_personalization_config(config_path)
        self._rules = self._config.get("recommendations", {})

    def execute(self, context: ActivationContext) -> ActivationResult:
        if not context.intents:
            raise ActivationError("Recommendation selector requires an intent signal.")

        primary_intent = context.intents[0].label
        intents_cfg = (self._rules.get("intents") or {}).get(primary_intent, [])
        default_cfg = self._rules.get("default", [])

        actions: List[Dict[str, Any]] = []
        diagnostics: List[str] = []

        for candidate in intents_cfg or default_cfg:
            action = {
                "type": "recommendation",
                "category": candidate.get("type"),
                "id": candidate.get("id"),
                "label": candidate.get("label"),
                "description": candidate.get("description"),
            }
            actions.append(action)
            diagnostics.append(f"Recommendation '{candidate.get('id')}' proposed for {primary_intent}.")

        metadata: Dict[str, Any] = {"source": "recommendation_rules", "intent": primary_intent}
        return ActivationResult(actions=actions, diagnostics=diagnostics, metadata=metadata)
