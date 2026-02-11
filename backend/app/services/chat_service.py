import logging

from app.schemas.chat import ChatResponse
from app.services.ai_service import AIService
from app.services.jira_service import JiraService
from app.services.session_store import SessionStore
from app.services.template_service import TemplateService

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(
        self,
        ai_service: AIService,
        template_service: TemplateService,
        jira_service: JiraService,
        session_store: SessionStore,
    ):
        self.ai = ai_service
        self.templates = template_service
        self.jira = jira_service
        self.sessions = session_store

    async def handle_message(
        self, session_id: str, user_message: str
    ) -> ChatResponse:
        session = self.sessions.get_or_create(session_id)
        session.add_message("user", user_message)

        # If we already matched a template and are awaiting more info
        if session.pending_template_id:
            return await self._continue_field_extraction(
                session, user_message
            )

        # Classify VOC against templates
        classification = await self.ai.classify_voc(
            voc_text=user_message,
            conversation_history=session.recent_messages(limit=10),
        )

        if classification.get("action") == "clarify":
            question = classification.get("question", "좀 더 자세히 설명해 주시겠어요?")
            session.add_message("assistant", question)
            return ChatResponse(
                session_id=session_id,
                message=question,
                type="text",
            )

        # Template matched — extract fields
        template_id = classification.get("template_id", "")
        template = self.templates.get_template(template_id)

        if template is None:
            msg = "죄송합니다, 적절한 템플릿을 찾지 못했습니다. 다시 설명해 주시겠어요?"
            session.add_message("assistant", msg)
            return ChatResponse(
                session_id=session_id, message=msg, type="text"
            )

        extracted_fields = await self.ai.extract_fields(
            voc_text=user_message,
            template=template,
            conversation_history=session.recent_messages(limit=10),
        )

        session.pending_template_id = template.id
        session.pending_fields = extracted_fields

        preview_message = self._format_preview(template, extracted_fields)
        session.add_message(
            "assistant",
            preview_message,
            msg_type="template_preview",
            metadata={
                "template_id": template.id,
                "template_name": template.name,
                "fields": extracted_fields,
            },
        )

        return ChatResponse(
            session_id=session_id,
            message=preview_message,
            type="template_preview",
            metadata={
                "template_id": template.id,
                "template_name": template.name,
                "fields": extracted_fields,
            },
        )

    async def _continue_field_extraction(self, session, user_message: str) -> ChatResponse:
        template = self.templates.get_template(session.pending_template_id)
        if template is None:
            session.pending_template_id = None
            session.pending_fields = None
            msg = "세션 정보가 올바르지 않습니다. 다시 VOC를 입력해 주세요."
            session.add_message("assistant", msg)
            return ChatResponse(
                session_id=session.id, message=msg, type="text"
            )

        extracted_fields = await self.ai.extract_fields(
            voc_text=user_message,
            template=template,
            conversation_history=session.recent_messages(limit=10),
        )

        session.pending_fields = extracted_fields

        preview_message = self._format_preview(template, extracted_fields)
        session.add_message(
            "assistant",
            preview_message,
            msg_type="template_preview",
            metadata={
                "template_id": template.id,
                "template_name": template.name,
                "fields": extracted_fields,
            },
        )

        return ChatResponse(
            session_id=session.id,
            message=preview_message,
            type="template_preview",
            metadata={
                "template_id": template.id,
                "template_name": template.name,
                "fields": extracted_fields,
            },
        )

    async def confirm_and_create(
        self, session_id: str, template_id: str, fields: dict
    ) -> dict:
        session = self.sessions.get(session_id)
        if session is None:
            raise ValueError("Session not found")

        template = self.templates.get_template(template_id)
        if template is None:
            raise ValueError("Template not found")

        result = await self.jira.create_issue(
            issue_type=template.jira_issue_type, fields=fields
        )

        session.pending_template_id = None
        session.pending_fields = None

        ticket_key = result.get("key", "")
        ticket_url = f"{self.jira.base_url}/browse/{ticket_key}"
        ticket_message = f"Jira 티켓 **{ticket_key}**이(가) 성공적으로 생성되었습니다!\n링크: {ticket_url}"

        session.add_message(
            "assistant",
            ticket_message,
            msg_type="ticket_created",
            metadata={"ticket_key": ticket_key, "ticket_url": ticket_url},
        )

        return {
            "ticket_key": ticket_key,
            "ticket_url": ticket_url,
        }

    def _format_preview(self, template, fields: dict) -> str:
        lines = [f"**[{template.name}]** 템플릿으로 Jira 티켓을 생성할 준비가 되었습니다.\n"]
        lines.append("**미리보기:**")
        for tf in template.fields:
            value = fields.get(tf.key, "")
            if value:
                lines.append(f"- **{tf.label}**: {value}")
        lines.append("\n이 내용으로 티켓을 생성하시겠습니까? 수정이 필요하면 말씀해 주세요.")
        return "\n".join(lines)
