"""
Intent Recognition Engine - The core system that recognizes user intent from context.

This implements the Context-Conditioned Intent Activation (CCIA) hypothesis from the article:
LLMs can reliably predict human intention when the prompt supplies enough structured
situational context to activate the submanifolds of the model's latent space that encode
human social-goal patterns.
"""

import json
from typing import Dict, Any, Optional

from .taxonomy import IntentTaxonomy
from .llm_provider import BaseLLMProvider, LLMProviderFactory
from ..utils.context_builder import ContextBuilder


class IntentRecognitionEngine:
    """
    Core engine for recognizing user intent from behavioral context.

    This is the Layer 2 (Intent Recognition) from the article's four-layer architecture.
    """

    def __init__(
        self,
        llm_provider: Optional[BaseLLMProvider] = None,
        taxonomy: Optional[IntentTaxonomy] = None,
        prompt_template_path: str = "config/prompts/intent_classification.txt",
        enable_caching: bool = True
    ):
        """
        Initialize the intent recognition engine.

        Args:
            llm_provider: LLM provider instance (defaults to auto-detect from env)
            taxonomy: Intent taxonomy (defaults to ecommerce)
            prompt_template_path: Path to prompt template
            enable_caching: Whether to cache results (simplified for hackathon)
        """
        # Initialize LLM provider
        self.llm = llm_provider or LLMProviderFactory.create_from_env()

        # Initialize taxonomy
        self.taxonomy = taxonomy or IntentTaxonomy.from_domain("ecommerce")

        # Load prompt template
        self.prompt_template = self._load_prompt_template(prompt_template_path)

        # Initialize context builder
        self.context_builder = ContextBuilder()

        # Simple in-memory cache (replace with Redis in production)
        self.cache: Optional[Dict[str, Dict[str, Any]]] = {} if enable_caching else None
        self.enable_caching = enable_caching

    def _load_prompt_template(self, path: str) -> str:
        """Load the prompt template from file."""
        try:
            with open(path, "r") as f:
                return f.read()
        except FileNotFoundError:
            # Fallback to a basic template if file not found
            return self._get_default_prompt_template()

    def _get_default_prompt_template(self) -> str:
        """Fallback prompt template."""
        return """
You are an expert behavioral analyst specializing in customer intent recognition.

Analyze the following context and identify the user's primary intent.

=== USER CONTEXT ===
{context}

=== INTENT TAXONOMY ===
{intent_definitions}

Provide your analysis in JSON format with these fields:
- primary_intent
- confidence (0.0 to 1.0)
- justification
- behavioral_evidence (list)
- predicted_next_actions (list)
- uncertainty_factors (list)

Provide your analysis:
"""

    def recognize_intent(
        self,
        user_query: str = "",
        page_type: str = "",
        previous_actions: str = "",
        time_on_page: int = 0,
        session_history: str = "",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Recognize user intent from behavioral signals.

        This is the main method that combines context building and LLM inference.

        Args:
            user_query: Search query or text input
            page_type: Type of page user is on
            previous_actions: Comma-separated actions
            time_on_page: Seconds on page
            session_history: JSON string of past sessions
            **kwargs: Additional context signals

        Returns:
            Dict containing intent analysis with structure:
            {
                "primary_intent": str,
                "confidence": float,
                "justification": str,
                "secondary_intents": List[Dict],
                "behavioral_evidence": List[str],
                "predicted_next_actions": List[str],
                "uncertainty_factors": List[str],
                "recommended_marketing_actions": List[str],
                "bid_modifier_suggestion": float,
                "conversion_probability": float
            }
        """
        # Step 1: Build structured context
        context = self.context_builder.build_context(
            user_query=user_query,
            page_type=page_type,
            previous_actions=previous_actions,
            time_on_page=time_on_page,
            session_history=session_history,
            **kwargs
        )

        # Step 2: Check cache
        cache_key = self._generate_cache_key(context)
        if self.enable_caching and self.cache is not None and cache_key in self.cache:
            return self.cache[cache_key]

        # Step 3: Format context for LLM
        context_formatted = self.context_builder.format_for_llm(context)

        # Step 4: Build complete prompt
        prompt = self._build_prompt(context_formatted)

        # Step 5: Get LLM inference
        try:
            raw_response = self.llm.generate_sync(
                prompt=prompt,
                system_prompt="You are an expert behavioral analyst for digital marketing."
            )

            # Step 6: Parse LLM response
            result = self._parse_llm_response(raw_response)

            # Step 7: Calibrate confidence (simplified for hackathon)
            result = self._calibrate_confidence(result, context)

            # Step 8: Add recommended actions from taxonomy
            result = self._add_marketing_recommendations(result)

            # Step 9: Cache result
            if self.enable_caching and self.cache is not None:
                self.cache[cache_key] = result

            return result

        except Exception as e:
            # Return error state with fallback
            return self._fallback_response(str(e))

    def _build_prompt(self, formatted_context: str) -> str:
        """Build the complete prompt for the LLM."""
        # Get formatted intent definitions
        intent_definitions = self.taxonomy.format_for_llm()

        # Fill in the template
        prompt = self.prompt_template
        prompt = prompt.replace("{identity_context}", formatted_context)
        prompt = prompt.replace("{historical_context}", formatted_context)
        prompt = prompt.replace("{situational_context}", formatted_context)
        prompt = prompt.replace("{behavioral_signals}", formatted_context)
        prompt = prompt.replace("{temporal_signals}", formatted_context)
        prompt = prompt.replace("{constraint_signals}", formatted_context)
        prompt = prompt.replace("{intent_definitions}", intent_definitions)

        # Simplified: just put full context in one place
        if "{context}" in prompt:
            prompt = prompt.replace("{context}", formatted_context)

        return prompt

    def _parse_llm_response(self, raw_response: str) -> Dict[str, Any]:
        """
        Parse LLM response into structured format.

        Handles both JSON and natural language responses.
        """
        # Try to extract JSON from response
        try:
            # Look for JSON in the response
            start_idx = raw_response.find("{")
            end_idx = raw_response.rfind("}") + 1

            if start_idx != -1 and end_idx > start_idx:
                json_str = raw_response[start_idx:end_idx]
                result = json.loads(json_str)

                # Ensure all required fields are present
                result = self._validate_and_fix_result(result)
                return result
            else:
                # No JSON found, create structured response from text
                return self._parse_natural_language_response(raw_response)

        except json.JSONDecodeError:
            # JSON parsing failed, fall back to natural language parsing
            return self._parse_natural_language_response(raw_response)

    def _validate_and_fix_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure result has all required fields."""
        required_fields = {
            "primary_intent": "unknown",
            "confidence": 0.5,
            "justification": "",
            "secondary_intents": [],
            "behavioral_evidence": [],
            "predicted_next_actions": [],
            "uncertainty_factors": [],
            "recommended_marketing_actions": [],
            "bid_modifier_suggestion": 0.0,
            "conversion_probability": 0.5
        }

        for field, default_value in required_fields.items():
            if field not in result:
                result[field] = default_value

        # Ensure confidence is in valid range
        result["confidence"] = max(0.0, min(1.0, float(result["confidence"])))

        return result

    def _parse_natural_language_response(self, response: str) -> Dict[str, Any]:
        """Parse natural language response when JSON isn't returned."""
        # This is a simplified fallback - in production, use more sophisticated parsing

        # Try to extract intent from common patterns
        intent = "unknown"
        confidence = 0.5

        response_lower = response.lower()

        # Check for each intent in taxonomy
        for intent_label in self.taxonomy.get_all_intent_labels():
            if intent_label.replace("_", " ") in response_lower:
                intent = intent_label
                break

        # Try to extract confidence
        if "high confidence" in response_lower or "very confident" in response_lower:
            confidence = 0.85
        elif "medium confidence" in response_lower or "moderately confident" in response_lower:
            confidence = 0.65
        elif "low confidence" in response_lower:
            confidence = 0.40

        return {
            "primary_intent": intent,
            "confidence": confidence,
            "justification": response[:200],  # First 200 chars as justification
            "secondary_intents": [],
            "behavioral_evidence": ["Extracted from natural language response"],
            "predicted_next_actions": [],
            "uncertainty_factors": ["Response was not in JSON format"],
            "recommended_marketing_actions": [],
            "bid_modifier_suggestion": 0.0,
            "conversion_probability": confidence
        }

    def _calibrate_confidence(
        self,
        result: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calibrate confidence score based on context quality and signal strength.

        This implements basic Hypothesis 3 (Confidence Calibration) from the article.
        In production, this would use historical accuracy data.
        """
        original_confidence = result["confidence"]

        # Start with LLM's confidence
        calibrated = original_confidence

        # Adjust based on context quality
        behavioral = context.get("behavioral_signals", {})
        historical = context.get("historical_context", {})

        # Boost if we have strong signals
        if behavioral.get("engagement_level") in ["high", "very_high"]:
            calibrated += 0.05

        if behavioral.get("action_patterns", {}).get("added_to_cart"):
            calibrated += 0.10

        if len(behavioral.get("actions_taken", [])) > 5:
            calibrated += 0.05

        # Boost if we have historical data
        if historical.get("previous_session_count", 0) > 0:
            calibrated += 0.05

        # Reduce if signals are weak or conflicting
        if behavioral.get("engagement_level") == "very_low":
            calibrated -= 0.10

        if len(behavioral.get("actions_taken", [])) == 0:
            calibrated -= 0.05

        # Ensure in valid range
        calibrated = max(0.0, min(1.0, calibrated))

        result["confidence"] = calibrated
        result["confidence_original"] = original_confidence

        return result

    def _add_marketing_recommendations(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Add marketing recommendations based on intent."""
        intent = result["primary_intent"]

        # Get actions from taxonomy
        actions = self.taxonomy.get_recommended_actions(intent)
        if actions:
            result["recommended_marketing_actions"] = actions

        # Get bid modifier
        bid_modifier = self.taxonomy.get_bid_modifier(intent)
        if bid_modifier != 0.0:
            result["bid_modifier_suggestion"] = bid_modifier

        # Get conversion likelihood from taxonomy
        intent_def = self.taxonomy.get_intent_definition(intent)
        if intent_def:
            result["conversion_probability"] = intent_def.get("conversion_likelihood", 0.5)

        return result

    def _generate_cache_key(self, context: Dict[str, Any]) -> str:
        """Generate cache key from context."""
        # Simplified: use hash of JSON representation
        # In production, use more sophisticated key generation
        context_str = json.dumps(context, sort_keys=True)
        return str(hash(context_str))

    def _fallback_response(self, error_message: str) -> Dict[str, Any]:
        """Return fallback response when LLM fails."""
        return {
            "primary_intent": "unknown",
            "confidence": 0.0,
            "justification": f"Error in intent recognition: {error_message}",
            "secondary_intents": [],
            "behavioral_evidence": [],
            "predicted_next_actions": [],
            "uncertainty_factors": [f"System error: {error_message}"],
            "recommended_marketing_actions": [],
            "bid_modifier_suggestion": 0.0,
            "conversion_probability": 0.0,
            "error": True,
            "error_message": error_message
        }

    def clear_cache(self):
        """Clear the intent cache."""
        if self.cache is not None:
            self.cache = {}

    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        if self.cache is None:
            return {"enabled": False}

        return {
            "enabled": True,
            "size": len(self.cache)
        }
