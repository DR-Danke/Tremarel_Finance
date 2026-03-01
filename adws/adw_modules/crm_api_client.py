"""CRM API client for prospect and meeting record management.

Encapsulates all HTTP calls to the backend CRM API endpoints:
- Authentication (JWT token acquisition)
- Prospect search, creation, and stage advancement
- Meeting record creation
"""

import logging
from typing import Optional

import requests


class CrmApiClient:
    """Client for interacting with the CRM backend API."""

    def __init__(self, base_url: str, logger: logging.Logger) -> None:
        self._base_url = base_url.rstrip("/")
        self._logger = logger
        self._token: Optional[str] = None
        self._timeout = 30

    def authenticate(self, email: str, password: str) -> bool:
        """Authenticate with the backend API and cache the JWT token.

        Returns True on success, False on failure.
        """
        url = f"{self._base_url}/auth/login"
        self._logger.info(f"CrmApiClient: Authenticating as {email}")
        try:
            resp = requests.post(
                url,
                json={"email": email, "password": password},
                timeout=self._timeout,
            )
            if resp.status_code == 200:
                self._token = resp.json()["access_token"]
                self._logger.info("CrmApiClient: Authentication successful")
                return True
            else:
                self._logger.error(
                    f"CrmApiClient: Authentication failed with status {resp.status_code}"
                )
                return False
        except requests.RequestException as e:
            self._logger.error(f"CrmApiClient: Authentication request failed: {e}")
            return False

    def _headers(self) -> dict:
        """Return authorization headers for API requests."""
        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

    def search_prospect(
        self, entity_id: str, company_name: str
    ) -> Optional[dict]:
        """Search for an existing prospect by company name (case-insensitive).

        Returns the first matching prospect dict or None.
        """
        url = f"{self._base_url}/prospects/"
        self._logger.info(
            f"CrmApiClient: Searching prospects for company '{company_name}' in entity {entity_id}"
        )
        try:
            resp = requests.get(
                url,
                params={"entity_id": entity_id, "limit": 100},
                headers=self._headers(),
                timeout=self._timeout,
            )
            if resp.status_code != 200:
                self._logger.error(
                    f"CrmApiClient: Prospect search failed with status {resp.status_code}"
                )
                return None

            prospects = resp.json().get("prospects", [])
            target = company_name.lower()
            for prospect in prospects:
                if prospect.get("company_name", "").lower() == target:
                    self._logger.info(
                        f"CrmApiClient: Found matching prospect {prospect['id']} "
                        f"for company '{company_name}'"
                    )
                    return prospect

            self._logger.info(
                f"CrmApiClient: No prospect found for company '{company_name}'"
            )
            return None
        except requests.RequestException as e:
            self._logger.error(f"CrmApiClient: Prospect search request failed: {e}")
            return None

    def create_prospect(
        self,
        entity_id: str,
        company_name: str,
        contact_name: Optional[str] = None,
        contact_email: Optional[str] = None,
        stage: str = "lead",
        source: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Optional[dict]:
        """Create a new prospect via the API.

        Returns the created prospect dict or None on failure.
        """
        url = f"{self._base_url}/prospects/"
        payload = {
            "entity_id": entity_id,
            "company_name": company_name,
            "stage": stage,
        }
        if contact_name:
            payload["contact_name"] = contact_name
        if contact_email:
            payload["contact_email"] = contact_email
        if source:
            payload["source"] = source
        if notes:
            payload["notes"] = notes

        self._logger.info(
            f"CrmApiClient: Creating prospect for company '{company_name}'"
        )
        try:
            resp = requests.post(
                url,
                json=payload,
                headers=self._headers(),
                timeout=self._timeout,
            )
            if resp.status_code == 201:
                prospect = resp.json()
                self._logger.info(
                    f"CrmApiClient: Prospect created with ID {prospect.get('id')}"
                )
                return prospect
            else:
                self._logger.error(
                    f"CrmApiClient: Prospect creation failed with status {resp.status_code}: "
                    f"{resp.text[:200]}"
                )
                return None
        except requests.RequestException as e:
            self._logger.error(f"CrmApiClient: Prospect creation request failed: {e}")
            return None

    def create_meeting_record(
        self,
        entity_id: str,
        prospect_id: str,
        title: str,
        transcript_ref: Optional[str] = None,
        summary: Optional[str] = None,
        action_items: Optional[list[str]] = None,
        participants: Optional[list[str]] = None,
        html_output: Optional[str] = None,
        meeting_date: Optional[str] = None,
    ) -> Optional[dict]:
        """Create a meeting record linked to a prospect.

        Returns the created meeting record dict or None on failure.
        """
        url = f"{self._base_url}/meeting-records/"
        payload: dict = {
            "entity_id": entity_id,
            "prospect_id": prospect_id,
            "title": title,
        }
        if transcript_ref:
            payload["transcript_ref"] = transcript_ref
        if summary:
            payload["summary"] = summary
        if action_items is not None:
            payload["action_items"] = action_items
        if participants is not None:
            payload["participants"] = participants
        if html_output:
            payload["html_output"] = html_output
        if meeting_date:
            payload["meeting_date"] = meeting_date

        self._logger.info(
            f"CrmApiClient: Creating meeting record '{title}' for prospect {prospect_id}"
        )
        try:
            resp = requests.post(
                url,
                json=payload,
                headers=self._headers(),
                timeout=self._timeout,
            )
            if resp.status_code == 201:
                record = resp.json()
                self._logger.info(
                    f"CrmApiClient: Meeting record created with ID {record.get('id')}"
                )
                return record
            else:
                self._logger.error(
                    f"CrmApiClient: Meeting record creation failed with status {resp.status_code}: "
                    f"{resp.text[:200]}"
                )
                return None
        except requests.RequestException as e:
            self._logger.error(
                f"CrmApiClient: Meeting record creation request failed: {e}"
            )
            return None

    def advance_prospect_stage(
        self,
        prospect_id: str,
        entity_id: str,
        new_stage: str,
        notes: Optional[str] = None,
    ) -> Optional[dict]:
        """Advance a prospect's pipeline stage.

        Returns the updated prospect dict or None on failure.
        """
        url = f"{self._base_url}/prospects/{prospect_id}/stage"
        payload: dict = {"new_stage": new_stage}
        if notes:
            payload["notes"] = notes

        self._logger.info(
            f"CrmApiClient: Advancing prospect {prospect_id} to stage '{new_stage}'"
        )
        try:
            resp = requests.patch(
                url,
                json=payload,
                params={"entity_id": entity_id},
                headers=self._headers(),
                timeout=self._timeout,
            )
            if resp.status_code == 200:
                prospect = resp.json()
                self._logger.info(
                    f"CrmApiClient: Prospect {prospect_id} advanced to '{new_stage}'"
                )
                return prospect
            else:
                self._logger.error(
                    f"CrmApiClient: Stage advance failed with status {resp.status_code}: "
                    f"{resp.text[:200]}"
                )
                return None
        except requests.RequestException as e:
            self._logger.error(
                f"CrmApiClient: Stage advance request failed: {e}"
            )
            return None
