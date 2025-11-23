"""
Context Builder - Transforms raw behavioral data into structured context for intent recognition.

This module implements the Context Capture layer from the article, creating rich,
structured context that activates the right latent representations in the LLM.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json


class ContextBuilder:
    """Builds structured context from raw behavioral signals."""

    def __init__(self):
        """Initialize the context builder."""
        self.context_schema_version = "1.0"

    def build_context(
        self,
        user_query: str = "",
        page_type: str = "",
        previous_actions: str = "",
        time_on_page: int = 0,
        session_history: str = "",
        device_type: str = "desktop",
        traffic_source: str = "direct",
        timestamp: Optional[datetime] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Build structured context from behavioral signals.

        Args:
            user_query: Search query or text input
            page_type: Type of page (product_detail, category, etc.)
            previous_actions: Comma-separated list of actions
            time_on_page: Seconds spent on current page
            session_history: JSON string of past session data
            device_type: Device being used
            traffic_source: How user arrived
            timestamp: When this happened (defaults to now)
            **kwargs: Additional context signals

        Returns:
            Structured context dictionary
        """
        timestamp = timestamp or datetime.now()

        # Parse previous actions
        actions_list = [a.strip() for a in previous_actions.split(",")] if previous_actions else []

        # Parse session history
        history_data = self._parse_session_history(session_history)

        # Build the five dimensions of context from the article
        context = {
            "schema_version": self.context_schema_version,
            "timestamp": timestamp.isoformat(),

            # 1. IDENTITY CONTEXT: Who are they?
            "identity_context": self._build_identity_context(
                device_type=device_type,
                history_data=history_data,
                **kwargs
            ),

            # 2. HISTORICAL CONTEXT: What have they done?
            "historical_context": self._build_historical_context(
                history_data=history_data,
                previous_actions=actions_list,
                **kwargs
            ),

            # 3. SITUATIONAL CONTEXT: Where are they right now?
            "situational_context": self._build_situational_context(
                page_type=page_type,
                device_type=device_type,
                traffic_source=traffic_source,
                timestamp=timestamp,
                **kwargs
            ),

            # 4. BEHAVIORAL SIGNALS: What are they doing?
            "behavioral_signals": self._build_behavioral_signals(
                user_query=user_query,
                actions_list=actions_list,
                time_on_page=time_on_page,
                **kwargs
            ),

            # 5. TEMPORAL SIGNALS: When are they acting?
            "temporal_signals": self._build_temporal_signals(
                timestamp=timestamp,
                history_data=history_data,
                **kwargs
            ),

            # 6. CONSTRAINT SIGNALS: What limits their choices?
            "constraint_signals": self._extract_constraint_signals(
                user_query=user_query,
                actions_list=actions_list,
                **kwargs
            )
        }

        return context

    def _parse_session_history(self, session_history: str) -> List[Dict]:
        """Parse session history JSON string."""
        if not session_history or session_history.strip() == "":
            return []

        try:
            history = json.loads(session_history)
            if isinstance(history, list):
                return history
            elif isinstance(history, dict):
                return [history]
            else:
                return []
        except json.JSONDecodeError:
            return []

    def _build_identity_context(
        self,
        device_type: str,
        history_data: List[Dict],
        **kwargs
    ) -> Dict[str, Any]:
        """Build identity context - who is this person?"""

        # Infer role based on behavior patterns
        role = self._infer_role(history_data, **kwargs)

        return {
            "device_type": device_type,
            "inferred_role": role,
            "is_returning_user": len(history_data) > 0,
            "session_count": len(history_data) + 1,
            "user_segment": kwargs.get("user_segment", "unknown")
        }

    def _infer_role(self, history_data: List[Dict], **kwargs) -> str:
        """Infer what role the user is playing."""
        # Simple heuristics - can be enhanced with ML

        if any("gift" in str(h).lower() for h in history_data):
            return "gift_giver"

        if any("bulk" in str(h).lower() or "corporate" in str(h).lower() for h in history_data):
            return "professional_buyer"

        if len(history_data) > 5:
            return "enthusiast_researcher"

        return "general_consumer"

    def _build_historical_context(
        self,
        history_data: List[Dict],
        previous_actions: List[str],
        **kwargs
    ) -> Dict[str, Any]:
        """Build historical context - what have they done?"""

        # Extract past intents if available
        past_intents = [h.get("intent") for h in history_data if h.get("intent")]

        # Extract past searches
        past_searches = []
        for item in history_data:
            if item.get("query"):
                past_searches.append(item["query"])

        return {
            "previous_session_count": len(history_data),
            "past_intents": past_intents,
            "past_searches": past_searches,
            "current_session_actions": previous_actions,
            "action_count": len(previous_actions),
            "has_abandoned_cart": "abandoned_cart" in previous_actions or any(
                "cart" in str(h).lower() for h in history_data
            ),
            "has_made_purchase": "purchased" in previous_actions or any(
                "purchase" in str(h).lower() for h in history_data
            )
        }

    def _build_situational_context(
        self,
        page_type: str,
        device_type: str,
        traffic_source: str,
        timestamp: datetime,
        **kwargs
    ) -> Dict[str, Any]:
        """Build situational context - where are they right now?"""

        return {
            "page_type": page_type,
            "device_type": device_type,
            "traffic_source": traffic_source,
            "channel": self._classify_channel(traffic_source),
            "location_context": kwargs.get("location", "unknown"),
            "is_mobile": device_type.lower() in ["mobile", "smartphone", "tablet"]
        }

    def _classify_channel(self, traffic_source: str) -> str:
        """Classify traffic source into channel."""
        source_lower = traffic_source.lower()

        if "google" in source_lower or "bing" in source_lower:
            return "search"
        elif "facebook" in source_lower or "instagram" in source_lower or "social" in source_lower:
            return "social"
        elif "email" in source_lower:
            return "email"
        elif "direct" in source_lower:
            return "direct"
        else:
            return "other"

    def _build_behavioral_signals(
        self,
        user_query: str,
        actions_list: List[str],
        time_on_page: int,
        **kwargs
    ) -> Dict[str, Any]:
        """Build behavioral signals - what are they doing?"""

        # Analyze the query for intent signals
        query_signals = self._analyze_query(user_query)

        # Analyze actions for patterns
        action_patterns = self._analyze_actions(actions_list)

        return {
            "current_query": user_query,
            "query_intent_signals": query_signals,
            "time_on_page_seconds": time_on_page,
            "engagement_level": self._classify_engagement(time_on_page, actions_list),
            "actions_taken": actions_list,
            "action_patterns": action_patterns,
            "scroll_depth": kwargs.get("scroll_depth", 0),
            "clicks_count": len([a for a in actions_list if "click" in a.lower()])
        }

    def _analyze_query(self, query: str) -> Dict[str, bool]:
        """Extract signals from search query."""
        query_lower = query.lower()

        return {
            "has_brand_name": any(brand in query_lower for brand in ["nike", "adidas", "apple", "samsung"]),
            "has_comparison_words": any(word in query_lower for word in ["vs", "versus", "compare", "better", "best"]),
            "has_price_signals": any(word in query_lower for word in ["cheap", "affordable", "expensive", "price", "cost"]),
            "has_urgency_signals": any(word in query_lower for word in ["now", "today", "urgent", "asap", "fast"]),
            "has_quality_signals": any(word in query_lower for word in ["best", "top", "review", "rating"]),
            "is_specific": len(query.split()) > 3,
            "is_question": "?" in query or query_lower.startswith(("how", "what", "where", "when", "why"))
        }

    def _analyze_actions(self, actions: List[str]) -> Dict[str, Any]:
        """Analyze action patterns."""
        actions_lower = [a.lower() for a in actions]

        return {
            "viewed_reviews": any("review" in a for a in actions_lower),
            "compared_products": any("compar" in a for a in actions_lower),
            "added_to_cart": any("cart" in a for a in actions_lower),
            "used_filters": any("filter" in a for a in actions_lower),
            "zoomed_images": any("zoom" in a for a in actions_lower),
            "read_details": any("detail" in a or "spec" in a for a in actions_lower),
            "checked_shipping": any("ship" in a for a in actions_lower)
        }

    def _classify_engagement(self, time_on_page: int, actions: List[str]) -> str:
        """Classify engagement level."""
        if time_on_page > 180 and len(actions) > 5:
            return "very_high"
        elif time_on_page > 120 and len(actions) > 3:
            return "high"
        elif time_on_page > 60 and len(actions) > 1:
            return "medium"
        elif time_on_page > 30 or len(actions) > 0:
            return "low"
        else:
            return "very_low"

    def _build_temporal_signals(
        self,
        timestamp: datetime,
        history_data: List[Dict],
        **kwargs
    ) -> Dict[str, Any]:
        """Build temporal signals - when are they acting?"""

        hour = timestamp.hour
        day_of_week = timestamp.weekday()  # 0 = Monday, 6 = Sunday

        # Calculate days since last visit
        days_since_last_visit = None
        if history_data:
            # Simplified - in production, parse timestamps
            days_since_last_visit = kwargs.get("days_since_last_visit", 1)

        return {
            "timestamp": timestamp.isoformat(),
            "hour_of_day": hour,
            "day_of_week": day_of_week,
            "is_weekend": day_of_week >= 5,
            "is_business_hours": 9 <= hour <= 17 and day_of_week < 5,
            "is_evening": 18 <= hour <= 23,
            "days_since_last_visit": days_since_last_visit,
            "is_new_user": len(history_data) == 0,
            "session_number": len(history_data) + 1
        }

    def _extract_constraint_signals(
        self,
        user_query: str,
        actions_list: List[str],
        **kwargs
    ) -> Dict[str, Any]:
        """Extract constraint signals - what limits their choices?"""

        query_lower = user_query.lower()
        actions_lower = [a.lower() for a in actions_list]

        # Budget constraints
        has_budget_constraint = any(word in query_lower for word in [
            "cheap", "affordable", "budget", "under", "less than", "discount", "sale"
        ]) or any("price" in a and "filter" in a for a in actions_lower)

        # Urgency constraints
        has_time_constraint = any(word in query_lower for word in [
            "today", "now", "urgent", "asap", "fast", "quick", "express", "next day"
        ]) or any("express" in a or "fast" in a for a in actions_lower)

        # Knowledge constraints
        has_knowledge_gap = any(word in query_lower for word in [
            "how to", "what is", "beginner", "guide", "help", "learn", "tutorial"
        ]) or any("guide" in a or "tutorial" in a for a in actions_lower)

        return {
            "has_budget_constraint": has_budget_constraint,
            "has_time_constraint": has_time_constraint,
            "has_knowledge_gap": has_knowledge_gap,
            "budget_level": self._infer_budget_level(query_lower, actions_lower),
            "urgency_level": self._infer_urgency_level(query_lower, actions_lower),
            "expertise_level": self._infer_expertise_level(query_lower, actions_lower)
        }

    def _infer_budget_level(self, query: str, actions: List[str]) -> str:
        """Infer budget level from signals."""
        if any(word in query for word in ["luxury", "premium", "high-end"]):
            return "high"
        elif any(word in query for word in ["cheap", "budget", "affordable"]):
            return "low"
        else:
            return "medium"

    def _infer_urgency_level(self, query: str, actions: List[str]) -> str:
        """Infer urgency level from signals."""
        if any(word in query for word in ["now", "today", "urgent", "asap"]):
            return "high"
        elif any(word in query for word in ["soon", "fast", "quick"]):
            return "medium"
        else:
            return "low"

    def _infer_expertise_level(self, query: str, actions: List[str]) -> str:
        """Infer expertise level from signals."""
        if any(word in query for word in ["beginner", "how to", "what is", "guide"]):
            return "novice"
        elif any(word in query for word in ["advanced", "professional", "expert"]):
            return "expert"
        else:
            return "intermediate"

    def format_for_llm(self, context: Dict[str, Any]) -> str:
        """Format context for LLM prompt."""

        # Create a narrative summary that activates latent representations
        identity = context["identity_context"]
        history = context["historical_context"]
        situation = context["situational_context"]
        behavioral = context["behavioral_signals"]
        temporal = context["temporal_signals"]
        constraints = context["constraint_signals"]

        formatted = f"""
IDENTITY:
- Device: {identity['device_type']}
- Role: {identity['inferred_role']}
- User Type: {"Returning user" if identity['is_returning_user'] else "New user"}
- Session Count: {identity['session_count']}

HISTORY:
- Previous Sessions: {history['previous_session_count']}
- Past Intents: {', '.join(history['past_intents']) if history['past_intents'] else 'None recorded'}
- Past Searches: {', '.join(history['past_searches'][:3]) if history['past_searches'] else 'None'}
- Current Session Actions: {', '.join(history['current_session_actions']) if history['current_session_actions'] else 'Just arrived'}
- Cart Status: {"Has abandoned cart" if history['has_abandoned_cart'] else "No cart activity"}

CURRENT SITUATION:
- Page Type: {situation['page_type']}
- Traffic Source: {situation['traffic_source']} ({situation['channel']})
- Device: {"Mobile" if situation['is_mobile'] else "Desktop/Laptop"}

BEHAVIORAL SIGNALS:
- Current Query: "{behavioral['current_query']}"
- Time on Page: {behavioral['time_on_page_seconds']} seconds
- Engagement Level: {behavioral['engagement_level']}
- Actions: {', '.join(behavioral['actions_taken']) if behavioral['actions_taken'] else 'None yet'}
- Query Signals: {self._format_signals(behavioral['query_intent_signals'])}
- Action Patterns: {self._format_signals(behavioral['action_patterns'])}

TEMPORAL SIGNALS:
- Time: {temporal['hour_of_day']}:00 on {"weekend" if temporal['is_weekend'] else "weekday"}
- Context: {"Business hours" if temporal['is_business_hours'] else "Evening" if temporal['is_evening'] else "Off hours"}
- Recency: {"New user" if temporal['is_new_user'] else f"{temporal['days_since_last_visit']} days since last visit" if temporal['days_since_last_visit'] else "Unknown"}

CONSTRAINTS:
- Budget: {constraints['budget_level']} (constraint: {"Yes" if constraints['has_budget_constraint'] else "No"})
- Urgency: {constraints['urgency_level']} (constraint: {"Yes" if constraints['has_time_constraint'] else "No"})
- Expertise: {constraints['expertise_level']} (knowledge gap: {"Yes" if constraints['has_knowledge_gap'] else "No"})
"""
        return formatted.strip()

    def _format_signals(self, signals: Dict[str, Any]) -> str:
        """Format signal dictionary as readable text."""
        active_signals = [k.replace("_", " ") for k, v in signals.items() if v]
        return ", ".join(active_signals) if active_signals else "None detected"
