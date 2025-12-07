"""
Base interfaces for Layer 4 activation components.

Layer 4 turns intent recognition + pattern discovery outputs into actions:
audience creation, bid optimization, personalization, and creative guidance.
Each activation module should subclass `ActivationComponent` so the rest of
the system can orchestrate them consistently (CLI, MCP, Gradio, or API).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional


@dataclass
class IntentSignal:
    """
    Structured representation of an intent prediction.

    Attributes:
        label: Canonical intent label (e.g., "ready_to_purchase").
        confidence: Confidence score (0.0-1.0) after calibration.
        stage: Funnel stage or taxonomy grouping.
        evidence: Key behavioral signals that justify the classification.
        metadata: Arbitrary extra data (LLM response, bid multipliers, etc.).
    """

    label: str
    confidence: float
    stage: Optional[str] = None
    evidence: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PersonaProfile:
    """
    Representation of a behavioral persona discovered in Layer 3.

    Attributes:
        name: Human-friendly persona name.
        description: Markdown/HTML description for stakeholders.
        size: Absolute number of users in the cluster.
        share: Percentage of total traffic/users.
        intent_distribution: Mapping of intent label → share.
        metrics: Performance metrics (CVR, AOV, LTV, etc.).
        metadata: Extra data (recommended bid modifier, copy cues, etc.).
    """

    name: str
    description: str
    size: int
    share: float
    intent_distribution: Dict[str, float] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ActivationContext:
    """
    Carries the upstream signals required for activation.

    Attributes:
        intents: Primary + secondary intent predictions for the user/persona.
        persona: Optional persona descriptor from Pattern Discovery.
        metrics: Observed performance metrics (conversion rate, AOV, etc.).
        metadata: Free-form dictionary for channel-specific fields.
            Expected optional keys:
                - preferred_channels: list of activation channels to prioritize.
                - available_assets: dict describing reusable creative assets.
                - creative_history: prior creative performance metrics/logs.
                - personalization_context: ad-hoc signals for slot rules.
    """

    intents: List[IntentSignal]
    persona: Optional[PersonaProfile] = None
    metrics: Optional[Dict[str, float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ActivationResult:
    """
    Standard response envelope for activation modules.

    Attributes:
        actions: Structured actions produced (e.g., bid modifiers, segments).
        diagnostics: Human-readable summary explaining the decisions.
        metadata: Extra machine-readable outputs for downstream systems.
    """

    actions: List[Dict[str, Any]] = field(default_factory=list)
    diagnostics: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ActivationError(RuntimeError):
    """Raised when an activation component cannot complete its task."""


class ActivationComponent(ABC):
    """
    Abstract base class for all Layer 4 components.

    Subclasses implement specific capabilities (audience exporters, bid
    strategies, personalization hooks, creative generators).  They receive an
    `ActivationContext` and return an `ActivationResult`.
    """

    component_name: str = "activation_component"

    def __init__(self, *, enabled: bool = True) -> None:
        self.enabled = enabled

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"{self.__class__.__name__}(enabled={self.enabled})"

    def validate(self, context: ActivationContext) -> None:
        """Hook for subclasses to validate the incoming context."""

    @abstractmethod
    def execute(self, context: ActivationContext) -> ActivationResult:
        """
        Run the component for the provided context.

        Raises:
            ActivationError: if the component cannot complete successfully.
        """

    def run(self, context: ActivationContext) -> ActivationResult:
        """
        Convenience wrapper that handles validation and enabled checks.
        """
        if not self.enabled:
            return ActivationResult(
                actions=[],
                diagnostics=[f"{self.component_name} disabled, skipping."],
            )

        self.validate(context)
        return self.execute(context)


class ActivationPlaybook(ActivationComponent):
    """
    Orchestrates multiple activation components as a single playbook.

    Example: build audience + calculate bid modifiers + generate creative
    brief for a persona before syncing to downstream platforms.
    """

    component_name = "activation_playbook"

    def __init__(
        self,
        components: Iterable[ActivationComponent],
        *,
        enabled: bool = True,
    ) -> None:
        super().__init__(enabled=enabled)
        self.components = list(components)

    def execute(self, context: ActivationContext) -> ActivationResult:
        master = ActivationResult()
        for component in self.components:
            result = component.run(context)
            master.actions.extend(result.actions)
            master.diagnostics.extend(result.diagnostics)
            master.metadata.setdefault(component.component_name, result.metadata)
        return master


@dataclass
class AudienceCohort:
    """
    Data model for a cohort that will be synced to media platforms.

    Attributes:
        name: Display name for the audience/segment.
        description: Optional longer description.
        user_ids: Identifiers (hashed emails, device IDs, etc.).
        metadata: Additional sync settings (lifetime, platform-specific IDs).
    """

    name: str
    description: str
    user_ids: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


class AudienceConnector(ActivationComponent):
    """
    Base class for channel-specific audience exporters (Google, Meta, etc.).
    """

    component_name = "audience_connector"

    @abstractmethod
    def sync(self, cohort: AudienceCohort, context: ActivationContext) -> Dict[str, Any]:
        """Push the cohort to the downstream platform and return identifiers."""

    def execute(self, context: ActivationContext) -> ActivationResult:
        cohort = context.metadata.get("audience_cohort")
        if not isinstance(cohort, AudienceCohort):
            raise ActivationError("AudienceConnector requires `audience_cohort` in metadata.")
        response = self.sync(cohort, context)
        return ActivationResult(
            actions=[{"type": "audience_sync", "platform": self.component_name, **response}],
            diagnostics=[f"Synced cohort '{cohort.name}' via {self.component_name}."],
            metadata=response,
        )


@dataclass
class BidRecommendation:
    """
    Structured bid recommendations returned by bid strategies.

    Attributes:
        base_bid: Suggested base bid (e.g., CPC) before modifiers.
        bid_modifier: Relative adjustment (e.g., +0.25 = +25%).
        rationale: Human-readable explanation for the modifier.
        thresholds: Optional guardrails (min/max bid).
        metadata: Channel-specific extras (campaign ID, pacing notes).
    """

    base_bid: Optional[float]
    bid_modifier: float
    rationale: str
    thresholds: Optional[Dict[str, float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class BidStrategy(ActivationComponent):
    """
    Base class for converting intent signals to bid recommendations.
    """

    component_name = "bid_strategy"

    @abstractmethod
    def recommend(self, context: ActivationContext) -> BidRecommendation:
        """Return bid modifier guidance based on the provided context."""

    def execute(self, context: ActivationContext) -> ActivationResult:
        recommendation = self.recommend(context)
        return ActivationResult(
            actions=[
                {
                    "type": "bid_recommendation",
                    "base_bid": recommendation.base_bid,
                    "bid_modifier": recommendation.bid_modifier,
                    "thresholds": recommendation.thresholds,
                }
            ],
            diagnostics=[recommendation.rationale],
            metadata=recommendation.metadata,
        )
