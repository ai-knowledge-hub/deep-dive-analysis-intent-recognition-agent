"""
Intent Taxonomy Loader - Loads and manages intent definitions from YAML files.

This module handles loading intent taxonomies, which define the possible intents
and their characteristics for different domains (ecommerce, B2B SaaS, etc.)
"""

import yaml
from typing import Dict, Any, List, Optional
from pathlib import Path


class IntentTaxonomy:
    """Manages intent taxonomy definitions."""

    def __init__(self, taxonomy_data: Dict[str, Any]):
        """
        Initialize with taxonomy data.

        Args:
            taxonomy_data: Dictionary containing taxonomy definition
        """
        self.name = taxonomy_data.get("name", "Unknown Taxonomy")
        self.version = taxonomy_data.get("version", "1.0")
        self.description = taxonomy_data.get("description", "")
        self.domain = taxonomy_data.get("domain", "general")
        self.intents = taxonomy_data.get("intents", {})
        self.confidence_modifiers = taxonomy_data.get("confidence_modifiers", {})
        self.transitions = taxonomy_data.get("transitions", {})
        self.recommended_actions = taxonomy_data.get("recommended_actions", {})

    @classmethod
    def from_file(cls, filepath: str) -> "IntentTaxonomy":
        """
        Load taxonomy from YAML file.

        Args:
            filepath: Path to YAML file

        Returns:
            IntentTaxonomy instance
        """
        with open(filepath, "r") as f:
            data = yaml.safe_load(f)
        return cls(data)

    @classmethod
    def from_domain(cls, domain: str, config_dir: str = "config/intent_taxonomies") -> "IntentTaxonomy":
        """
        Load taxonomy for a specific domain.

        Args:
            domain: Domain name (e.g., 'ecommerce', 'b2b_saas')
            config_dir: Directory containing taxonomy files

        Returns:
            IntentTaxonomy instance
        """
        filepath = Path(config_dir) / f"{domain}.yaml"
        return cls.from_file(str(filepath))

    def get_intent_definition(self, intent_label: str) -> Optional[Dict[str, Any]]:
        """Get definition for a specific intent."""
        return self.intents.get(intent_label)

    def get_all_intent_labels(self) -> List[str]:
        """Get list of all intent labels."""
        return list(self.intents.keys())

    def get_intents_by_stage(self, stage: str) -> List[str]:
        """
        Get all intents for a specific stage.

        Args:
            stage: Stage name (awareness, consideration, decision, etc.)

        Returns:
            List of intent labels for that stage
        """
        return [
            label
            for label, definition in self.intents.items()
            if definition.get("stage") == stage
        ]

    def get_confidence_modifier(self, signal_name: str) -> float:
        """
        Get confidence modifier for a specific signal.

        Args:
            signal_name: Name of the behavioral signal

        Returns:
            Modifier value (positive or negative)
        """
        # Check in strong signals
        if signal_name in self.confidence_modifiers.get("strong_signals", {}):
            return self.confidence_modifiers["strong_signals"][signal_name]

        # Check in weak signals
        if signal_name in self.confidence_modifiers.get("weak_signals", {}):
            return self.confidence_modifiers["weak_signals"][signal_name]

        # Check in temporal factors
        if signal_name in self.confidence_modifiers.get("temporal_factors", {}):
            return self.confidence_modifiers["temporal_factors"][signal_name]

        return 0.0  # No modifier

    def get_recommended_actions(self, intent_label: str) -> List[str]:
        """Get recommended marketing actions for an intent."""
        actions = self.recommended_actions.get(intent_label, [])
        if isinstance(actions, list):
            return actions
        else:
            # If stored as dict, extract action items
            return [a for a in actions if not a.startswith("bid_modifier")]

    def get_bid_modifier(self, intent_label: str) -> float:
        """Get recommended bid modifier for an intent."""
        actions = self.recommended_actions.get(intent_label, [])
        if isinstance(actions, list):
            for action in actions:
                if isinstance(action, str) and "bid_modifier" in action:
                    try:
                        return float(action.split(":")[-1].strip())
                    except ValueError:
                        continue
                if isinstance(action, dict) and "bid_modifier" in action:
                    try:
                        return float(action["bid_modifier"])
                    except (TypeError, ValueError):
                        continue
        elif isinstance(actions, dict) and "bid_modifier" in actions:
            try:
                return float(actions["bid_modifier"])
            except (TypeError, ValueError):
                return 0.0
        return 0.0

    def get_likely_next_intents(self, current_intent: str) -> List[tuple[str, float]]:
        """
        Get likely next intents based on transition probabilities.

        Args:
            current_intent: Current intent label

        Returns:
            List of (intent_label, probability) tuples
        """
        transitions = self.transitions.get(current_intent, {})
        return [(intent, prob) for intent, prob in transitions.items()]

    def format_for_llm(self) -> str:
        """
        Format taxonomy for inclusion in LLM prompt.

        Returns:
            Formatted string describing all intents
        """
        formatted_intents = []

        for label, definition in self.intents.items():
            intent_desc = f"""
{label.upper()}:
- Description: {definition.get('description', 'No description')}
- Stage: {definition.get('stage', 'unknown')}
- Typical Signals: {', '.join(definition.get('typical_signals', []))}
- Conversion Likelihood: {definition.get('conversion_likelihood', 0.0):.0%}
"""
            formatted_intents.append(intent_desc.strip())

        return "\n\n".join(formatted_intents)

    def __repr__(self) -> str:
        return f"IntentTaxonomy(name='{self.name}', domain='{self.domain}', intents={len(self.intents)})"
