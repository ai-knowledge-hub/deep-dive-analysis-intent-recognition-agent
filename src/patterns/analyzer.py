"""
Pattern Analyzer - Generates persona descriptions and marketing insights from clusters.

This implements Step 4 of Pattern Discovery from the article:
"Use LLM to name and characterize each pattern. Give it the cluster statistics and ask:
What defines this group? What should we call them? How should we market to them?"

From article: "When you discover that 18% of your traffic follows the pattern 'research-heavy comparer',
you can build campaigns specifically for them, optimize bidding, predict behavior."
"""

import json
import numpy as np
from typing import List, Dict, Any, Optional
from collections import Counter

from ..intent.llm_provider import BaseLLMProvider, LLMProviderFactory


class PatternAnalyzer:
    """
    Analyzes discovered patterns and generates persona descriptions using LLM.

    This is the final step that transforms statistical clusters into actionable
    marketing personas with names, characteristics, and strategic recommendations.
    """

    def __init__(self, llm_provider: Optional[BaseLLMProvider] = None):
        """
        Initialize the pattern analyzer.

        Args:
            llm_provider: LLM provider for generating persona descriptions.
                         If None, will auto-detect from environment.
        """
        self.llm = llm_provider or LLMProviderFactory.create_from_env()
        print(f"🤖 Pattern Analyzer initialized with {type(self.llm).__name__}")

    def analyze_cluster(
        self,
        cluster_id: int,
        user_histories: List[List[Dict[str, Any]]],
        cluster_size_total: int
    ) -> Dict[str, Any]:
        """
        Analyze a single cluster and generate comprehensive persona.

        Args:
            cluster_id: The cluster ID
            user_histories: List of user histories for this cluster
            cluster_size_total: Total number of users across all clusters

        Returns:
            Dict with persona description and insights

        From article: "Step 4: Name and characterize each pattern"
        """
        print(f"\n🔬 Analyzing Pattern {cluster_id}...")
        print(f"   Users in this pattern: {len(user_histories)}")

        # Extract statistical characteristics
        stats = self._extract_cluster_statistics(user_histories)

        # Calculate cluster percentage
        percentage = (len(user_histories) / cluster_size_total * 100) if cluster_size_total > 0 else 0

        print(f"   Intent distribution: {dict(list(stats['intent_distribution'].items())[:3])}")
        print(f"   Avg journey length: {stats['avg_journey_length']:.1f} sessions")

        # Generate persona using LLM
        persona = self._generate_persona_with_llm(
            cluster_id=cluster_id,
            size=len(user_histories),
            percentage=percentage,
            statistics=stats
        )

        return {
            'cluster_id': cluster_id,
            'size': len(user_histories),
            'percentage': percentage,
            'statistics': stats,
            'persona': persona,
            'user_indices': list(range(len(user_histories)))  # Can be used to map back to original data
        }

    def _extract_cluster_statistics(
        self,
        user_histories: List[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Extract comprehensive statistics from cluster user histories.

        Returns rich behavioral data for LLM to analyze.
        """
        all_intents = []
        all_confidences = []
        all_channels = []
        all_engagement_levels = []
        journey_lengths = []
        budget_constraints = []
        time_constraints = []
        knowledge_gaps = []
        urgency_levels = []
        expertise_levels = []

        for history in user_histories:
            journey_lengths.append(len(history))

            for record in history:
                all_intents.append(record.get('intent', 'unknown'))
                all_confidences.append(record.get('confidence', 0.5))
                all_channels.append(record.get('channel', 'unknown'))
                all_engagement_levels.append(record.get('engagement_level', 'medium'))
                budget_constraints.append(record.get('has_budget_constraint', False))
                time_constraints.append(record.get('has_time_constraint', False))
                knowledge_gaps.append(record.get('has_knowledge_gap', False))
                urgency_levels.append(record.get('urgency_level', 'medium'))
                expertise_levels.append(record.get('expertise_level', 'intermediate'))

        # Calculate distributions
        intent_dist = Counter(all_intents)
        total_intents = sum(intent_dist.values())
        intent_percentages = {k: (v / total_intents * 100) for k, v in intent_dist.most_common(10)}

        channel_dist = Counter(all_channels)
        total_channels = sum(channel_dist.values())
        channel_percentages = {k: (v / total_channels * 100) for k, v in channel_dist.items()}

        engagement_dist = Counter(all_engagement_levels)
        total_engagement = sum(engagement_dist.values())
        engagement_percentages = {k: (v / total_engagement * 100) for k, v in engagement_dist.items()}

        # Intent stage analysis (from article: awareness → consideration → decision)
        research_intents = ['browsing_inspiration', 'category_research']
        comparison_intents = ['compare_options', 'price_discovery', 'evaluate_fit']
        decision_intents = ['ready_to_purchase', 'deal_seeking', 'gift_shopping']

        research_count = sum(1 for i in all_intents if any(r in i for r in research_intents))
        comparison_count = sum(1 for i in all_intents if any(c in i for c in comparison_intents))
        decision_count = sum(1 for i in all_intents if any(d in i for d in decision_intents))

        total_stage_intents = research_count + comparison_count + decision_count
        if total_stage_intents > 0:
            stage_distribution = {
                'awareness': research_count / total_stage_intents * 100,
                'consideration': comparison_count / total_stage_intents * 100,
                'decision': decision_count / total_stage_intents * 100
            }
        else:
            stage_distribution = {'awareness': 33.3, 'consideration': 33.3, 'decision': 33.3}

        return {
            'intent_distribution': intent_percentages,
            'channel_distribution': channel_percentages,
            'engagement_distribution': engagement_percentages,
            'stage_distribution': stage_distribution,
            'avg_confidence': float(np.mean(all_confidences)) if all_confidences else 0.5,
            'avg_journey_length': float(np.mean(journey_lengths)) if journey_lengths else 0,
            'min_journey_length': int(np.min(journey_lengths)) if journey_lengths else 0,
            'max_journey_length': int(np.max(journey_lengths)) if journey_lengths else 0,
            'budget_conscious_ratio': sum(budget_constraints) / len(budget_constraints) if budget_constraints else 0,
            'time_sensitive_ratio': sum(time_constraints) / len(time_constraints) if time_constraints else 0,
            'knowledge_gap_ratio': sum(knowledge_gaps) / len(knowledge_gaps) if knowledge_gaps else 0,
            'urgency_distribution': Counter(urgency_levels),
            'expertise_distribution': Counter(expertise_levels),
            'total_sessions': len(all_intents)
        }

    def _generate_persona_with_llm(
        self,
        cluster_id: int,
        size: int,
        percentage: float,
        statistics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use LLM to generate human-readable persona description.

        From article: "Give it the cluster statistics and ask: What defines this group?
        What should we call them? How should we market to them?"
        """
        # Build the prompt
        prompt = self._build_persona_prompt(cluster_id, size, percentage, statistics)

        try:
            print(f"   🤖 Generating persona with LLM...")

            # Call LLM
            response = self.llm.generate_sync(
                prompt=prompt,
                system_prompt="You are an expert marketing strategist specializing in behavioral audience segmentation."
            )

            # Parse response
            persona = self._parse_persona_response(response)

            print(f"   ✅ Persona generated: \"{persona.get('persona_name', 'Unknown')}\"")

            return persona

        except Exception as e:
            print(f"   ⚠️  LLM generation failed: {e}")
            return self._create_fallback_persona(cluster_id, size, percentage, statistics)

    def _build_persona_prompt(
        self,
        cluster_id: int,
        size: int,
        percentage: float,
        stats: Dict[str, Any]
    ) -> str:
        """
        Build the prompt for LLM persona generation.

        This follows the template from Appendix B of the article.
        """
        # Format intent distribution nicely
        top_intents = list(stats['intent_distribution'].items())[:5]
        intent_str = "\n".join([f"    - {intent}: {pct:.1f}%" for intent, pct in top_intents])

        # Format channel distribution
        channel_str = "\n".join([f"    - {ch}: {pct:.1f}%" for ch, pct in stats['channel_distribution'].items()])

        # Format stage distribution
        stage_str = "\n".join([f"    - {stage.title()}: {pct:.1f}%" for stage, pct in stats['stage_distribution'].items()])

        prompt = f"""You are an expert marketing strategist creating audience personas from behavioral data.

# CLUSTER STATISTICS

**Cluster ID**: {cluster_id}
**Size**: {size} users ({percentage:.1f}% of total)

**Intent Distribution** (top intents):
{intent_str}

**Journey Funnel Stage Distribution**:
{stage_str}

**Channel Behavior**:
{channel_str}

**Engagement Patterns**:
  - High/Very High Engagement: {stats['engagement_distribution'].get('high', 0) + stats['engagement_distribution'].get('very_high', 0):.1f}%
  - Medium Engagement: {stats['engagement_distribution'].get('medium', 0):.1f}%
  - Low Engagement: {stats['engagement_distribution'].get('low', 0):.1f}%

**Journey Characteristics**:
  - Average journey length: {stats['avg_journey_length']:.1f} sessions
  - Journey range: {stats['min_journey_length']}-{stats['max_journey_length']} sessions
  - Average intent confidence: {stats['avg_confidence']:.2f}

**Constraint Signals**:
  - Budget conscious: {stats['budget_conscious_ratio']:.1%}
  - Time sensitive: {stats['time_sensitive_ratio']:.1%}
  - Knowledge gaps: {stats['knowledge_gap_ratio']:.1%}

# TASK

Create a comprehensive marketing persona in JSON format with the following structure:

{{
  "persona_name": "Memorable, descriptive name (e.g., 'Research-Driven Comparers', 'Fast Impulse Buyers')",
  "description": "2-3 sentence behavioral description of this audience",
  "key_characteristics": [
    "Characteristic 1",
    "Characteristic 2",
    "Characteristic 3"
  ],
  "motivations": [
    "Primary motivation 1",
    "Primary motivation 2",
    "Primary motivation 3"
  ],
  "pain_points": [
    "Pain point or concern 1",
    "Pain point or concern 2"
  ],
  "marketing_insights": [
    "Actionable insight 1",
    "Actionable insight 2",
    "Actionable insight 3"
  ],
  "recommended_strategies": [
    "Campaign strategy 1",
    "Campaign strategy 2",
    "Campaign strategy 3"
  ],
  "content_preferences": [
    "Content type they engage with",
    "Messaging style that resonates",
    "Channel preferences"
  ],
  "conversion_approach": "How to convert this audience (1-2 sentences)",
  "estimated_ltv_multiplier": 1.0,
  "recommended_bid_modifier": 0.0
}}

# GUIDELINES

1. The persona name should be memorable and capture the essence of the behavior
2. Base all insights on the actual behavioral data provided
3. Be specific and actionable - avoid generic marketing advice
4. Consider the full customer journey (awareness → consideration → decision)
5. LTV multiplier: 1.0 = average, >1.0 = higher value, <1.0 = lower value
6. Bid modifier: -0.5 to +1.0 range (-50% to +100% bid adjustment)
7. Make it useful for a marketing team to immediately act on

Generate the persona now (JSON only, no markdown formatting):"""

        return prompt

    def _parse_persona_response(self, response: str) -> Dict[str, Any]:
        """
        Parse LLM response into structured persona.

        Handles both clean JSON and markdown-wrapped JSON.
        """
        # Try to extract JSON from response
        response_clean = response.strip()

        # Remove markdown code blocks if present
        if response_clean.startswith('```'):
            # Find the content between ``` markers
            lines = response_clean.split('\n')
            json_lines = []
            in_code_block = False

            for line in lines:
                if line.strip().startswith('```'):
                    in_code_block = not in_code_block
                    continue
                if in_code_block or (line.strip().startswith('{') or line.strip().startswith('"')):
                    json_lines.append(line)

            response_clean = '\n'.join(json_lines)

        # Find JSON object
        start_idx = response_clean.find('{')
        end_idx = response_clean.rfind('}') + 1

        if start_idx != -1 and end_idx > start_idx:
            json_str = response_clean[start_idx:end_idx]

            try:
                persona = json.loads(json_str)
                return self._validate_persona(persona)
            except json.JSONDecodeError as e:
                print(f"   ⚠️  JSON parsing error: {e}")
                # Try to fix common issues
                try:
                    # Remove trailing commas
                    json_str_fixed = json_str.replace(',}', '}').replace(',]', ']')
                    persona = json.loads(json_str_fixed)
                    return self._validate_persona(persona)
                except:
                    pass

        # If we get here, parsing failed
        print("   ⚠️  Could not parse persona JSON, using fallback")
        return None

    def _validate_persona(self, persona: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure persona has all required fields."""
        required_fields = {
            'persona_name': 'Unknown Persona',
            'description': 'No description available',
            'key_characteristics': [],
            'motivations': [],
            'pain_points': [],
            'marketing_insights': [],
            'recommended_strategies': [],
            'content_preferences': [],
            'conversion_approach': 'No conversion approach specified',
            'estimated_ltv_multiplier': 1.0,
            'recommended_bid_modifier': 0.0
        }

        for field, default in required_fields.items():
            if field not in persona:
                persona[field] = default

        # Validate numeric fields
        try:
            persona['estimated_ltv_multiplier'] = float(persona['estimated_ltv_multiplier'])
        except:
            persona['estimated_ltv_multiplier'] = 1.0

        try:
            persona['recommended_bid_modifier'] = float(persona['recommended_bid_modifier'])
        except:
            persona['recommended_bid_modifier'] = 0.0

        return persona

    def _create_fallback_persona(
        self,
        cluster_id: int,
        size: int,
        percentage: float,
        stats: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a basic persona when LLM fails."""
        top_intent = list(stats['intent_distribution'].keys())[0] if stats['intent_distribution'] else 'unknown'

        return {
            'persona_name': f'Pattern {cluster_id} Users',
            'description': f'This group represents {percentage:.1f}% of users with primary intent: {top_intent}',
            'key_characteristics': [
                f'Average journey: {stats["avg_journey_length"]:.1f} sessions',
                f'Top intent: {top_intent}',
                f'Confidence: {stats["avg_confidence"]:.0%}'
            ],
            'motivations': ['Analysis required'],
            'pain_points': ['Analysis required'],
            'marketing_insights': [
                f'Represents {size} users',
                f'Primary behavior: {top_intent}',
                'Detailed analysis unavailable'
            ],
            'recommended_strategies': ['Manual analysis recommended'],
            'content_preferences': ['Unknown'],
            'conversion_approach': 'Requires further analysis',
            'estimated_ltv_multiplier': 1.0,
            'recommended_bid_modifier': 0.0
        }

    def analyze_all_clusters(
        self,
        cluster_labels: np.ndarray,
        user_histories: List[List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """
        Analyze all discovered clusters and generate personas.

        Args:
            cluster_labels: Array of cluster assignments from PatternClusterer
            user_histories: Original user histories

        Returns:
            List of persona dictionaries
        """
        unique_labels = set(cluster_labels)
        unique_labels.discard(-1)  # Remove noise label

        personas = []
        total_users = len([l for l in cluster_labels if l != -1])  # Exclude noise from total

        print(f"\n📊 Analyzing {len(unique_labels)} discovered patterns...")

        for label in sorted(unique_labels):
            # Get user histories for this cluster
            cluster_mask = cluster_labels == label
            cluster_histories = [user_histories[i] for i, mask in enumerate(cluster_mask) if mask]

            # Analyze cluster
            persona = self.analyze_cluster(
                cluster_id=int(label),
                user_histories=cluster_histories,
                cluster_size_total=total_users
            )

            personas.append(persona)

        print(f"\n✅ Generated {len(personas)} audience personas")

        return personas

    def export_personas_for_activation(
        self,
        personas: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Export personas in format ready for marketing activation.

        Returns data structured for:
        - Ad platform audience uploads
        - Campaign briefs
        - Marketing team handoff
        """
        export = {
            'summary': {
                'total_patterns': len(personas),
                'total_users': sum(p['size'] for p in personas),
                'generation_timestamp': '2025-01-01T00:00:00'  # Would be actual timestamp
            },
            'personas': []
        }

        for persona in personas:
            export['personas'].append({
                'id': persona['cluster_id'],
                'name': persona['persona']['persona_name'],
                'size': persona['size'],
                'percentage': persona['percentage'],
                'description': persona['persona']['description'],
                'recommended_bid_modifier': persona['persona']['recommended_bid_modifier'],
                'estimated_ltv_multiplier': persona['persona']['estimated_ltv_multiplier'],
                'top_intents': list(persona['statistics']['intent_distribution'].keys())[:3],
                'marketing_strategies': persona['persona']['recommended_strategies'],
                'content_preferences': persona['persona']['content_preferences']
            })

        return export

    def __repr__(self) -> str:
        return f"PatternAnalyzer(llm={type(self.llm).__name__})"
