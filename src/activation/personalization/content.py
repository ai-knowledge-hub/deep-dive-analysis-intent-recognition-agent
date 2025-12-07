"""Content personalization engine."""

from __future__ import annotations

import copy
from typing import Any, Dict, List

from ..base import ActivationComponent, ActivationContext, ActivationError, ActivationResult
from .config_loader import load_personalization_config


class ContentPersonalizationEngine(ActivationComponent):
    """Assigns content slots/variants using YAML rules + context metadata."""

    component_name = "content_personalization"

    def __init__(
        self,
        *,
        config_path: str = "config/activation/personalization.yaml",
        enabled: bool = True,
    ) -> None:
        super().__init__(enabled=enabled)
        self.config_path = config_path
        self._config = load_personalization_config(config_path)
        self._slots = self._config.get("slots", {})
        self._offers = self._config.get("offers", {})
        self._channel_rules = self._config.get("channel_rules", {})

    def execute(self, context: ActivationContext) -> ActivationResult:
        if not context.intents:
            raise ActivationError("Content personalization requires at least one intent signal.")

        primary_intent = context.intents[0]
        preferred_channels = self._preferred_channels(context)
        constraints = self._gather_constraints(context)
        personalization_meta = (context.metadata or {}).get("personalization_context") or {}
        available_slots = personalization_meta.get("available_slots")
        if isinstance(available_slots, list) and available_slots:
            available_set = {slot for slot in available_slots if isinstance(slot, str)}
        else:
            available_set = None

        actions: List[Dict[str, Any]] = []
        diagnostics: List[str] = []

        for channel in preferred_channels:
            slot_ids = self._slot_order_for_channel(channel)
            if available_set:
                slot_ids = [slot_id for slot_id in slot_ids if slot_id in available_set]
            for slot_id in slot_ids:
                slot_cfg = self._slots.get(slot_id)
                if not slot_cfg:
                    continue
                allowed = slot_cfg.get("allowed_intents")
                if allowed and primary_intent.label not in allowed:
                    continue
                content = self._build_slot_content(slot_cfg, constraints)
                if not content:
                    continue
                actions.append(
                    {
                        "type": "content_slot",
                        "slot": slot_id,
                        "channel": channel,
                        "content": content,
                    }
                )
                diagnostics.append(
                    f"Slot '{slot_id}' prepared for channel '{channel}' (intent={primary_intent.label})."
                )

        offer = self._select_offer(context, primary_intent)
        metadata: Dict[str, Any] = {}
        if offer:
            actions.append({"type": "offer", **offer})
            diagnostics.append(f"Offer '{offer.get('name')}' selected for {primary_intent.label}.")
            metadata["selected_offer"] = offer

        return ActivationResult(actions=actions, diagnostics=diagnostics, metadata=metadata)

    # Helpers -----------------------------------------------------------------
    def _preferred_channels(self, context: ActivationContext) -> List[str]:
        metadata = context.metadata or {}
        preferred = metadata.get("preferred_channels")
        if isinstance(preferred, list) and preferred:
            return [str(ch).lower() for ch in preferred]
        channel = metadata.get("channel")
        if isinstance(channel, str) and channel:
            return [channel.lower()]
        return ["web"]

    def _slot_order_for_channel(self, channel: str) -> List[str]:
        rules = self._channel_rules.get(channel, {})
        priority = rules.get("priority_slots")
        if priority:
            return [slot for slot in priority if slot in self._slots]
        return list(self._slots.keys())

    def _gather_constraints(self, context: ActivationContext) -> Dict[str, Any]:
        constraints: Dict[str, Any] = {}
        metadata = context.metadata or {}
        from_meta = metadata.get("personalization_context", {})
        if isinstance(from_meta, dict):
            meta_constraints = from_meta.get("constraints")
            if isinstance(meta_constraints, dict):
                constraints.update(meta_constraints)

        preview = metadata.get("context_preview")
        if isinstance(preview, dict):
            constraint_signals = preview.get("constraint_signals")
            if isinstance(constraint_signals, dict):
                constraints.update(constraint_signals)
        return constraints

    def _build_slot_content(self, slot_cfg: Dict[str, Any], constraints: Dict[str, Any]) -> Dict[str, Any]:
        base_content = copy.deepcopy(slot_cfg.get("default_content") or {})
        overrides = slot_cfg.get("constraint_overrides") or {}
        for constraint_key, override in overrides.items():
            is_active = constraints.get(constraint_key)
            if is_active:
                base_content.update(override)
        return base_content

    def _select_offer(self, context: ActivationContext, intent) -> Dict[str, Any]:
        persona_metrics = (context.persona.metrics if context.persona and context.persona.metrics else {}) or {}
        for name, cfg in self._offers.items():
            intents = cfg.get("intents")
            if intents and intent.label not in intents:
                continue
            conditions = cfg.get("persona_conditions") or {}
            if not self._conditions_met(conditions, persona_metrics):
                continue
            recommendation = {
                "name": name,
                "description": cfg.get("recommendation", {}).get("description"),
                "mode": cfg.get("recommendation", {}).get("type"),
            }
            return {k: v for k, v in recommendation.items() if v}
        return {}

    @staticmethod
    def _conditions_met(conditions: Dict[str, Any], metrics: Dict[str, Any]) -> bool:
        if not conditions:
            return True
        min_ltv = conditions.get("min_ltv_index")
        if min_ltv is not None and metrics.get("ltv_index", 0) < min_ltv:
            return False
        return True
