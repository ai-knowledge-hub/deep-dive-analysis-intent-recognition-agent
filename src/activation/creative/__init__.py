"""
Creative activation subpackage.

Provides helpers that translate intent/pattern signals into creative briefs,
copy templates, or LLM-powered content suggestions for marketing teams.
"""

from ..base import ActivationComponent, ActivationContext, ActivationResult
from .generator import CreativeBriefGenerator

__all__ = [
    "ActivationComponent",
    "ActivationContext",
    "ActivationResult",
    "CreativeBriefGenerator",
]
