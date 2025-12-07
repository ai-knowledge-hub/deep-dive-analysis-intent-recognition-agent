"""Prebuilt activation playbooks."""

from __future__ import annotations

from typing import Optional

from .base import ActivationComponent, ActivationPlaybook
from .bidding import IntentAwareBidOptimizer
from .creative import CreativeBriefGenerator
from .personalization import (
    ContentPersonalizationEngine,
    RecommendationSelector,
    TriggeredEmailPlanner,
)


class Layer4ActivationPlaybook(ActivationPlaybook):
    """
    Bundles personalization, creative, and bidding components into one playbook.

    This is helpful for the Gradio UI / MCP tools where we want a single call to
    return slot guidance, recommendations, triggered emails, creative briefs,
    and bid modifiers.
    """

    component_name = "layer4_activation_playbook"

    def __init__(
        self,
        *,
        include_bidding: bool = True,
        bid_component: Optional[ActivationComponent] = None,
        enabled: bool = True,
        use_llm_brief: bool = True,
    ) -> None:
        components = [
            ContentPersonalizationEngine(),
            RecommendationSelector(),
            TriggeredEmailPlanner(),
            CreativeBriefGenerator(use_llm=use_llm_brief),
        ]
        if include_bidding:
            components.append(bid_component or IntentAwareBidOptimizer())
        super().__init__(components, enabled=enabled)
