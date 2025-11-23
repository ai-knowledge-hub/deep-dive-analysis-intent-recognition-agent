"""
Basic Intent Recognition Example

This script demonstrates how to use the intent recognition engine directly
(without the Gradio interface).

Usage:
    python examples/basic_intent_recognition.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from src.intent.engine import IntentRecognitionEngine
from src.intent.taxonomy import IntentTaxonomy
from src.intent.llm_provider import LLMProviderFactory


def main():
    """Run basic intent recognition examples."""

    print("\n" + "="*70)
    print("🎯 Intent Recognition Engine - Basic Example")
    print("="*70 + "\n")

    # Load environment variables
    load_dotenv()

    # Check for API keys
    if not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: No API key found!")
        print("Please set ANTHROPIC_API_KEY or OPENAI_API_KEY in your .env file")
        print("\nExample:")
        print("  ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)

    try:
        # Initialize engine
        print("🔧 Initializing Intent Recognition Engine...")

        llm_provider = LLMProviderFactory.create_from_env()
        taxonomy = IntentTaxonomy.from_domain("ecommerce")
        engine = IntentRecognitionEngine(llm_provider=llm_provider, taxonomy=taxonomy)

        print("✅ Engine initialized successfully!\n")
        print(f"Using taxonomy: {taxonomy.name}")
        print(f"Available intents: {len(taxonomy.get_all_intent_labels())}\n")
        print("-"*70 + "\n")

    except Exception as e:
        print(f"❌ Error initializing engine: {e}")
        sys.exit(1)

    # Example 1: High-intent purchase scenario
    print("📊 Example 1: High-Intent Purchase (Marathon Runner)")
    print("-"*70)

    result1 = engine.recognize_intent(
        user_query="nike pegasus 40 stability features",
        page_type="product_detail",
        previous_actions="searched_marathon_shoes,viewed_3_products,read_reviews,zoomed_arch_support_image,checked_return_policy",
        time_on_page=245,
        session_history='[{"intent": "category_research"}, {"intent": "compare_options"}]'
    )

    print(f"Primary Intent: {result1['primary_intent']}")
    print(f"Confidence: {result1['confidence']:.2%}")
    print(f"Justification: {result1['justification'][:150]}...")
    print(f"Bid Modifier: {result1['bid_modifier_suggestion']:+.0%}")
    print(f"Conversion Probability: {result1['conversion_probability']:.0%}")
    print()

    # Example 2: Budget-conscious comparison shopping
    print("📊 Example 2: Budget-Conscious Comparison")
    print("-"*70)

    result2 = engine.recognize_intent(
        user_query="best running shoes under $100",
        page_type="search_results",
        previous_actions="filtered_by_price,sorted_by_price,viewed_2_products",
        time_on_page=120
    )

    print(f"Primary Intent: {result2['primary_intent']}")
    print(f"Confidence: {result2['confidence']:.2%}")
    print(f"Justification: {result2['justification'][:150]}...")
    print(f"Recommended Actions:")
    for action in result2['recommended_marketing_actions'][:3]:
        print(f"  • {action}")
    print()

    # Example 3: Gift shopping
    print("📊 Example 3: Gift Shopping")
    print("-"*70)

    result3 = engine.recognize_intent(
        user_query="popular gifts for runners",
        page_type="category",
        previous_actions="viewed_gift_guide,clicked_best_sellers,viewed_gift_wrap_options",
        time_on_page=90
    )

    print(f"Primary Intent: {result3['primary_intent']}")
    print(f"Confidence: {result3['confidence']:.2%}")
    print(f"Predicted Next Actions:")
    for action in result3['predicted_next_actions']:
        print(f"  • {action}")
    print()

    # Show cache stats
    print("📈 Cache Statistics")
    print("-"*70)
    cache_stats = engine.get_cache_stats()
    print(f"Cache enabled: {cache_stats.get('enabled', False)}")
    if cache_stats.get('enabled'):
        print(f"Cache size: {cache_stats.get('size', 0)} entries")
    print()

    print("="*70)
    print("✨ Done! All examples completed successfully.")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
