"""
Pattern Clustering - Discovers behavioral patterns using HDBSCAN.

This implements Step 2 of Pattern Discovery from the article:
"Cluster similar behavioral patterns. Find users whose behavioral signatures look alike."

From article: "Use clustering algorithms to find users who behave similarly across multiple dimensions.
These clusters become your audiences - not demographic segments but intentional archetypes."

Key Research Finding: Stable patterns (>70% overlap across months) represent real audience segments.
"""

import numpy as np
from typing import Tuple, Optional, Dict, Any, TYPE_CHECKING, Type, cast
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import warnings

# Suppress HDBSCAN warnings for cleaner output
warnings.filterwarnings('ignore', category=UserWarning)

try:
    from hdbscan import HDBSCAN as HDBSCANClass  # type: ignore[import-not-found]
    HDBSCAN_AVAILABLE = True
except ImportError:
    HDBSCANClass = None  # type: ignore[assignment]
    HDBSCAN_AVAILABLE = False
    print("⚠️  HDBSCAN not available. Install with: pip install hdbscan")

if TYPE_CHECKING:
    from hdbscan import HDBSCAN  # pragma: no cover


class PatternClusterer:
    """
    Discovers behavioral patterns using HDBSCAN clustering.

    HDBSCAN (Hierarchical Density-Based Spatial Clustering of Applications with Noise)
    is ideal for:
    1. Finding clusters of varying density
    2. Identifying noise/outliers (users who don't fit patterns)
    3. Not requiring number of clusters upfront
    4. Producing stable, hierarchical clusters

    From article: "When you discover that 18% of your traffic follows the pattern
    'research-heavy comparer'... you can build campaigns specifically for them."
    """

    def __init__(
        self,
        min_cluster_size: int = 50,
        min_samples: int = 10,
        metric: str = 'euclidean',
        cluster_selection_epsilon: float = 0.0,
        n_components_pca: int = 50
    ):
        """
        Initialize the pattern clusterer. 

        Args:
            min_cluster_size: Minimum size for a cluster to be considered valid.
                             From article: "10K-50K sessions → 3-5 stable patterns"
                             Adjust based on your data size.
            min_samples: How conservative the clustering is.
                        Higher = fewer, more stable clusters.
            metric: Distance metric ('euclidean' for behavioral embeddings)
            cluster_selection_epsilon: Allows merging of close clusters
            n_components_pca: Dimensions for PCA reduction (improves clustering speed)
        """
        if not HDBSCAN_AVAILABLE:
            raise ImportError("HDBSCAN is required. Install with: pip install hdbscan")

        self.min_cluster_size = min_cluster_size
        self.min_samples = min_samples
        self.metric = metric
        self.cluster_selection_epsilon = cluster_selection_epsilon
        self.n_components_pca = n_components_pca

        # Initialize clusterer
        cluster_cls: Type["HDBSCAN"] = cast(Type["HDBSCAN"], HDBSCANClass)
        self.clusterer = cluster_cls(
            min_cluster_size=min_cluster_size,
            min_samples=min_samples,
            metric=metric,
            cluster_selection_epsilon=cluster_selection_epsilon,
            core_dist_n_jobs=-1  # Use all CPU cores
        )

        # For dimensionality reduction (improves clustering quality)
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=n_components_pca)

        # Store results
        self.cluster_labels_ = None
        self.probabilities_ = None
        self.outlier_scores_ = None
        self.visualization_coords_ = None

    def discover_patterns(
        self,
        embeddings: np.ndarray,
        use_pca: bool = True,
        create_visualization: bool = True
    ) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        """
        Discover behavioral patterns from user embeddings.

        Args:
            embeddings: Array of shape (n_users, embedding_dim)
            use_pca: Whether to use PCA for dimensionality reduction
            create_visualization: Whether to create 2D coordinates for plotting

        Returns:
            cluster_labels: Array of shape (n_users,) with cluster assignments
                          -1 = noise/outlier, 0+ = cluster ID
            viz_coords: Array of shape (n_users, 2) for visualization (if requested)

        From article: "Step 2: Measure similarity - Which users have similar signatures?"
        """
        n_users, embed_dim = embeddings.shape
        print(f"\n🔍 Discovering behavioral patterns from {n_users} users...")
        print(f"   Embedding dimensions: {embed_dim}")

        if n_users == 0:
            raise ValueError("No embeddings provided for clustering")

        if n_users < self.min_cluster_size:
            warnings.warn(
                "Number of samples is smaller than min_cluster_size; returning single cluster",
                UserWarning
            )
            labels = np.zeros(n_users, dtype=int)
            self.cluster_labels_ = labels
            self.probabilities_ = np.ones(n_users)
            self.outlier_scores_ = np.zeros(n_users)
            self.visualization_coords_ = np.zeros((n_users, 2)) if create_visualization else None
            return labels, self.visualization_coords_

        # Step 1: Standardize features (important for distance-based clustering)
        print("   📊 Standardizing features...")
        embeddings_scaled = self.scaler.fit_transform(embeddings)

        # Step 2: Optional PCA for dimensionality reduction
        if use_pca and embed_dim > self.n_components_pca:
            print(f"   🔬 Reducing dimensions: {embed_dim} → {self.n_components_pca} (PCA)")
            embeddings_for_clustering = self.pca.fit_transform(embeddings_scaled)
            explained_variance = self.pca.explained_variance_ratio_.sum()
            print(f"   ✓ Explained variance: {explained_variance:.1%}")
        else:
            embeddings_for_clustering = embeddings_scaled

        # Step 3: Run HDBSCAN clustering
        print(f"   🎯 Running HDBSCAN clustering...")
        print(f"      min_cluster_size={self.min_cluster_size}, min_samples={self.min_samples}")

        if n_users < self.min_samples:
            effective_min_samples = max(1, n_users)
        else:
            effective_min_samples = self.min_samples

        cluster_cls: Type["HDBSCAN"] = cast(Type["HDBSCAN"], HDBSCANClass)
        self.clusterer = cluster_cls(
            min_cluster_size=min(self.min_cluster_size, n_users),
            min_samples=effective_min_samples,
            metric=self.metric,
            cluster_selection_epsilon=self.cluster_selection_epsilon,
            core_dist_n_jobs=-1
        )

        self.clusterer.fit(embeddings_for_clustering)

        # Extract results
        self.cluster_labels_ = self.clusterer.labels_
        self.probabilities_ = self.clusterer.probabilities_
        self.outlier_scores_ = self.clusterer.outlier_scores_

        # Analyze results
        unique_labels = set(self.cluster_labels_)
        n_clusters = len(unique_labels) - (1 if -1 in unique_labels else 0)
        n_noise = list(self.cluster_labels_).count(-1)

        print(f"\n   ✅ Pattern discovery complete!")
        print(f"      Found {n_clusters} behavioral patterns")
        print(f"      Noise/outliers: {n_noise} users ({n_noise/len(self.cluster_labels_)*100:.1f}%)")

        # Print cluster sizes
        if n_clusters > 0:
            print(f"\n   📊 Pattern sizes:")
            for label in sorted(unique_labels):
                if label == -1:
                    continue
                count = list(self.cluster_labels_).count(label)
                percentage = count / len(self.cluster_labels_) * 100
                print(f"      Pattern {label}: {count} users ({percentage:.1f}%)")

        # Step 4: Create visualization coordinates (2D projection)
        viz_coords = None
        if create_visualization:
            print(f"\n   🎨 Creating 2D visualization coordinates...")
            viz_coords = self._create_visualization_coords(embeddings_scaled)
            self.visualization_coords_ = viz_coords

        return self.cluster_labels_, viz_coords

    def _create_visualization_coords(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Create 2D coordinates for visualization using PCA.

        This projects high-dimensional embeddings to 2D for plotting.
        """
        pca_2d = PCA(n_components=2)
        coords_2d = pca_2d.fit_transform(embeddings)

        explained_var = pca_2d.explained_variance_ratio_.sum()
        print(f"      ✓ 2D projection (explains {explained_var:.1%} of variance)")

        return coords_2d

    def get_cluster_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about discovered clusters.

        Returns detailed information for analysis and validation.
        """
        if self.cluster_labels_ is None:
            raise ValueError("Must run discover_patterns() first")

        unique_labels = set(self.cluster_labels_)
        n_clusters = len(unique_labels) - (1 if -1 in unique_labels else 0)
        n_noise = list(self.cluster_labels_).count(-1)
        n_total = len(self.cluster_labels_)

        # Per-cluster statistics
        cluster_stats = {}
        for label in sorted(unique_labels):
            if label == -1:
                continue

            mask = self.cluster_labels_ == label
            cluster_size = mask.sum()

            # Get probabilities for this cluster
            cluster_probs = self.probabilities_[mask]

            cluster_stats[int(label)] = {
                'size': int(cluster_size),
                'percentage': float(cluster_size / n_total * 100),
                'avg_membership_probability': float(cluster_probs.mean()),
                'min_membership_probability': float(cluster_probs.min()),
                'max_membership_probability': float(cluster_probs.max()),
                'cohesion': float(cluster_probs.mean())  # Higher = more cohesive cluster
            }

        return {
            'n_clusters': n_clusters,
            'n_noise': n_noise,
            'n_total': n_total,
            'noise_percentage': float(n_noise / n_total * 100),
            'clusters': cluster_stats,
            'avg_cluster_size': float(np.mean([s['size'] for s in cluster_stats.values()])) if cluster_stats else 0,
            'largest_cluster_size': int(max([s['size'] for s in cluster_stats.values()])) if cluster_stats else 0,
            'smallest_cluster_size': int(min([s['size'] for s in cluster_stats.values()])) if cluster_stats else 0
        }

    def validate_cluster_stability(
        self,
        embeddings1: np.ndarray,
        embeddings2: np.ndarray,
        threshold: float = 0.3
    ) -> Dict[str, Any]:
        """
        Validate cluster stability across two time periods.

        From article: "Stable pattern: >70% of Month 1 users in cluster X are also
        in similar cluster in Month 2. Stable patterns become your strategic audiences."

        Args:
            embeddings1: Embeddings from period 1 (e.g., Month 1)
            embeddings2: Embeddings from period 2 (e.g., Month 2)
            threshold: Overlap threshold for considering patterns stable (default 0.3 = 30%)

        Returns:
            Stability analysis with overlap scores
        """
        # Cluster both periods independently
        labels1, _ = self.discover_patterns(embeddings1, create_visualization=False)
        labels2_obj = PatternClusterer(
            min_cluster_size=self.min_cluster_size,
            min_samples=self.min_samples,
            metric=self.metric,
            cluster_selection_epsilon=self.cluster_selection_epsilon,
            n_components_pca=self.n_components_pca
        )
        labels2, _ = labels2_obj.discover_patterns(embeddings2, create_visualization=False)

        # Calculate overlap (Jaccard similarity)
        unique_labels1 = set(labels1) - {-1}
        unique_labels2 = set(labels2) - {-1}

        overlap_scores = {}
        stable_patterns = 0

        for label1 in unique_labels1:
            mask1 = labels1 == label1
            users1 = set(np.where(mask1)[0])

            # Find most similar cluster in period 2
            max_overlap = 0.0
            best_match = None

            for label2 in unique_labels2:
                mask2 = labels2 == label2
                users2 = set(np.where(mask2)[0])

                # Jaccard similarity
                intersection = len(users1 & users2)
                union = len(users1 | users2)
                overlap = intersection / union if union > 0 else 0.0

                if overlap > max_overlap:
                    max_overlap = overlap
                    best_match = label2

            overlap_scores[int(label1)] = {
                'overlap': float(max_overlap),
                'best_match': int(best_match) if best_match is not None else None,
                'is_stable': bool(max_overlap >= threshold)
            }

            if max_overlap >= threshold:
                stable_patterns += 1

        return {
            'n_patterns_period1': len(unique_labels1),
            'n_patterns_period2': len(unique_labels2),
            'overlap_scores': overlap_scores,
            'n_stable_patterns': stable_patterns,
            'stability_rate': float(stable_patterns / len(unique_labels1)) if unique_labels1 else 0.0,
            'threshold_used': threshold
        }

    def get_cluster_members(self, cluster_id: int) -> np.ndarray:
        """
        Get indices of all users in a specific cluster.

        Args:
            cluster_id: The cluster ID

        Returns:
            Array of user indices in this cluster
        """
        if self.cluster_labels_ is None:
            raise ValueError("Must run discover_patterns() first")

        return np.where(self.cluster_labels_ == cluster_id)[0]

    def get_cluster_label(self, user_index: int) -> int:
        """
        Get cluster assignment for a specific user.

        Args:
            user_index: Index of the user

        Returns:
            Cluster ID (-1 if noise/outlier)
        """
        if self.cluster_labels_ is None:
            raise ValueError("Must run discover_patterns() first")

        return int(self.cluster_labels_[user_index])

    def __repr__(self) -> str:
        if self.cluster_labels_ is not None:
            unique_labels = set(self.cluster_labels_)
            n_clusters = len(unique_labels) - (1 if -1 in unique_labels else 0)
            return f"PatternClusterer(patterns={n_clusters}, noise={list(self.cluster_labels_).count(-1)})"
        else:
            return f"PatternClusterer(min_cluster_size={self.min_cluster_size}, not_fitted=True)"
