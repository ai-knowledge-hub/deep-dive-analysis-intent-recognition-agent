"""
Google Ads Customer Match connector.

Implements the AudienceConnector contract and syncs hashed identifiers into
Google Ads user lists. When google-ads SDK is unavailable or dry_run=True, the
connector simulates uploads so developers can validate the activation layer
without external dependencies.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import yaml

from ..base import ActivationContext, ActivationError, AudienceCohort, AudienceConnector

try:  # pragma: no cover - optional dependency
    from google.ads.googleads.client import GoogleAdsClient  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    GoogleAdsClient = None  # type: ignore


class GoogleAdsAudienceConnector(AudienceConnector):
    """
    Google Ads Customer Match exporter.

    Required config values:
        developer_token, login_customer_id, customer_id,
        client_id, client_secret, refresh_token
    """

    component_name = "google_ads"

    def __init__(
        self,
        *,
        config_path: str = "config/activation/audiences.yaml",
        dry_run: Optional[bool] = None,
    ) -> None:
        super().__init__()
        self.config = self._load_config(config_path)
        self.batch_size = int(self.config.get("batch_size", 1000))
        self.dry_run = dry_run if dry_run is not None else bool(self.config.get("dry_run", True))
        self.hashing_salt = self.config.get("hashing_salt", "")
        self.credentials = {
            "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN") or self.config.get("developer_token"),
            "login_customer_id": os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID") or self.config.get("login_customer_id"),
            "customer_id": os.getenv("GOOGLE_ADS_CUSTOMER_ID") or self.config.get("customer_id"),
            "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID") or self.config.get("client_id"),
            "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET") or self.config.get("client_secret"),
            "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN") or self.config.get("refresh_token"),
        }

        if not self.dry_run and GoogleAdsClient is None:
            raise ActivationError(
                "google-ads SDK not installed. Install google-ads or set dry_run=True."
            )

        self.client = None
        if not self.dry_run and GoogleAdsClient:
            if not all(self.credentials.values()):
                raise ActivationError(
                    "Missing Google Ads credentials. Set GOOGLE_ADS_* env vars or update config overrides."
                )
            self.client = GoogleAdsClient.load_from_dict(
                {
                    "developer_token": self.credentials["developer_token"],
                    "login_customer_id": self.credentials["login_customer_id"],
                    "use_proto_plus": True,
                    "oauth2_client_id": self.credentials["client_id"],
                    "oauth2_client_secret": self.credentials["client_secret"],
                    "oauth2_refresh_token": self.credentials["refresh_token"],
                }
            )

    # ------------------------------------------------------------------
    # AudienceConnector interface
    # ------------------------------------------------------------------
    def sync(self, cohort: AudienceCohort, context: ActivationContext) -> Dict[str, Any]:
        hashed_ids = self._hash_identifiers(cohort.user_ids)
        batches = list(self._batch(hashed_ids, self.batch_size))

        if not batches:
            raise ActivationError("Audience cohort contains no identifiers to sync.")

        metadata = {
            "audience_name": cohort.name,
            "user_count": len(hashed_ids),
            "batch_count": len(batches),
            "dry_run": self.dry_run,
        }

        if self.dry_run:
            metadata["status"] = "simulated_upload"
            metadata["sample_hash"] = hashed_ids[:3]
            return metadata

        if self.client is None:
            raise ActivationError("Google Ads client not configured.")

        user_list_resource = self._create_or_get_user_list(cohort)
        uploads = []
        for batch in batches:
            uploads.append(self._upload_batch(user_list_resource, batch))

        metadata["status"] = "uploaded"
        metadata["user_list_resource"] = user_list_resource
        metadata["operations"] = uploads
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
        return content.get("google_ads", {})

    def _hash_identifiers(self, identifiers: Iterable[str]) -> List[str]:
        hashed: List[str] = []
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

    def _create_or_get_user_list(self, cohort: AudienceCohort) -> str:
        """
        Create or fetch the Customer Match user list.
        This simplified implementation always creates a new list.
        """
        user_list_service = self.client.get_service("UserListService")
        user_list_operation = self.client.get_type("UserListOperation")
        user_list = user_list_operation.create
        user_list.name = cohort.name
        user_list.description = cohort.description or "Intent-based audience"
        user_list.membership_life_span = 540
        crm_based = user_list.crm_based_user_list
        crm_based.upload_key_type = self.client.enums.CustomerMatchUploadKeyTypeEnum.CONTACT_INFO
        response = user_list_service.mutate_user_lists(
            customer_id=self.credentials.get("customer_id"), operations=[user_list_operation]
        )
        return response.results[0].resource_name

    def _upload_batch(self, user_list_resource: str, batch: List[str]) -> Dict[str, Any]:
        offline_user_data_job_service = self.client.get_service("OfflineUserDataJobService")
        user_data_job = self.client.get_type("OfflineUserDataJob")
        user_data_job.type_ = self.client.enums.OfflineUserDataJobTypeEnum.CUSTOMER_MATCH_USER_LIST
        user_data_job.customer_match_user_list_metadata.user_list = user_list_resource

        create_response = offline_user_data_job_service.create_offline_user_data_job(
            customer_id=self.credentials.get("customer_id"), job=user_data_job
        )
        operations = []
        for hashed in batch:
            user_data = self.client.get_type("OfflineUserDataJobOperation")
            user_identifier = self.client.get_type("UserIdentifier")
            user_identifier.hashed_email = hashed
            user_data.create.user_identifiers.append(user_identifier)
            operations.append(user_data)

        offline_user_data_job_service.add_offline_user_data_job_operations(
            resource_name=create_response.resource_name,
            operations=operations,
            enable_partial_failure=True,
            enable_warnings=True,
        )

        request = self.client.get_type("RunOfflineUserDataJobRequest")
        request.resource_name = create_response.resource_name
        offline_user_data_job_service.run_offline_user_data_job(request=request)

        return {
            "resource_name": create_response.resource_name,
            "uploaded": len(batch),
        }
