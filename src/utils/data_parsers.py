"""
Data Parsers - Shared utilities for parsing user history data.
"""

import csv
import json
from io import StringIO
from typing import List, Dict, Any, Tuple
from collections import defaultdict

def parse_user_histories_from_csv(csv_content: str) -> Tuple[List[List[Dict[str, Any]]], List[str]]:
    """
    Parse CSV content into user histories format expected by embedder.

    Args:
        csv_content: CSV string with user session data

    Returns:
        (user_histories, user_ids) - grouped by user_id

    CSV Format:
        user_id,session_intent,confidence,timestamp,channel,engagement_level,
        has_budget_constraint,has_time_constraint,has_knowledge_gap,
        urgency_level,expertise_level
    """
    reader = csv.DictReader(StringIO(csv_content))

    # Group sessions by user_id
    user_sessions = defaultdict(list)

    for row in reader:
        user_id = row.get('user_id', '').strip()
        if not user_id:
            continue

        # Parse boolean fields
        def parse_bool(val: str) -> bool:
            return val.strip().lower() in ('true', '1', 'yes')

        session = {
            'intent': row.get('session_intent', '').strip(),
            'confidence': float(row.get('confidence', 0.5)),
            'timestamp': row.get('timestamp', '').strip(),
            'channel': row.get('channel', 'organic').strip(),
            'engagement_level': row.get('engagement_level', 'medium').strip(),
            'has_budget_constraint': parse_bool(row.get('has_budget_constraint', 'false')),
            'has_time_constraint': parse_bool(row.get('has_time_constraint', 'false')),
            'has_knowledge_gap': parse_bool(row.get('has_knowledge_gap', 'false')),
            'urgency_level': row.get('urgency_level', 'medium').strip(),
            'expertise_level': row.get('expertise_level', 'intermediate').strip()
        }

        user_sessions[user_id].append(session)

    # Convert to list format
    user_ids = sorted(user_sessions.keys())
    user_histories = [user_sessions[uid] for uid in user_ids]

    return user_histories, user_ids

def parse_user_histories_from_json(json_content: str) -> Tuple[List[List[Dict[str, Any]]], List[str]]:
    """
    Parse JSON content into user histories.
    
    Expected JSON format:
    [
        {
            "user_id": "user_1",
            "history": [
                {"intent": "...", ...},
                ...
            ]
        },
        ...
    ]
    OR list of flat records like CSV.
    """
    try:
        data = json.loads(json_content)
    except json.JSONDecodeError:
        return [], []

    if not isinstance(data, list):
        return [], []

    # Check if it's already grouped
    if data and 'history' in data[0]:
        user_ids = [d.get('user_id', f'user_{i}') for i, d in enumerate(data)]
        user_histories = [d.get('history', []) for d in data]
        return user_histories, user_ids

    # Assume flat records, group by user_id
    user_sessions = defaultdict(list)
    for i, row in enumerate(data):
        user_id = row.get('user_id', f'user_{i}') # Default unique ID if missing
        
        # Normalize fields if needed (similar to CSV parsing)
        session = row.copy()
        # Ensure minimal fields
        if 'intent' not in session and 'session_intent' in session:
            session['intent'] = session['session_intent']
            
        user_sessions[user_id].append(session)

    user_ids = sorted(user_sessions.keys())
    user_histories = [user_sessions[uid] for uid in user_ids]
    
    return user_histories, user_ids
