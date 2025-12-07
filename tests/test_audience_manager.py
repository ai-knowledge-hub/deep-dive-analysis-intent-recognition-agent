from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.activation import (
    ActivationContext,
    ActivationError,
    AudienceCohort,
    IntentSignal,
)
from src.activation.audiences import AudienceManager, GoogleAdsAudienceConnector


def build_context() -> ActivationContext:
    intent = IntentSignal(
        label="ready_to_purchase",
        confidence=0.9,
        stage="decision",
        evidence=["checkout_initiation"],
    )
    return ActivationContext(intents=[intent], persona=None, metrics=None, metadata={})


def test_google_ads_connector_dry_run():
    connector = GoogleAdsAudienceConnector(dry_run=True)
    cohort = AudienceCohort(
        name="Test Audience",
        description="Dry run test",
        user_ids=["user@example.com", "second@example.com"],
    )
    result = connector.sync(cohort, build_context())

    assert result["status"] == "simulated_upload"
    assert result["user_count"] == 2
    assert result["batch_count"] == 1
    assert len(result["sample_hash"]) == 2


def test_audience_manager_register_and_sync():
    manager = AudienceManager()
    manager.register(GoogleAdsAudienceConnector(dry_run=True))

    cohort = AudienceCohort(
        name="Manager Audience",
        description="Manager test",
        user_ids=["alpha@example.com", "beta@example.com", "gamma@example.com"],
    )

    result = manager.sync("google_ads", cohort, build_context())
    assert result["status"] == "simulated_upload"
    assert result["batch_count"] == 1


def test_audience_manager_missing_connector():
    manager = AudienceManager()
    cohort = AudienceCohort(name="Sample", description="", user_ids=["one@example.com"])
    try:
        manager.sync("meta_ads", cohort, build_context())
    except ActivationError as exc:
        assert "No audience connector" in str(exc)
    else:
        raise AssertionError("Expected ActivationError")
