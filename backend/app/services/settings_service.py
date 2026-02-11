import json
import logging
from pathlib import Path

from app.config import Settings

logger = logging.getLogger(__name__)

SETTINGS_FILE = Path(__file__).resolve().parent.parent.parent / "settings.json"


def _mask(value: str) -> str:
    if not value or len(value) <= 4:
        return "****"
    return value[:2] + "*" * (len(value) - 4) + value[-2:]


class SettingsService:
    def __init__(self, env_settings: Settings):
        self._env = env_settings

    def _load_overrides(self) -> dict:
        if SETTINGS_FILE.exists():
            try:
                return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                logger.warning("Failed to read settings.json, using defaults")
        return {}

    def _save_overrides(self, data: dict) -> None:
        SETTINGS_FILE.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def get_effective(self) -> dict:
        overrides = self._load_overrides()
        return {
            "ai_base_url": overrides.get("ai_base_url", self._env.ai_base_url),
            "ai_api_key": overrides.get("ai_api_key", self._env.ai_api_key),
            "ai_model_name": overrides.get("ai_model_name", self._env.ai_model_name),
            "jira_base_url": overrides.get("jira_base_url", self._env.jira_base_url),
            "jira_user_email": overrides.get("jira_user_email", self._env.jira_user_email),
            "jira_api_token": overrides.get("jira_api_token", self._env.jira_api_token),
            "jira_project_key": overrides.get("jira_project_key", self._env.jira_project_key),
        }

    def get_masked(self) -> dict:
        eff = self.get_effective()
        return {
            **eff,
            "ai_api_key": _mask(eff["ai_api_key"]),
            "jira_api_token": _mask(eff["jira_api_token"]),
        }

    def update(self, updates: dict) -> dict:
        overrides = self._load_overrides()
        for key, value in updates.items():
            if value is not None:
                overrides[key] = value
        self._save_overrides(overrides)
        return self.get_effective()
