from app.config import Settings
from app.services.ai_service import AIService
from app.services.chat_service import ChatService
from app.services.jira_service import JiraService
from app.services.rag_service import RagService
from app.services.session_store import SessionStore
from app.services.settings_service import SettingsService
from app.services.template_service import TemplateService

_settings: Settings | None = None
_template_service: TemplateService | None = None
_ai_service: AIService | None = None
_jira_service: JiraService | None = None
_rag_service: RagService | None = None
_session_store: SessionStore | None = None
_chat_service: ChatService | None = None
_settings_service: SettingsService | None = None


def _build_settings_from_effective(effective: dict) -> Settings:
    """env Settings를 기반으로 effective 값으로 오버라이드된 Settings 객체 생성."""
    assert _settings is not None
    overrides = {k: v for k, v in effective.items() if v is not None}
    return _settings.model_copy(update=overrides)


def init_services(settings: Settings):
    global _settings, _template_service, _ai_service
    global _jira_service, _rag_service, _session_store, _chat_service
    global _settings_service

    _settings = settings
    _settings_service = SettingsService(settings)

    # effective settings (env + json overrides)
    effective = _settings_service.get_effective()
    eff_settings = _build_settings_from_effective(effective)

    _template_service = TemplateService()
    _rag_service = RagService()
    _ai_service = AIService(eff_settings, _template_service, _rag_service)
    _jira_service = JiraService(eff_settings)
    _session_store = SessionStore(ttl_hours=settings.session_ttl_hours)
    _chat_service = ChatService(
        ai_service=_ai_service,
        template_service=_template_service,
        jira_service=_jira_service,
        session_store=_session_store,
    )


async def reinit_services(effective: dict) -> None:
    """설정 변경 시 AIService, JiraService를 재생성."""
    global _ai_service, _jira_service, _chat_service

    eff_settings = _build_settings_from_effective(effective)

    # 기존 Jira 클라이언트 닫기
    if _jira_service:
        await _jira_service.close()

    _ai_service = AIService(eff_settings, _template_service, _rag_service)
    _jira_service = JiraService(eff_settings)
    _chat_service = ChatService(
        ai_service=_ai_service,
        template_service=_template_service,
        jira_service=_jira_service,
        session_store=_session_store,
    )


def get_settings() -> Settings:
    assert _settings is not None
    return _settings


def get_template_service() -> TemplateService:
    assert _template_service is not None
    return _template_service


def get_ai_service() -> AIService:
    assert _ai_service is not None
    return _ai_service


def get_jira_service() -> JiraService:
    assert _jira_service is not None
    return _jira_service


def get_session_store() -> SessionStore:
    assert _session_store is not None
    return _session_store


def get_rag_service() -> RagService:
    assert _rag_service is not None
    return _rag_service


def get_chat_service() -> ChatService:
    assert _chat_service is not None
    return _chat_service


def get_settings_service() -> SettingsService:
    assert _settings_service is not None
    return _settings_service
