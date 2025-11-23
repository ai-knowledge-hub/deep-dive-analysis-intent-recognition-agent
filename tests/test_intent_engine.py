"""
Tests for Intent Recognition Engine

Run with: pytest tests/test_intent_engine.py
"""

import pytest
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.intent.engine import IntentRecognitionEngine
from src.intent.taxonomy import IntentTaxonomy
from src.utils.context_builder import ContextBuilder


class TestContextBuilder:
    """Test the context builder."""

    def test_basic_context_building(self):
        """Test basic context construction."""
        builder = ContextBuilder()

        context = builder.build_context(
            user_query="running shoes",
            page_type="search_results",
            previous_actions="viewed_product",
            time_on_page=60
        )

        assert "identity_context" in context
        assert "historical_context" in context
        assert "situational_context" in context
        assert "behavioral_signals" in context
        assert "temporal_signals" in context
        assert "constraint_signals" in context

    def test_query_signal_extraction(self):
        """Test extraction of signals from queries."""
        builder = ContextBuilder()

        # Test budget signal
        context1 = builder.build_context(
            user_query="cheap running shoes under $50",
            page_type="search_results",
            previous_actions="",
            time_on_page=30
        )

        assert context1["constraint_signals"]["has_budget_constraint"] is True

        # Test comparison signal
        context2 = builder.build_context(
            user_query="nike vs adidas running shoes",
            page_type="search_results",
            previous_actions="",
            time_on_page=30
        )

        assert context2["behavioral_signals"]["query_intent_signals"]["has_comparison_words"] is True

    def test_action_pattern_analysis(self):
        """Test analysis of action patterns."""
        builder = ContextBuilder()

        context = builder.build_context(
            user_query="",
            page_type="product_detail",
            previous_actions="viewed_reviews,added_to_cart,checked_shipping",
            time_on_page=180
        )

        patterns = context["behavioral_signals"]["action_patterns"]

        assert patterns["viewed_reviews"] is True
        assert patterns["added_to_cart"] is True
        assert patterns["checked_shipping"] is True

    def test_engagement_classification(self):
        """Test engagement level classification."""
        builder = ContextBuilder()

        # High engagement
        context1 = builder.build_context(
            user_query="",
            page_type="product_detail",
            previous_actions="action1,action2,action3,action4,action5,action6",
            time_on_page=200
        )

        assert context1["behavioral_signals"]["engagement_level"] == "very_high"

        # Low engagement
        context2 = builder.build_context(
            user_query="",
            page_type="homepage",
            previous_actions="",
            time_on_page=10
        )

        assert context2["behavioral_signals"]["engagement_level"] in ["very_low", "low"]


class TestIntentTaxonomy:
    """Test the intent taxonomy."""

    def test_load_ecommerce_taxonomy(self):
        """Test loading ecommerce taxonomy."""
        taxonomy = IntentTaxonomy.from_domain("ecommerce")

        assert taxonomy.name == "Ecommerce Intent Taxonomy"
        assert len(taxonomy.get_all_intent_labels()) > 0
        assert "ready_to_purchase" in taxonomy.get_all_intent_labels()
        assert "compare_options" in taxonomy.get_all_intent_labels()

    def test_get_intent_definition(self):
        """Test retrieving intent definitions."""
        taxonomy = IntentTaxonomy.from_domain("ecommerce")

        intent_def = taxonomy.get_intent_definition("ready_to_purchase")

        assert intent_def is not None
        assert intent_def["stage"] == "decision"
        assert "conversion_likelihood" in intent_def

    def test_get_intents_by_stage(self):
        """Test filtering intents by stage."""
        taxonomy = IntentTaxonomy.from_domain("ecommerce")

        decision_intents = taxonomy.get_intents_by_stage("decision")

        assert len(decision_intents) > 0
        assert "ready_to_purchase" in decision_intents

    def test_recommended_actions(self):
        """Test getting recommended actions."""
        taxonomy = IntentTaxonomy.from_domain("ecommerce")

        actions = taxonomy.get_recommended_actions("ready_to_purchase")

        assert isinstance(actions, list)
        # Should have marketing actions
        assert len(actions) > 0

    def test_format_for_llm(self):
        """Test formatting taxonomy for LLM."""
        taxonomy = IntentTaxonomy.from_domain("ecommerce")

        formatted = taxonomy.format_for_llm()

        assert isinstance(formatted, str)
        assert len(formatted) > 0
        assert "ready_to_purchase" in formatted.lower()


