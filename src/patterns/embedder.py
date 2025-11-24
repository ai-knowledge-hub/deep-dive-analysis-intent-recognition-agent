"""
Behavioral Embedder - Creates vector representations of user behavioral patterns.

This implements Step 1 of Pattern Discovery from the article:
"Transform intent sequences into vector representations that capture behavioral similarity."

From article: "Represent each user as a behavioral signature:
- Intent sequence: [research → compare → evaluate_fit → ready_to_purchase]
- Constraint profile: [budget_conscious, time_sensitive, knowledge_moderate]
- Channel behavior: [starts_organic, returns_via_email, converts_on_paid]
- Temporal pattern: [weekend_browser, evening_converter]
- Outcome: [converted, AOV, LTV]"
"""

import numpy as np
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from datetime import datetime


class BehavioralEmbedder:
    """
    Creates behavioral embeddings from user intent histories.

    Combines:
    1. Semantic embeddings of intent sequences (using sentence-transformers)
    2. Behavioral feature vectors (session patterns, engagement)
    3. Temporal feature vectors (time patterns, recency)
    4. Constraint feature vectors (budget, urgency, knowledge)
    """

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the behavioral embedder.

        Args:
            model_name: Sentence transformer model to use.
                       'all-MiniLM-L6-v2' is fast and good for hackathon (384 dimensions)
                       For production, consider 'all-mpnet-base-v2' (768 dimensions)
        """
        print(f"🔧 Loading sentence transformer model: {model_name}")
        self.text_encoder = SentenceTransformer(model_name)
        self.embedding_dim = self.text_encoder.get_sentence_embedding_dimension()
        print(f"✅ Model loaded. Embedding dimension: {self.embedding_dim}")

    def create_embedding(self, user_history: List[Dict[str, Any]]) -> np.ndarray:
        """
        Create a comprehensive behavioral embedding for a user.

        Args:
            user_history: List of intent records for a user, e.g.:
                [
                    {
                        "intent": "research_category",
                        "confidence": 0.85,
                        "timestamp": "2025-01-15T10:00:00",
                        "channel": "organic",
                        "has_budget_constraint": False,
                        "has_time_constraint": False,
                        "engagement_level": "high"
                    },
                    ...
                ]

        Returns:
            numpy array: Combined embedding vector
        """
        if not user_history or len(user_history) == 0:
            # Return zero vector for empty history
            total_dim = self.embedding_dim + 15 + 5 + 5  # text + behavioral + temporal + constraint
            return np.zeros(total_dim)

        # 1. Intent Sequence Embedding (semantic)
        intent_embedding = self._create_intent_sequence_embedding(user_history)

        # 2. Behavioral Features (statistical)
        behavioral_features = self._extract_behavioral_features(user_history)

        # 3. Temporal Features (time patterns)
        temporal_features = self._extract_temporal_features(user_history)

        # 4. Constraint Features (user limitations)
        constraint_features = self._extract_constraint_features(user_history)

        # Concatenate all features into single embedding
        full_embedding = np.concatenate([
            intent_embedding,
            behavioral_features,
            temporal_features,
            constraint_features
        ])

        return full_embedding

    def _create_intent_sequence_embedding(self, history: List[Dict[str, Any]]) -> np.ndarray:
        """
        Create semantic embedding of intent sequence.

        From article: "Intent sequence: [research → compare → evaluate_fit → ready_to_purchase]"

        This captures the narrative arc of user behavior.
        """
        # Extract intent labels in chronological order
        intent_sequence = [record.get('intent', 'unknown') for record in history]

        # Create a narrative string (LLMs understand sequences in text form)
        intent_narrative = " -> ".join(intent_sequence)

        # Add context about the journey
        journey_description = f"User journey: {intent_narrative}. Total steps: {len(intent_sequence)}."

        # Encode using sentence transformer
        embedding = self.text_encoder.encode(journey_description, convert_to_numpy=True)

        return embedding

    def _extract_behavioral_features(self, history: List[Dict[str, Any]]) -> np.ndarray:
        """
        Extract statistical behavioral features.

        From article: "Behavioral signature" includes session patterns,
        engagement depth, comparison behavior, etc.
        """
        # Session characteristics
        session_count = len(history)
        avg_confidence = np.mean([r.get('confidence', 0.5) for r in history])

        # Intent diversity (how many unique intents)
        unique_intents = len(set(r.get('intent', 'unknown') for r in history))
        intent_diversity = unique_intents / max(session_count, 1)

        # Stage progression (from article: awareness → consideration → decision)
        research_count = sum(1 for r in history if 'research' in r.get('intent', '').lower() or 'browsing' in r.get('intent', '').lower())
        compare_count = sum(1 for r in history if 'compare' in r.get('intent', '').lower() or 'evaluate' in r.get('intent', '').lower())
        decision_count = sum(1 for r in history if 'ready' in r.get('intent', '').lower() or 'purchase' in r.get('intent', '').lower())

        # Normalize by session count
        research_ratio = research_count / session_count
        compare_ratio = compare_count / session_count
        decision_ratio = decision_count / session_count

        # Engagement patterns
        engagement_levels = [r.get('engagement_level', 'medium') for r in history]
        high_engagement_ratio = sum(1 for e in engagement_levels if e == 'high' or e == 'very_high') / session_count

        # Channel behavior (from article: "starts_organic, returns_via_email")
        channels = [r.get('channel', 'direct') for r in history]
        unique_channels = len(set(channels))
        channel_diversity = unique_channels / max(session_count, 1)

        # Deal-seeking behavior
        deal_seeking_count = sum(1 for r in history if 'deal' in r.get('intent', '').lower() or 'price' in r.get('intent', '').lower())
        deal_seeking_ratio = deal_seeking_count / session_count

        # Gift shopping signals
        gift_shopping_count = sum(1 for r in history if 'gift' in r.get('intent', '').lower())
        gift_shopping_ratio = gift_shopping_count / session_count

        # Journey completion (did they reach decision stage?)
        reached_decision = 1.0 if decision_count > 0 else 0.0

        # Repeat behavior
        repeat_intents = session_count - unique_intents
        repeat_ratio = repeat_intents / max(session_count, 1)

        return np.array([
            session_count,
            avg_confidence,
            intent_diversity,
            research_ratio,
            compare_ratio,
            decision_ratio,
            high_engagement_ratio,
            channel_diversity,
            deal_seeking_ratio,
            gift_shopping_ratio,
            reached_decision,
            repeat_ratio,
            unique_intents,
            research_count,
            compare_count
        ], dtype=np.float32)

    def _extract_temporal_features(self, history: List[Dict[str, Any]]) -> np.ndarray:
        """
        Extract temporal behavioral patterns.

        From article: "Temporal pattern: [weekend_browser, evening_converter]"
        """
        # Parse timestamps
        timestamps = []
        for record in history:
            ts_str = record.get('timestamp', '')
            if ts_str:
                try:
                    timestamps.append(datetime.fromisoformat(ts_str.replace('Z', '+00:00')))
                except:
                    pass

        if not timestamps:
            # No temporal data available
            return np.zeros(5, dtype=np.float32)

        # Time span (how long is the journey?)
        time_span_days = (max(timestamps) - min(timestamps)).total_seconds() / (24 * 3600)

        # Recency (how recent is last action?)
        now = datetime.now()
        if timestamps[-1].tzinfo:
            now = now.astimezone(timestamps[-1].tzinfo)
        days_since_last = (now - timestamps[-1]).total_seconds() / (24 * 3600)

        # Time of day patterns
        hours = [ts.hour for ts in timestamps]
        weekend_sessions = sum(1 for ts in timestamps if ts.weekday() >= 5)
        weekend_ratio = weekend_sessions / len(timestamps)

        # Session frequency
        session_frequency = len(timestamps) / max(time_span_days, 1)  # sessions per day

        return np.array([
            time_span_days,
            days_since_last,
            weekend_ratio,
            session_frequency,
            len(timestamps)
        ], dtype=np.float32)

    def _extract_constraint_features(self, history: List[Dict[str, Any]]) -> np.ndarray:
        """
        Extract constraint signals.

        From article: "Constraint profile: [budget_conscious, time_sensitive, knowledge_moderate]"
        """
        # Budget constraints
        has_budget_constraint = sum(1 for r in history if r.get('has_budget_constraint', False))
        budget_constraint_ratio = has_budget_constraint / len(history)

        # Time constraints
        has_time_constraint = sum(1 for r in history if r.get('has_time_constraint', False))
        time_constraint_ratio = has_time_constraint / len(history)

        # Knowledge level (inferred from behavior)
        # Users with knowledge gaps engage more with educational content
        has_knowledge_gap = sum(1 for r in history if r.get('has_knowledge_gap', False))
        knowledge_gap_ratio = has_knowledge_gap / len(history)

        # Urgency signals (high time pressure)
        urgency_level = np.mean([
            1.0 if r.get('urgency_level', 'low') == 'high' else
            0.5 if r.get('urgency_level', 'low') == 'medium' else
            0.0
            for r in history
        ])

        # Expertise level
        expertise_scores = []
        for r in history:
            expertise = r.get('expertise_level', 'intermediate')
            if expertise == 'expert':
                expertise_scores.append(1.0)
            elif expertise == 'intermediate':
                expertise_scores.append(0.5)
            else:  # novice
                expertise_scores.append(0.0)
        avg_expertise = np.mean(expertise_scores) if expertise_scores else 0.5

        return np.array([
            budget_constraint_ratio,
            time_constraint_ratio,
            knowledge_gap_ratio,
            urgency_level,
            avg_expertise
        ], dtype=np.float32)

    def get_embedding_dimension(self) -> int:
        """Get the total dimension of the combined embedding."""
        # text_embedding + behavioral (15) + temporal (5) + constraint (5)
        return self.embedding_dim + 15 + 5 + 5

    def create_batch_embeddings(self, user_histories: List[List[Dict[str, Any]]]) -> np.ndarray:
        """
        Create embeddings for multiple users efficiently.

        Args:
            user_histories: List of user histories

        Returns:
            numpy array of shape (n_users, embedding_dim)
        """
        embeddings = []
        total = len(user_histories)

        print(f"🔄 Creating embeddings for {total} users...")

        for i, history in enumerate(user_histories):
            if i % 100 == 0 and i > 0:
                print(f"   Progress: {i}/{total} ({i/total*100:.1f}%)")

            embedding = self.create_embedding(history)
            embeddings.append(embedding)

        print(f"✅ Created {len(embeddings)} embeddings")

        return np.array(embeddings)

    def __repr__(self) -> str:
        return f"BehavioralEmbedder(model={self.text_encoder}, dim={self.get_embedding_dimension()})"
