"""
Bidding activation subpackage.

Hosts bid optimization strategies, conversion models, and pacing logic that
transform intent confidence into actionable bid modifiers per channel.
"""

from ..base import ActivationComponent, ActivationContext, ActivationResult
from .conversion_model import ConversionModel, ConversionEstimate
from .optimizer import IntentAwareBidOptimizer

__all__ = [
    "ActivationComponent",
    "ActivationContext",
    "ActivationResult",
    "ConversionModel",
    "ConversionEstimate",
    "IntentAwareBidOptimizer",
]
