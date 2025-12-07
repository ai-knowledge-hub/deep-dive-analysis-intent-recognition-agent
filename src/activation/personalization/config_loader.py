"""Helpers for loading personalization configuration."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml


def load_personalization_config(path: str) -> Dict[str, Any]:
    """Load YAML configuration for personalization engines."""
    file_path = Path(path)
    if not file_path.exists():
        return {}
    with file_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}
