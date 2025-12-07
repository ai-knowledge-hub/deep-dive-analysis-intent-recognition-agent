"""
Conversion model used by the bid optimizer.

Combines taxonomy priors, persona metrics, historical performance, and intent
confidence to predict conversion probability and lift for a given context.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import yaml

from ..base import ActivationContext, IntentSignal
from ...intent.taxonomy import IntentTaxonomy


@dataclass
class ConversionEstimate:
    """Container for predicted conversion metrics."""

    probability: float
    lift_vs_baseline: float
    contributions: Dict[str, float]


DEFAULT_LIMITS = {
    "base_conversion_rate": 0.02,
    "min_conversion_rate": 0.005,
    "max_conversion_rate": 0.90,
    "neutral_confidence": 0.55,
}

DEFAULT_WEIGHTS = {
    "confidence_weight": 0.6,
    "persona_weight": 0.25,
    "historical_weight": 0.25,
}


class ConversionModel:
    """
    Lightweight conversion estimator used for bid decisions.
    """

    def __init__(
        self,
        taxonomy: IntentTaxonomy,
        *,
        config: Optional[Dict[str, float]] = None,
        defaults: Optional[Dict[str, float]] = None,
    ) -> None:
        self.taxonomy = taxonomy
        self.intent_conversion_map = {
            label: definition.get("conversion_likelihood", 0.0)
            for label, definition in taxonomy.intents.items()
        }
        self.defaults = {**DEFAULT_LIMITS, **(defaults or {})}
        self.weights = {**DEFAULT_WEIGHTS}
        config = config or {}
        self.weights.update({k: v for k, v in config.items() if k in DEFAULT_WEIGHTS})
        self.stage_multipliers = config.get("stage_multipliers", {})

    @classmethod
    def from_config(
        cls,
        taxonomy: IntentTaxonomy,
        config_path: str,
    ) -> "ConversionModel":
        """Create model from YAML config (shared with bid optimizer)."""
        config: Dict[str, Dict[str, float]] = {}
        path = Path(config_path)
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
        conversion_cfg = config.get("conversion_model", {})
        defaults = config.get("defaults", {})
        merged_defaults = {**DEFAULT_LIMITS, **defaults}
        return cls(taxonomy, config=conversion_cfg, defaults=merged_defaults)

    def predict(self, context: ActivationContext) -> ConversionEstimate:
        """Predict conversion probability for the provided context."""
        base_prob = self._base_conversion(context.intents[0] if context.intents else None)
        prob = base_prob
        contributions: Dict[str, float] = {"base": base_prob}

        if context.intents:
            intent = context.intents[0]
            confidence_adj = self._confidence_adjustment(intent)
            prob *= confidence_adj
            contributions["confidence"] = confidence_adj

        persona_adj = self._persona_adjustment(context)
        prob *= persona_adj
        contributions["persona"] = persona_adj

        history_adj = self._historical_adjustment(context)
        prob *= history_adj
        contributions["historical"] = history_adj

        prob = max(self.defaults["min_conversion_rate"], min(prob, self.defaults["max_conversion_rate"]))
        lift = ((prob - base_prob) / base_prob) if base_prob > 0 else 0.0
        return ConversionEstimate(probability=prob, lift_vs_baseline=lift, contributions=contributions)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _base_conversion(self, intent: Optional[IntentSignal]) -> float:
        base = self.defaults["base_conversion_rate"]
        if intent:
            base = self.intent_conversion_map.get(intent.label, base)
            stage = self._intent_stage(intent.label)
            if stage and stage in self.stage_multipliers:
                base *= self.stage_multipliers[stage]
        return base

    def _confidence_adjustment(self, intent: IntentSignal) -> float:
        neutral = self.defaults["neutral_confidence"]
        delta = intent.confidence - neutral
        return 1.0 + self.weights["confidence_weight"] * delta

    def _persona_adjustment(self, context: ActivationContext) -> float:
        persona = context.persona
        if not persona or not persona.metrics:
            return 1.0
        persona_cvr = persona.metrics.get("conversion_rate")
        if persona_cvr is None:
            return 1.0
        base = self.defaults["base_conversion_rate"]
        uplift = (persona_cvr - base) / base if base > 0 else 0.0
        return 1.0 + self.weights["persona_weight"] * uplift

    def _historical_adjustment(self, context: ActivationContext) -> float:
        metrics = context.metrics or {}
        historical_cvr = metrics.get("historical_cvr")
        if historical_cvr is None:
            return 1.0
        base = self.defaults["base_conversion_rate"]
        uplift = (historical_cvr - base) / base if base > 0 else 0.0
        return 1.0 + self.weights["historical_weight"] * uplift

    def _intent_stage(self, intent_label: str) -> Optional[str]:
        definition = self.taxonomy.get_intent_definition(intent_label)
        if definition:
            return definition.get("stage")
        return None
