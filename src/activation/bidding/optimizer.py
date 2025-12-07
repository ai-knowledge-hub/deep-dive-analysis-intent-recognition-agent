"""
Intent-aware bid optimization.

Transforms intent signals + persona metrics + historical performance into bid
recommendations, conversion lift estimates, and pacing guidance.
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from ..base import (
    ActivationContext,
    ActivationError,
    BidRecommendation,
    BidStrategy,
    IntentSignal,
)
from ...intent.taxonomy import IntentTaxonomy
from .conversion_model import ConversionModel, ConversionEstimate


class IntentAwareBidOptimizer(BidStrategy):
    """Default bid strategy that respects taxonomy multipliers and context."""

    component_name = "intent_aware_bid_optimizer"

    def __init__(
        self,
        taxonomy: Optional[IntentTaxonomy] = None,
        *,
        config_path: str = "config/activation/bidding.yaml",
        conversion_model: Optional[ConversionModel] = None,
    ) -> None:
        self.base_config = self._load_config(config_path)
        self.taxonomy = taxonomy or IntentTaxonomy.from_domain("ecommerce")
        self._conversion_models: Dict[str, ConversionModel] = {}
        if conversion_model:
            self._conversion_models["default"] = conversion_model
        else:
            self._conversion_models["default"] = ConversionModel(
                self.taxonomy,
                config=self.base_config.get("conversion_model"),
                defaults=self.base_config.get("defaults"),
            )

    # ------------------------------------------------------------------
    # BidStrategy interface
    # ------------------------------------------------------------------
    def recommend(self, context: ActivationContext) -> BidRecommendation:
        if not context.intents:
            raise ActivationError("Bid optimizer requires at least one intent signal.")

        top_intent = context.intents[0]
        channel = (context.metadata or {}).get("channel", "default")
        settings = self._channel_settings(channel)
        conversion_model = self._conversion_model_for_channel(channel, settings)

        taxonomy_modifier = self._taxonomy_modifier(top_intent.label)
        conversion_estimate = conversion_model.predict(context)
        confidence_component = self._confidence_component(top_intent, settings)
        persona_component = self._persona_component(context, settings)
        historical_component = self._historical_component(context, settings)
        conversion_component = self._conversion_component(conversion_estimate, settings)

        raw_modifier = (
            taxonomy_modifier
            + confidence_component
            + persona_component
            + historical_component
            + conversion_component
        )

        modifier = self._clamp_modifier(raw_modifier, settings)
        base_bid = self._base_bid_amount(settings)
        adjusted_bid = base_bid * (1 + modifier)
        pacing = self._pacing_guidance(settings, conversion_estimate.probability, modifier)

        rationale = self._build_rationale(
            taxonomy_modifier,
            confidence_component,
            persona_component,
            historical_component,
            conversion_component,
            pacing,
        )

        metadata = {
            "intent_label": top_intent.label,
            "intent_confidence": top_intent.confidence,
            "channel": channel,
            "conversion_probability": conversion_estimate.probability,
            "conversion_lift": conversion_estimate.lift_vs_baseline,
            "pacing": pacing,
            "inputs": {
                "taxonomy_modifier": taxonomy_modifier,
                "confidence_component": confidence_component,
                "persona_component": persona_component,
                "historical_component": historical_component,
                "conversion_component": conversion_component,
            },
        }

        thresholds = {
            "min_modifier": settings["defaults"]["min_bid_modifier"],
            "max_modifier": settings["defaults"]["max_bid_modifier"],
        }

        return BidRecommendation(
            base_bid=round(adjusted_bid, 4),
            bid_modifier=round(modifier, 4),
            rationale=rationale,
            thresholds=thresholds,
            metadata=metadata,
        )

    # ------------------------------------------------------------------
    # Components
    # ------------------------------------------------------------------
    def _taxonomy_modifier(self, intent_label: str) -> float:
        modifier = self.taxonomy.get_bid_modifier(intent_label)
        return modifier if modifier is not None else 0.0

    def _confidence_component(self, intent: IntentSignal, settings: Dict[str, Any]) -> float:
        neutral = settings["defaults"]["neutral_confidence"]
        weight = settings["bid_weights"]["confidence"]
        return weight * (intent.confidence - neutral)

    def _persona_component(self, context: ActivationContext, settings: Dict[str, Any]) -> float:
        persona = context.persona
        if not persona or not persona.metrics:
            return 0.0
        weight = settings["bid_weights"]["persona_ltv"]
        ltv_index = persona.metrics.get("ltv_index")
        if ltv_index is None:
            return 0.0
        return weight * (ltv_index - 1.0)

    def _historical_component(self, context: ActivationContext, settings: Dict[str, Any]) -> float:
        metrics = context.metrics or {}
        if "recent_roas" not in metrics:
            return 0.0
        target = settings["defaults"]["target_roas"]
        weight = settings["bid_weights"]["historical_roas"]
        roas_ratio = metrics["recent_roas"] / target if target > 0 else 1.0
        return weight * (roas_ratio - 1.0)

    def _conversion_component(self, estimate: ConversionEstimate, settings: Dict[str, Any]) -> float:
        weight = settings["bid_weights"]["conversion_lift"]
        return weight * estimate.lift_vs_baseline

    def _base_bid_amount(self, settings: Dict[str, Any]) -> float:
        return settings["defaults"]["base_cpc"]

    def _clamp_modifier(self, modifier: float, settings: Dict[str, Any]) -> float:
        limits = settings["defaults"]
        return max(limits["min_bid_modifier"], min(modifier, limits["max_bid_modifier"]))

    def _pacing_guidance(self, settings: Dict[str, Any], conversion_prob: float, modifier: float) -> str:
        thresholds = settings.get("pacing_thresholds", {})
        accel_threshold = thresholds.get("accelerate", 0.55)
        maintain_threshold = thresholds.get("maintain", 0.35)

        if conversion_prob >= accel_threshold and modifier > 0:
            return "accelerate"
        if conversion_prob >= maintain_threshold:
            return "maintain"
        if modifier < 0:
            return "decelerate"
        return "monitor"

    def _build_rationale(
        self,
        taxonomy_modifier: float,
        confidence_component: float,
        persona_component: float,
        historical_component: float,
        conversion_component: float,
        pacing: str,
    ) -> str:
        pieces = [
            f"Taxonomy bias={taxonomy_modifier:+.2f}",
            f"confidence={confidence_component:+.2f}",
            f"persona_ltv={persona_component:+.2f}",
            f"historical_roas={historical_component:+.2f}",
            f"conversion_lift={conversion_component:+.2f}",
            f"pacing={pacing}",
        ]
        return "; ".join(pieces)

    # ------------------------------------------------------------------
    # Config loader
    # ------------------------------------------------------------------
    def _load_config(self, path_str: str) -> Dict[str, Dict[str, float]]:
        path = Path(path_str)
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                raw = yaml.safe_load(f) or {}
        else:
            raw = {}
        config = {
            "defaults": {
                "base_cpc": 1.50,
                "base_conversion_rate": 0.02,
                "min_conversion_rate": 0.005,
                "max_conversion_rate": 0.90,
                "neutral_confidence": 0.55,
                "min_bid_modifier": -0.60,
                "max_bid_modifier": 0.90,
                "target_roas": 3.0,
            },
            "conversion_model": {},
            "bid_weights": {
                "confidence": 0.4,
                "persona_ltv": 0.3,
                "historical_roas": 0.2,
                "conversion_lift": 0.5,
            },
            "pacing_thresholds": {"accelerate": 0.55, "maintain": 0.35},
            "channels": {},
        }
        for key in config:
            if key in raw and isinstance(raw[key], dict):
                config[key].update(raw[key])
        return config

    def _channel_settings(self, channel: str) -> Dict[str, Dict[str, float]]:
        settings = copy.deepcopy({k: v for k, v in self.base_config.items() if k != "channels"})
        channel_overrides = self.base_config.get("channels", {}).get(channel, {})
        for key, override in channel_overrides.items():
            if key in settings and isinstance(settings[key], dict) and isinstance(override, dict):
                settings[key].update(override)
            else:
                settings[key] = override
        return settings

    def _conversion_model_for_channel(
        self,
        channel: str,
        settings: Dict[str, Dict[str, float]],
    ) -> ConversionModel:
        if channel not in self._conversion_models:
            self._conversion_models[channel] = ConversionModel(
                self.taxonomy,
                config=settings.get("conversion_model"),
                defaults=settings.get("defaults"),
            )
        return self._conversion_models[channel]
