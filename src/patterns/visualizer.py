"""
Pattern Visualization - Creates visual representations of discovered patterns.

Generates plots for understanding and presenting behavioral patterns to stakeholders.
"""

import numpy as np
from typing import Optional, Dict, Any
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


def plot_clusters(
    coordinates: np.ndarray,
    labels: np.ndarray,
    title: str = "Discovered Behavioral Patterns",
    figsize: tuple = (12, 8),
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Create a scatter plot of discovered clusters.

    Args:
        coordinates: 2D array of shape (n_users, 2) - visualization coordinates
        labels: Array of shape (n_users,) - cluster assignments
        title: Plot title
        figsize: Figure size
        save_path: If provided, save plot to this path

    Returns:
        matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=figsize)

    # Get unique clusters (excluding noise)
    unique_labels = set(labels)
    n_clusters = len(unique_labels) - (1 if -1 in unique_labels else 0)

    # Color map
    colors = plt.cm.Spectral(np.linspace(0, 1, n_clusters))

    # Plot each cluster
    for i, (label, color) in enumerate(zip(sorted(unique_labels), colors)):
        if label == -1:
            # Noise points in gray
            mask = labels == label
            ax.scatter(
                coordinates[mask, 0],
                coordinates[mask, 1],
                c='lightgray',
                s=30,
                alpha=0.3,
                label='Noise/Outliers',
                marker='x'
            )
        else:
            mask = labels == label
            count = mask.sum()
            percentage = count / len(labels) * 100

            ax.scatter(
                coordinates[mask, 0],
                coordinates[mask, 1],
                c=[color],
                s=50,
                alpha=0.6,
                label=f'Pattern {label}: {count} users ({percentage:.1f}%)',
                edgecolors='white',
                linewidth=0.5
            )

    ax.set_title(title, fontsize=16, fontweight='bold')
    ax.set_xlabel('Principal Component 1', fontsize=12)
    ax.set_ylabel('Principal Component 2', fontsize=12)
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"   💾 Visualization saved to: {save_path}")

    return fig


def plot_cluster_statistics(
    cluster_stats: Dict[str, Any],
    figsize: tuple = (14, 6),
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Create a dashboard of cluster statistics.

    Args:
        cluster_stats: Dictionary from PatternClusterer.get_cluster_statistics()
        figsize: Figure size
        save_path: If provided, save plot to this path

    Returns:
        matplotlib Figure object
    """
    fig, axes = plt.subplots(1, 2, figsize=figsize)

    # Extract data
    clusters = cluster_stats['clusters']
    if not clusters:
        print("⚠️  No clusters to visualize")
        return fig

    cluster_ids = list(clusters.keys())
    sizes = [clusters[cid]['size'] for cid in cluster_ids]
    cohesions = [clusters[cid]['cohesion'] for cid in cluster_ids]

    # Plot 1: Cluster sizes
    ax1 = axes[0]
    bars1 = ax1.bar(
        [f"Pattern {cid}" for cid in cluster_ids],
        sizes,
        color=plt.cm.Spectral(np.linspace(0, 1, len(cluster_ids))),
        alpha=0.7
    )
    ax1.set_title('Pattern Sizes', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Pattern ID', fontsize=12)
    ax1.set_ylabel('Number of Users', fontsize=12)
    ax1.grid(True, alpha=0.3, axis='y')

    # Add percentage labels on bars
    for bar, size in zip(bars1, sizes):
        height = bar.get_height()
        percentage = size / cluster_stats['n_total'] * 100
        ax1.text(
            bar.get_x() + bar.get_width() / 2.,
            height,
            f'{percentage:.1f}%',
            ha='center',
            va='bottom',
            fontsize=10
        )

    # Plot 2: Cluster cohesion (membership confidence)
    ax2 = axes[1]
    bars2 = ax2.bar(
        [f"Pattern {cid}" for cid in cluster_ids],
        cohesions,
        color=plt.cm.Spectral(np.linspace(0, 1, len(cluster_ids))),
        alpha=0.7
    )
    ax2.set_title('Pattern Cohesion (Avg Membership Probability)', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Pattern ID', fontsize=12)
    ax2.set_ylabel('Cohesion Score', fontsize=12)
    ax2.set_ylim(0, 1.0)
    ax2.grid(True, alpha=0.3, axis='y')

    # Add value labels on bars
    for bar, cohesion in zip(bars2, cohesions):
        height = bar.get_height()
        ax2.text(
            bar.get_x() + bar.get_width() / 2.,
            height,
            f'{cohesion:.2f}',
            ha='center',
            va='bottom',
            fontsize=10
        )

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"   💾 Statistics plot saved to: {save_path}")

    return fig


def create_pattern_summary_text(cluster_stats: Dict[str, Any]) -> str:
    """
    Create a text summary of discovered patterns.

    Args:
        cluster_stats: Dictionary from PatternClusterer.get_cluster_statistics()

    Returns:
        Formatted text summary
    """
    summary = []
    summary.append("\n" + "="*70)
    summary.append("📊 PATTERN DISCOVERY SUMMARY")
    summary.append("="*70)

    summary.append(f"\nTotal Users Analyzed: {cluster_stats['n_total']}")
    summary.append(f"Patterns Discovered: {cluster_stats['n_clusters']}")
    summary.append(f"Noise/Outliers: {cluster_stats['n_noise']} ({cluster_stats['noise_percentage']:.1f}%)")

    if cluster_stats['n_clusters'] > 0:
        summary.append(f"\nAverage Pattern Size: {cluster_stats['avg_cluster_size']:.0f} users")
        summary.append(f"Largest Pattern: {cluster_stats['largest_cluster_size']} users")
        summary.append(f"Smallest Pattern: {cluster_stats['smallest_cluster_size']} users")

        summary.append("\n" + "-"*70)
        summary.append("PATTERN DETAILS:")
        summary.append("-"*70)

        for cluster_id, stats in sorted(cluster_stats['clusters'].items()):
            summary.append(f"\n🎯 Pattern {cluster_id}:")
            summary.append(f"   Size: {stats['size']} users ({stats['percentage']:.1f}% of total)")
            summary.append(f"   Cohesion: {stats['cohesion']:.2f} (avg membership probability)")
            summary.append(f"   Range: {stats['min_membership_probability']:.2f} - {stats['max_membership_probability']:.2f}")

    summary.append("\n" + "="*70)

    return "\n".join(summary)
