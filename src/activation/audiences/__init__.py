"""
Audience activation subpackage.

Exports intent/persona cohorts into downstream platforms and manages audience
lifecycle operations (create, update, archive).
"""

from ..base import (
    ActivationComponent,
    ActivationContext,
    ActivationResult,
    AudienceCohort,
    AudienceConnector,
)
from .google_ads import GoogleAdsAudienceConnector
from .meta_ads import MetaAdsAudienceConnector
from .audience_manager import AudienceManager, default_audience_manager

__all__ = [
    "ActivationComponent",
    "ActivationContext",
    "ActivationResult",
    "AudienceCohort",
    "AudienceConnector",
    "GoogleAdsAudienceConnector",
    "MetaAdsAudienceConnector",
    "AudienceManager",
    "default_audience_manager",
]
