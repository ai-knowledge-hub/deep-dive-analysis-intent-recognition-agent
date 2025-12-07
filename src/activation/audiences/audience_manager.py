"""
Audience manager orchestration.

Provides a high-level API for syncing cohorts to downstream channels using the
AudienceConnector interface.
"""

from __future__ import annotations

from typing import Dict, Optional

from ..base import ActivationContext, ActivationError, AudienceCohort, ActivationComponent
from .google_ads import GoogleAdsAudienceConnector
from .meta_ads import MetaAdsAudienceConnector


class AudienceManager:
    """Simple registry + orchestrator for audience connectors."""

    def __init__(self) -> None:
        self._connectors: Dict[str, AudienceConnector] = {}

    def register(self, connector: "AudienceConnector") -> None:
        self._connectors[connector.component_name] = connector

    def get(self, channel: str) -> "AudienceConnector":
        if channel not in self._connectors:
            raise ActivationError(f"No audience connector registered for '{channel}'.")
        return self._connectors[channel]

    def sync(
        self,
        channel: str,
        cohort: AudienceCohort,
        context: ActivationContext,
        *,
        dry_run: Optional[bool] = None,
    ) -> Dict[str, object]:
        connector = self.get(channel)
        if dry_run is not None and hasattr(connector, "dry_run"):
            connector.dry_run = dry_run  # type: ignore[attr-defined]
        return connector.sync(cohort, context)


def default_audience_manager() -> AudienceManager:
    """Factory with the Google Ads connector registered."""
    manager = AudienceManager()
    manager.register(GoogleAdsAudienceConnector())
    manager.register(MetaAdsAudienceConnector())
    return manager


# Keep import at bottom to avoid circular dependency in typing context.
from ..base import AudienceConnector  # noqa: E402
