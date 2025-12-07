"""
Personalization activation subpackage.

Contains modules that orchestrate on-site/app/email personalization using
recognized intents and personas (e.g., content selection, recommendations,
next-best-action logic).
"""

from ..base import ActivationComponent, ActivationContext, ActivationResult
from .content import ContentPersonalizationEngine
from .recommendations import RecommendationSelector
from .email import TriggeredEmailPlanner

__all__ = [
    "ActivationComponent",
    "ActivationContext",
    "ActivationResult",
    "ContentPersonalizationEngine",
    "RecommendationSelector",
    "TriggeredEmailPlanner",
]
