"""
Personalization activation subpackage.

Contains modules that orchestrate on-site/app/email personalization using
recognized intents and personas (e.g., content selection, recommendations,
next-best-action logic).
"""

from ..base import ActivationComponent, ActivationContext, ActivationResult

__all__ = [
    "ActivationComponent",
    "ActivationContext",
    "ActivationResult",
]
