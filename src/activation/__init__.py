"""
Layer 4 Activation package.

This module initializes the activation layer that turns intents and personas
into concrete marketing actions (audience exports, bid adjustments,
personalization hooks, creative briefs).  It mirrors the architecture
described in README.md and docs/emterprise-build.md.
"""

from .base import (
    ActivationComponent,
    ActivationContext,
    ActivationResult,
    ActivationError,
    ActivationPlaybook,
    IntentSignal,
    PersonaProfile,
    AudienceCohort,
    AudienceConnector,
    BidRecommendation,
    BidStrategy,
)
from .bidding import IntentAwareBidOptimizer, ConversionModel, ConversionEstimate
from .audiences import (
    AudienceCohort,
    AudienceConnector,
    GoogleAdsAudienceConnector,
    AudienceManager,
    default_audience_manager,
)

__all__ = [
    "ActivationComponent",
    "ActivationContext",
    "ActivationResult",
    "ActivationError",
    "ActivationPlaybook",
    "IntentSignal",
    "PersonaProfile",
    "BidRecommendation",
    "BidStrategy",
    "IntentAwareBidOptimizer",
    "ConversionModel",
    "ConversionEstimate",
    "AudienceCohort",
    "AudienceConnector",
    "GoogleAdsAudienceConnector",
    "AudienceManager",
    "default_audience_manager",
]
