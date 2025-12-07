from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.activation import ActivationContext, IntentSignal, PersonaProfile
from src.activation.bidding import ConversionModel, IntentAwareBidOptimizer
from src.intent import IntentTaxonomy


def build_sample_context() -> ActivationContext:
    taxonomy = IntentTaxonomy.from_domain("ecommerce")
    intent_signal = IntentSignal(
        label="ready_to_purchase",
        confidence=0.9,
        stage="decision",
        evidence=["checkout_initiation"],
    )
    persona = PersonaProfile(
        name="High Intent Buyers",
        description="Users who initiate checkout within two sessions",
        size=500,
        share=0.25,
        intent_distribution={"ready_to_purchase": 0.8},
        metrics={"conversion_rate": 0.6, "ltv_index": 1.3},
    )
    metrics = {"historical_cvr": 0.5, "recent_roas": 3.8}
    return ActivationContext(
        intents=[intent_signal],
        persona=persona,
        metrics=metrics,
        metadata={"channel": "google_ads"},
    )


def test_conversion_model_predicts_probability_within_bounds():
    taxonomy = IntentTaxonomy.from_domain("ecommerce")
    model = ConversionModel(taxonomy)
    context = build_sample_context()
    estimate = model.predict(context)
    assert 0.005 <= estimate.probability <= 0.90
    assert estimate.contributions["base"] > 0
    assert estimate.lift_vs_baseline > 0


def test_bid_optimizer_returns_recommendation_with_metadata():
    taxonomy = IntentTaxonomy.from_domain("ecommerce")
    optimizer = IntentAwareBidOptimizer(taxonomy=taxonomy)
    context = build_sample_context()
    recommendation = optimizer.recommend(context)

    assert recommendation.base_bid and recommendation.base_bid > 0
    assert -0.6 <= recommendation.bid_modifier <= 1.2
    assert "pacing" in recommendation.metadata
    assert math.isclose(
        recommendation.metadata["intent_confidence"],
        context.intents[0].confidence,
    )


def test_bid_optimizer_respects_channel_overrides():
    taxonomy = IntentTaxonomy.from_domain("ecommerce")
    optimizer = IntentAwareBidOptimizer(taxonomy=taxonomy)
    context = build_sample_context()
    context.metadata["channel"] = "meta_ads"
    rec_meta = optimizer.recommend(context)

    context.metadata["channel"] = "google_ads"
    rec_google = optimizer.recommend(context)

    assert rec_meta.metadata["channel"] == "meta_ads"
    assert rec_google.metadata["channel"] == "google_ads"
    assert rec_meta.bid_modifier != rec_google.bid_modifier
