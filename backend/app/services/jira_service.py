import logging

import httpx

from app.config import Settings

logger = logging.getLogger(__name__)


def text_to_adf(text: str) -> dict:
    """Convert plain text to Atlassian Document Format."""
    paragraphs = text.split("\n\n") if text else [""]
    content = []
    for para in paragraphs:
        content.append(
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": para}],
            }
        )
    return {"version": 1, "type": "doc", "content": content}


class JiraService:
    def __init__(self, settings: Settings):
        self.base_url = settings.jira_base_url.rstrip("/")
        self.project_key = settings.jira_project_key
        self._client = httpx.AsyncClient(
            base_url=f"{self.base_url}/rest/api/3",
            auth=(settings.jira_user_email, settings.jira_api_token),
            headers={"Content-Type": "application/json"},
            timeout=30.0,
        )

    async def create_issue(self, issue_type: str, fields: dict) -> dict:
        description_text = fields.pop("description", "")
        summary = fields.pop("summary", "Untitled")

        # Handle priority format
        priority = fields.pop("priority", None)
        payload_fields = {
            "project": {"key": self.project_key},
            "issuetype": {"name": issue_type},
            "summary": summary,
            "description": text_to_adf(description_text),
        }
        if priority:
            payload_fields["priority"] = {"name": priority}

        # Handle components (multiselect -> list of objects)
        components = fields.pop("components", None)
        if components and isinstance(components, list):
            payload_fields["components"] = [
                {"name": c} for c in components
            ]

        # Add remaining custom fields
        for key, value in fields.items():
            if value is not None and value != "":
                payload_fields[key] = value

        payload = {"fields": payload_fields}
        logger.info("Creating Jira issue: %s", payload)

        response = await self._client.post("/issue", json=payload)
        response.raise_for_status()
        return response.json()

    async def get_issue(self, issue_key: str) -> dict:
        response = await self._client.get(f"/issue/{issue_key}")
        response.raise_for_status()
        return response.json()

    async def add_comment(self, issue_key: str, body: str) -> dict:
        payload = {"body": text_to_adf(body)}
        response = await self._client.post(
            f"/issue/{issue_key}/comment", json=payload
        )
        response.raise_for_status()
        return response.json()

    async def close(self):
        await self._client.aclose()
