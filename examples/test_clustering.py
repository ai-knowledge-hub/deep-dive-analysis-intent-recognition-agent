"""
Test Pattern Clustering

This script demonstrates the complete embedding → clustering → visualization pipeline.

Usage:
    python examples/test_clustering.py
"""

import sys
import os
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.patterns.embedder import BehavioralEmbedder
from src.patterns.clustering import PatternClusterer
from src.patterns.visualizer import plot_clusters, plot_cluster_statistics, create_pattern_summary_text


def generate_sample_users(n_users_per_pattern: int = 50):
    """
    Generate synthetic user histories representing different behavioral patterns.

    Creates 3 distinct patterns + some noise:
    1. Research-Heavy Comparers (slow, thorough)
    2. Fast Impulse Buyers (quick decisions)
    3. Budget-Conscious Deal Seekers (price-sensitive)
    4. Random noise users
    """
    all_histories = []

    print(f"📝 Generating {n_users_per_pattern * 3 + 20} synthetic user histories...")

    # Pattern 1: Research-Heavy Comparers
    print(f"   Creating Pattern 1: Research-Heavy Comparers ({n_users_per_pattern} users)")
    for i in range(n_users_per_pattern):
        history = [
            {
                "intent": "category_research",
                "confidence": np.random.uniform(0.80, 0.90),
                "timestamp": f"2025-01-{10+i%5}T10:00:00",
                "channel": "organic",
                "engagement_level": "high",
                "has_budget_constraint": False,
                "has_time_constraint": False,
                "has_knowledge_gap": np.random.choice([True, False]),
                "urgency_level": "low",
                "expertise_level": "intermediate"
            },
            {
                "intent": "compare_options",
                "confidence": np.random.uniform(0.85, 0.95),
                "timestamp": f"2025-01-{12+i%5}T14:00:00",
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
                "confidence": np.random.uniform(0.80, 0.90),
                "timestamp": f"2025-01-{14+i%5}T16:00:00",
                "channel": "email",
                "engagement_level": "high",
                "has_budget_constraint": False,
                "has_time_constraint": np.random.choice([True, False]),
                "has_knowledge_gap": False,
                "urgency_level": "medium",
                "expertise_level": "intermediate"
            },
            {
                "intent": "ready_to_purchase",
                "confidence": np.random.uniform(0.85, 0.95),
                "timestamp": f"2025-01-{15+i%5}T18:00:00",
                "channel": "direct",
                "engagement_level": "very_high",
                "has_budget_constraint": False,
                "has_time_constraint": True,
                "has_knowledge_gap": False,
                "urgency_level": "high",
                "expertise_level": "intermediate"
            }
        ]
        all_histories.append(history)

    # Pattern 2: Fast Impulse Buyers
    print(f"   Creating Pattern 2: Fast Impulse Buyers ({n_users_per_pattern} users)")
    for i in range(n_users_per_pattern):
        history = [
            {
                "intent": np.random.choice(["browsing_inspiration", "category_research"]),
                "confidence": np.random.uniform(0.70, 0.85),
                "timestamp": f"2025-01-{15+i%5}T12:00:00",
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
                "confidence": np.random.uniform(0.75, 0.90),
                "timestamp": f"2025-01-{15+i%5}T12:15:00",
                "channel": "social",
                "engagement_level": "medium",
                "has_budget_constraint": False,
                "has_time_constraint": False,
                "has_knowledge_gap": False,
                "urgency_level": np.random.choice(["low", "medium"]),
                "expertise_level": "intermediate"
            }
        ]
        all_histories.append(history)

    # Pattern 3: Budget-Conscious Deal Seekers
    print(f"   Creating Pattern 3: Budget-Conscious Deal Seekers ({n_users_per_pattern} users)")
    for i in range(n_users_per_pattern):
        history = [
            {
                "intent": "category_research",
                "confidence": np.random.uniform(0.75, 0.85),
                "timestamp": f"2025-01-{5+i%10}T10:00:00",
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
                "confidence": np.random.uniform(0.80, 0.90),
                "timestamp": f"2025-01-{7+i%10}T15:00:00",
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
                "confidence": np.random.uniform(0.85, 0.95),
                "timestamp": f"2025-01-{10+i%10}T11:00:00",
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
                "confidence": np.random.uniform(0.80, 0.90),
                "timestamp": f"2025-01-{15+i%10}T09:00:00",
                "channel": "email",
                "engagement_level": "low",
                "has_budget_constraint": True,
                "has_time_constraint": False,
                "has_knowledge_gap": False,
                "urgency_level": "low",
                "expertise_level": "novice"
            }
        ]
        all_histories.append(history)

    # Add some noise users (random patterns)
    print(f"   Creating noise users (20 users)")
    for i in range(20):
        n_sessions = np.random.randint(1, 4)
        history = []
        for j in range(n_sessions):
            history.append({
                "intent": np.random.choice(["browsing_inspiration", "gift_shopping", "support_seeking"]),
                "confidence": np.random.uniform(0.60, 0.80),
                "timestamp": f"2025-01-{np.random.randint(1, 20)}T{np.random.randint(9, 18)}:00:00",
                "channel": np.random.choice(["organic", "social", "direct"]),
                "engagement_level": np.random.choice(["low", "medium"]),
                "has_budget_constraint": np.random.choice([True, False]),
                "has_time_constraint": np.random.choice([True, False]),
                "has_knowledge_gap": np.random.choice([True, False]),
                "urgency_level": np.random.choice(["low", "medium"]),
                "expertise_level": np.random.choice(["novice", "intermediate"])
            })
        all_histories.append(history)

    return all_histories


