"""
Meta (Facebook) Custom Audiences connector.

Uses Marketing API to upload hashed identifiers to Custom Audiences. Supports
dry run mode for local testing without network access.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import yaml

try:  # pragma: no cover - optional dependency
    from facebook_business.adobjects.customaudience import CustomAudience  # type: ignore
    from facebook_business.api import FacebookAdsApi  # type: ignore
except ImportError:  # pragma: no cover
    CustomAudience = None  # type: ignore
    FacebookAdsApi = None  # type: ignore

from ..base import ActivationContext, ActivationError, AudienceCohort, AudienceConnector


class MetaAdsAudienceConnector(AudienceConnector):
    """Uploads hashed identifiers to Meta Custom Audiences."""

    component_name = "meta_ads"

    def __init__(
        self,
        *,
        config_path: str = "config/activation/audiences.yaml",
        dry_run: Optional[bool] = None,
    ) -> None:
        super().__init__()
        self.config = self._load_config(config_path)
        self.batch_size = int(self.config.get("batch_size", 5000))
        self.dry_run = dry_run if dry_run is not None else bool(self.config.get("dry_run", True))
        self.hashing_salt = self.config.get("hashing_salt", "")
        self.credentials = {
            "access_token": os.getenv("META_ACCESS_TOKEN") or self.config.get("access_token"),
            "app_secret": os.getenv("META_APP_SECRET") or self.config.get("app_secret"),
            "account_id": os.getenv("META_AD_ACCOUNT_ID") or self.config.get("account_id"),
        }

        if not self.dry_run and (CustomAudience is None or FacebookAdsApi is None):
            raise ActivationError("facebook-business SDK not installed or configured.")

        self.api_initialized = False
        if not self.dry_run and FacebookAdsApi:
            if not all(self.credentials.values()):
                raise ActivationError(
                    "Missing Meta credentials. Set META_ACCESS_TOKEN / META_APP_SECRET / META_AD_ACCOUNT_ID."
                )
            FacebookAdsApi.init(
                access_token=self.credentials.get("access_token"),
                app_secret=self.credentials.get("app_secret"),
            )
            self.api_initialized = True

    def sync(self, cohort: AudienceCohort, context: ActivationContext) -> Dict[str, Any]:
        hashed = self._hash_identifiers(cohort.user_ids)
        batches = list(self._batch(hashed, self.batch_size))
        if not batches:
            raise ActivationError("Audience cohort contains no identifiers to sync.")

        metadata = {
            "audience_name": cohort.name,
            "user_count": len(hashed),
            "batch_count": len(batches),
            "dry_run": self.dry_run,
        }

        if self.dry_run:
            metadata["status"] = "simulated_upload"
            metadata["sample_hash"] = hashed[:3]
            return metadata

        if not self.api_initialized:
            raise ActivationError("Meta API not initialized.")

        audience_id = self._create_or_get_audience(cohort)
        operations = []
        for batch in batches:
            operations.append(self._upload_batch(audience_id, batch))

        metadata["status"] = "uploaded"
        metadata["audience_id"] = audience_id
        metadata["operations"] = operations
        return metadata

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _load_config(self, path_str: str) -> Dict[str, Any]:
        path = Path(path_str)
        if not path.exists():
            raise ActivationError(f"Audience config not found: {path_str}")
        with path.open("r", encoding="utf-8") as f:
            content = yaml.safe_load(f) or {}
        return content.get("meta_ads", {})

    def _hash_identifiers(self, identifiers: Iterable[str]) -> List[str]:
        hashed = []
        for value in identifiers:
            if not value:
                continue
            normalized = value.strip().lower()
            digest = hashlib.sha256((self.hashing_salt + normalized).encode("utf-8")).hexdigest()
            hashed.append(digest)
        return hashed

    def _batch(self, items: List[str], size: int) -> Iterable[List[str]]:
        for i in range(0, len(items), size):
            yield items[i : i + size]

    def _create_or_get_audience(self, cohort: AudienceCohort) -> str:
        """Create a Custom Audience for the cohort."""
        params = {
            CustomAudience.Field.name: cohort.name,
            CustomAudience.Field.subtype: CustomAudience.Subtype.custom,
            CustomAudience.Field.description: cohort.description or "Intent-based audience",
        }
        audience = CustomAudience(parent_id=self.credentials.get("account_id"))
        audience.remote_create(params=params)
        return audience.get_id()

    def _upload_batch(self, audience_id: str, batch: List[str]) -> Dict[str, Any]:
        audience = CustomAudience(audience_id)
        payload = [{"match_keys": {"email": hashed}} for hashed in batch]
        audience.add_users(
            schema=CustomAudience.Schema.email_hash,
            users=payload,
        )
        return {"audience_id": audience_id, "uploaded": len(batch)}