class TestIntentRecognitionEngine:
    """Test the intent recognition engine."""

    @pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"),
        reason="No API key available"
    )
    def test_engine_initialization(self):
        """Test engine initialization."""
        from src.intent.llm_provider import LLMProviderFactory

        llm = LLMProviderFactory.create_from_env()
        taxonomy = IntentTaxonomy.from_domain("ecommerce")

        engine = IntentRecognitionEngine(llm_provider=llm, taxonomy=taxonomy)

        assert engine.llm is not None
        assert engine.taxonomy is not None
        assert engine.context_builder is not None

    def test_fallback_response(self):
        """Test fallback response on error."""
        from src.intent.llm_provider import LLMProviderFactory

        # This will likely fail without a key, testing fallback
        try:
            llm = LLMProviderFactory.create_from_env()
            taxonomy = IntentTaxonomy.from_domain("ecommerce")
            engine = IntentRecognitionEngine(llm_provider=llm, taxonomy=taxonomy)
        except:
            pytest.skip("No API key available")

        # Test with minimal context - might trigger fallback
        result = engine._fallback_response("Test error")

        assert result["primary_intent"] == "unknown"
        assert result["confidence"] == 0.0
        assert result["error"] is True

    def test_result_validation(self):
        """Test result validation and fixing."""
        from src.intent.llm_provider import LLMProviderFactory

        try:
            llm = LLMProviderFactory.create_from_env()
            taxonomy = IntentTaxonomy.from_domain("ecommerce")
            engine = IntentRecognitionEngine(llm_provider=llm, taxonomy=taxonomy)
        except:
            pytest.skip("No API key available")

        # Test with incomplete result
        incomplete = {
            "primary_intent": "compare_options",
            "confidence": 0.85
        }

        fixed = engine._validate_and_fix_result(incomplete)

        assert "primary_intent" in fixed
        assert "confidence" in fixed
        assert "behavioral_evidence" in fixed
        assert "predicted_next_actions" in fixed


class TestSampleContexts:
    """Test with sample context data."""

    def test_load_sample_contexts(self):
        """Test loading sample contexts."""
        with open("data/sample_contexts.json", "r") as f:
            samples = json.load(f)

        assert len(samples) > 0

        # Check first sample has required fields
        first = samples[0]
        assert "user_query" in first
        assert "page_type" in first
        assert "previous_actions" in first
        assert "time_on_page" in first
        assert "expected_intent" in first

    @pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"),
        reason="No API key available"
    )
    def test_intent_recognition_with_samples(self):
        """Test intent recognition with sample data."""
        from src.intent.llm_provider import LLMProviderFactory

        # Load samples
        with open("data/sample_contexts.json", "r") as f:
            samples = json.load(f)

        # Initialize engine
        llm = LLMProviderFactory.create_from_env()
        taxonomy = IntentTaxonomy.from_domain("ecommerce")
        engine = IntentRecognitionEngine(llm_provider=llm, taxonomy=taxonomy)

        # Test with first sample
        sample = samples[0]

        result = engine.recognize_intent(
            user_query=sample["user_query"],
            page_type=sample["page_type"],
            previous_actions=sample["previous_actions"],
            time_on_page=sample["time_on_page"],
            session_history=sample.get("session_history", "")
        )

        # Check result structure
        assert "primary_intent" in result
        assert "confidence" in result
        assert 0.0 <= result["confidence"] <= 1.0

        print(f"\nSample: {sample['name']}")
        print(f"Predicted: {result['primary_intent']} (confidence: {result['confidence']:.2%})")
        print(f"Expected: {sample['expected_intent']}")


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
