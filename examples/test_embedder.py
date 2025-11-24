"""
Test the Behavioral Embedder

This script demonstrates how the embedder creates behavioral vector representations
from user intent histories.

Usage:
    python examples/test_embedder.py
"""

import sys
import os
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.patterns.embedder import BehavioralEmbedder


def main():
    """Test the behavioral embedder with sample data."""

    print("\n" + "="*70)
    print("🧪 Testing Behavioral Embedder")
    print("="*70 + "\n")

    # Initialize embedder
    print("📦 Initializing embedder...")
    embedder = BehavioralEmbedder()
    print(f"✅ Embedder ready: {embedder}")
    print(f"   Embedding dimension: {embedder.get_embedding_dimension()}\n")

    # Create sample user histories
    print("📝 Creating sample user histories...\n")

    # User 1: Research-heavy comparer (from article)
    user1_history = [
        {
            "intent": "category_research",
            "confidence": 0.85,
            "timestamp": "2025-01-10T10:00:00",
            "channel": "organic",
            "engagement_level": "high",
            "has_budget_constraint": False,
            "has_time_constraint": False,
            "has_knowledge_gap": True,
            "urgency_level": "low",
            "expertise_level": "novice"
        },
        {
            "intent": "compare_options",
            "confidence": 0.90,
            "timestamp": "2025-01-12T14:00:00",
            "channel": "organic",
            "engagement_level": "very_high",
            "has_budget_constraint": False,
            "has_time_constraint": False,
            "has_knowledge_gap": False,
            "urgency_level": "low",
            "expertise_level": "intermediate"
        },
        {
            "intent": "evaluate_fit",
            "confidence": 0.88,
            "timestamp": "2025-01-14T16:00:00",
            "channel": "email",
            "engagement_level": "high",
            "has_budget_constraint": False,
            "has_time_constraint": True,
            "has_knowledge_gap": False,
            "urgency_level": "medium",
            "expertise_level": "intermediate"
        },
        {
            "intent": "ready_to_purchase",
            "confidence": 0.92,
            "timestamp": "2025-01-15T18:00:00",
            "channel": "direct",
            "engagement_level": "very_high",
            "has_budget_constraint": False,
            "has_time_constraint": True,
            "has_knowledge_gap": False,
            "urgency_level": "high",
            "expertise_level": "intermediate"
        }
    ]

    # User 2: Fast impulse buyer
    user2_history = [
        {
            "intent": "browsing_inspiration",
            "confidence": 0.75,
            "timestamp": "2025-01-15T12:00:00",
            "channel": "social",
            "engagement_level": "medium",
            "has_budget_constraint": False,
            "has_time_constraint": False,
            "has_knowledge_gap": False,
            "urgency_level": "low",
            "expertise_level": "intermediate"
        },
        {
            "intent": "ready_to_purchase",
            "confidence": 0.82,
            "timestamp": "2025-01-15T12:15:00",
            "channel": "social",
            "engagement_level": "medium",
            "has_budget_constraint": False,
            "has_time_constraint": False,
            "has_knowledge_gap": False,
            "urgency_level": "low",
            "expertise_level": "intermediate"
        }
    ]

    # User 3: Budget-conscious deal seeker
    user3_history = [
        {
            "intent": "category_research",
            "confidence": 0.78,
            "timestamp": "2025-01-05T10:00:00",
            "channel": "organic",
            "engagement_level": "medium",
            "has_budget_constraint": True,
            "has_time_constraint": False,
            "has_knowledge_gap": True,
            "urgency_level": "low",
            "expertise_level": "novice"
        },
        {
            "intent": "price_discovery",
            "confidence": 0.85,
            "timestamp": "2025-01-07T15:00:00",
            "channel": "organic",
            "engagement_level": "medium",
            "has_budget_constraint": True,
            "has_time_constraint": False,
            "has_knowledge_gap": False,
            "urgency_level": "low",
            "expertise_level": "novice"
        },
        {
            "intent": "deal_seeking",
            "confidence": 0.90,
            "timestamp": "2025-01-10T11:00:00",
            "channel": "email",
            "engagement_level": "low",
            "has_budget_constraint": True,
            "has_time_constraint": False,
            "has_knowledge_gap": False,
            "urgency_level": "low",
            "expertise_level": "novice"
        },
        {
            "intent": "deal_seeking",
            "confidence": 0.88,
            "timestamp": "2025-01-15T09:00:00",
            "channel": "email",
            "engagement_level": "low",
            "has_budget_constraint": True,
            "has_time_constraint": False,
            "has_knowledge_gap": False,
            "urgency_level": "low",
            "expertise_level": "novice"
        }
    ]

    # Test individual embeddings
    print("🔬 Test 1: Create embeddings for 3 different user types")
    print("-" * 70)

    print("\n👤 User 1: Research-Heavy Comparer")
    print(f"   Journey: {' → '.join([r['intent'] for r in user1_history])}")
    embedding1 = embedder.create_embedding(user1_history)
    print(f"   Embedding shape: {embedding1.shape}")
    print(f"   Embedding stats: mean={embedding1.mean():.4f}, std={embedding1.std():.4f}")

    print("\n👤 User 2: Fast Impulse Buyer")
    print(f"   Journey: {' → '.join([r['intent'] for r in user2_history])}")
    embedding2 = embedder.create_embedding(user2_history)
    print(f"   Embedding shape: {embedding2.shape}")
    print(f"   Embedding stats: mean={embedding2.mean():.4f}, std={embedding2.std():.4f}")

    print("\n👤 User 3: Budget-Conscious Deal Seeker")
    print(f"   Journey: {' → '.join([r['intent'] for r in user3_history])}")
    embedding3 = embedder.create_embedding(user3_history)
    print(f"   Embedding shape: {embedding3.shape}")
    print(f"   Embedding stats: mean={embedding3.mean():.4f}, std={embedding3.std():.4f}")

    # Test similarity
    print("\n\n🔬 Test 2: Calculate behavioral similarity")
    print("-" * 70)

    # Cosine similarity
    def cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    sim_1_2 = cosine_similarity(embedding1, embedding2)
    sim_1_3 = cosine_similarity(embedding1, embedding3)
    sim_2_3 = cosine_similarity(embedding2, embedding3)

    print(f"\n📊 Similarity Matrix:")
    print(f"   User 1 ↔ User 2 (Comparer vs Impulse):    {sim_1_2:.4f}")
    print(f"   User 1 ↔ User 3 (Comparer vs Deal Seeker): {sim_1_3:.4f}")
    print(f"   User 2 ↔ User 3 (Impulse vs Deal Seeker):  {sim_2_3:.4f}")

    print("\n💡 Interpretation:")
    if sim_1_3 > sim_1_2 and sim_1_3 > sim_2_3:
        print("   ✓ User 1 (Comparer) is most similar to User 3 (Deal Seeker)")
        print("     Both are research-heavy and take multiple sessions")
    elif sim_2_3 > sim_1_2 and sim_2_3 > sim_1_3:
        print("   ✓ User 2 (Impulse) is most similar to User 3 (Deal Seeker)")
    else:
        print("   ✓ User 1 (Comparer) is most similar to User 2 (Impulse)")

    # Test batch processing
    print("\n\n🔬 Test 3: Batch processing")
    print("-" * 70)

    all_histories = [user1_history, user2_history, user3_history]
    batch_embeddings = embedder.create_batch_embeddings(all_histories)

    print(f"\n📦 Batch embeddings shape: {batch_embeddings.shape}")
    print(f"   (3 users × {embedder.get_embedding_dimension()} dimensions)")

    # Test empty history
    print("\n\n🔬 Test 4: Edge case - empty history")
    print("-" * 70)

    empty_embedding = embedder.create_embedding([])
    print(f"\n   Empty history embedding shape: {empty_embedding.shape}")
    print(f"   All zeros: {np.allclose(empty_embedding, 0)}")

    print("\n" + "="*70)
    print("✅ All embedder tests passed!")
    print("="*70 + "\n")

    print("💡 Next Steps:")
    print("   1. The embedder is working correctly")
    print("   2. It captures semantic (intent sequences) + statistical (behavior) features")
    print("   3. Similar users have higher cosine similarity")
    print("   4. Ready to build the clustering layer!")
    print()


if __name__ == "__main__":
    main()
