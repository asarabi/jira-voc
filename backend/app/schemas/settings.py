from pydantic import BaseModel


class AdminSettingsResponse(BaseModel):
    ai_base_url: str = ""
    ai_api_key: str = ""  # 마스킹된 값
    ai_model_name: str = ""
    jira_base_url: str = ""
    jira_user_email: str = ""
    jira_api_token: str = ""  # 마스킹된 값
    jira_project_key: str = ""


class AdminSettingsUpdate(BaseModel):
    ai_base_url: str | None = None
    ai_api_key: str | None = None
    ai_model_name: str | None = None
    jira_base_url: str | None = None
    jira_user_email: str | None = None
    jira_api_token: str | None = None
    jira_project_key: str | None = None


class VerifyPasswordRequest(BaseModel):
    password: str
