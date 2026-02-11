from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # AI Service
    ai_base_url: str = "http://localhost:8000/v1"
    ai_api_key: str = ""
    ai_model_name: str = "default-model"

    # Jira Cloud
    jira_base_url: str = "https://yourorg.atlassian.net"
    jira_user_email: str = ""
    jira_api_token: str = ""
    jira_project_key: str = "VOC"

    # Admin
    admin_password: str = ""

    # Application
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    cors_origins: str = "http://localhost:5173"
    log_level: str = "INFO"
    session_ttl_hours: int = 24

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}