def main():
    """Test the complete pattern discovery pipeline."""

    print("\n" + "="*70)
    print("🧪 Testing Pattern Discovery Pipeline")
    print("="*70 + "\n")

    # Step 1: Generate sample data
    user_histories = generate_sample_users(n_users_per_pattern=50)
    print(f"✅ Generated {len(user_histories)} user histories\n")

    # Step 2: Create embeddings
    print("📦 Step 1: Creating Behavioral Embeddings")
    print("-"*70)
    embedder = BehavioralEmbedder()
    embeddings = embedder.create_batch_embeddings(user_histories)
    print(f"✅ Created embeddings: shape = {embeddings.shape}\n")

    # Step 3: Discover patterns
    print("🔍 Step 2: Discovering Behavioral Patterns")
    print("-"*70)
    clusterer = PatternClusterer(
        min_cluster_size=30,  # Smaller for our test data
        min_samples=5
    )
    labels, viz_coords = clusterer.discover_patterns(embeddings)

    # Step 4: Get statistics
    print("\n📊 Step 3: Analyzing Pattern Statistics")
    print("-"*70)
    stats = clusterer.get_cluster_statistics()
    summary_text = create_pattern_summary_text(stats)
    print(summary_text)

    # Step 5: Visualize
    print("\n🎨 Step 4: Creating Visualizations")
    print("-"*70)
    try:
        import matplotlib.pyplot as plt

        # Cluster scatter plot
        print("   Creating cluster visualization...")
        fig1 = plot_clusters(viz_coords, labels)
        plt.savefig('pattern_clusters.png', dpi=300, bbox_inches='tight')
        print("   ✅ Saved: pattern_clusters.png")

        # Statistics plot
        print("   Creating statistics plots...")
        fig2 = plot_cluster_statistics(stats)
        plt.savefig('pattern_statistics.png', dpi=300, bbox_inches='tight')
        print("   ✅ Saved: pattern_statistics.png")

        print("\n   💡 Open the PNG files to see the visualizations!")

    except ImportError:
        print("   ⚠️  matplotlib not available, skipping visualization")

    # Step 6: Examine specific patterns
    print("\n🔬 Step 5: Examining Discovered Patterns")
    print("-"*70)

    for cluster_id, cluster_info in sorted(stats['clusters'].items()):
        print(f"\n🎯 Pattern {cluster_id}:")
        print(f"   Size: {cluster_info['size']} users ({cluster_info['percentage']:.1f}%)")
        print(f"   Cohesion: {cluster_info['cohesion']:.2f}")

        # Get a sample user from this cluster
        member_indices = clusterer.get_cluster_members(cluster_id)
        if len(member_indices) > 0:
            sample_idx = member_indices[0]
            sample_history = user_histories[sample_idx]
            intent_sequence = " → ".join([r['intent'] for r in sample_history])
            print(f"   Sample journey: {intent_sequence}")
            print(f"   Journey length: {len(sample_history)} sessions")

    print("\n" + "="*70)
    print("✅ Pattern Discovery Pipeline Complete!")
    print("="*70)

    print("\n💡 Key Takeaways:")
    print("   1. Embedder transformed user histories into 409-dimensional vectors")
    print("   2. HDBSCAN discovered distinct behavioral patterns automatically")
    print("   3. Visualizations show clear clustering of similar behaviors")
    print("   4. Each pattern represents a targetable audience segment")
    print("\n   📈 This is Layer 3 from the research article working in practice!")
    print()


if __name__ == "__main__":
    main()
