"""Triggered email planner."""

from __future__ import annotations

from typing import Any, Dict, List

from ..base import ActivationComponent, ActivationContext, ActivationError, ActivationResult
from .config_loader import load_personalization_config


class TriggeredEmailPlanner(ActivationComponent):
    """Creates triggered email playbooks aligned with detected intent."""

    component_name = "triggered_email_planner"

    def __init__(
        self,
        *,
        config_path: str = "config/activation/personalization.yaml",
        enabled: bool = True,
    ) -> None:
        super().__init__(enabled=enabled)
        self.config_path = config_path
        self._config = load_personalization_config(config_path)
        self._playbooks = self._config.get("email_playbooks", {})

    def execute(self, context: ActivationContext) -> ActivationResult:
        if not context.intents:
            raise ActivationError("Email planner requires at least one intent.")

        primary_intent = context.intents[0].label
        playbook = self._playbooks.get(primary_intent) or self._playbooks.get("default")
        if not playbook:
            return ActivationResult(
                diagnostics=[f"No email playbook configured for intent '{primary_intent}'."]
            )

        steps = self._format_steps(playbook.get("steps", []))
        action = {
            "type": "email_playbook",
            "intent": primary_intent,
            "subject": playbook.get("subject"),
            "delay_minutes": playbook.get("delay_minutes", 60),
            "steps": steps,
        }

        diagnostics = [f"Email playbook prepared for {primary_intent} ({len(steps)} steps)."]
        metadata: Dict[str, Any] = {"intent": primary_intent, "steps_count": len(steps)}
        return ActivationResult(actions=[action], diagnostics=diagnostics, metadata=metadata)

    @staticmethod
    def _format_steps(raw_steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        formatted: List[Dict[str, Any]] = []
        for step in raw_steps:
            formatted.append(
                {
                    "type": step.get("type"),
                    "message": step.get("message"),
                }
            )
        return formatted
