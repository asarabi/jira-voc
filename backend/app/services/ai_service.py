import json
import logging

from openai import AsyncOpenAI

from app.config import Settings
from app.prompts.voc_classifier import SYSTEM_PROMPT as CLASSIFIER_PROMPT
from app.prompts.field_extractor import SYSTEM_PROMPT as EXTRACTOR_PROMPT
from app.prompts.ticket_analyzer import SYSTEM_PROMPT as ANALYZER_PROMPT
from app.schemas.template import JiraTemplate
from app.services.rag_service import RagService
from app.services.template_service import TemplateService

logger = logging.getLogger(__name__)


class AIService:
    def __init__(
        self,
        settings: Settings,
        template_service: TemplateService,
        rag_service: RagService,
    ):
        self.client = AsyncOpenAI(
            base_url=settings.ai_base_url,
            api_key=settings.ai_api_key,
        )
        self.model = settings.ai_model_name
        self.template_service = template_service
        self.rag = rag_service

    async def classify_voc(
        self,
        voc_text: str,
        conversation_history: list[dict] | None = None,
    ) -> dict:
        templates_summary = self.template_service.get_templates_summary_text()
        system_prompt = CLASSIFIER_PROMPT.format(
            templates_summary=templates_summary
        )

        # RAG: 유사 과거 VOC 사례를 컨텍스트로 추가
        rag_context = self.rag.format_context_for_prompt(voc_text, top_k=3)
        if rag_context:
            system_prompt += f"\n\n참고할 수 있는 과거 데이터:\n{rag_context}"

        messages = [{"role": "system", "content": system_prompt}]
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": voc_text})

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.1,
        )

        content = response.choices[0].message.content
        return self._parse_json_response(content)

    async def extract_fields(
        self,
        voc_text: str,
        template: JiraTemplate,
        conversation_history: list[dict] | None = None,
    ) -> dict:
        fields_definition = self.template_service.get_fields_definition_text(
            template
        )
        system_prompt = EXTRACTOR_PROMPT.format(
            template_name=template.name,
            fields_definition=fields_definition,
        )

        messages = [{"role": "system", "content": system_prompt}]
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": voc_text})

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.2,
        )

        content = response.choices[0].message.content
        return self._parse_json_response(content)

    async def analyze_ticket(self, ticket_data: dict) -> str:
        fields = ticket_data.get("fields", {})
        description_raw = fields.get("description", "N/A")

        # ADF format -> plain text extraction
        if isinstance(description_raw, dict):
            description = self._extract_text_from_adf(description_raw)
        else:
            description = str(description_raw) if description_raw else "N/A"

        summary = fields.get("summary", "N/A")

        # RAG: 유사 VOC + 관련 가이드를 참고 자료로 검색
        search_query = f"{summary} {description[:200]}"
        rag_context = self.rag.format_context_for_prompt(search_query, top_k=3)
        additional = ""
        if rag_context:
            additional = f"\n\n참고 자료:\n{rag_context}"

        system_prompt = ANALYZER_PROMPT.format(
            ticket_key=ticket_data.get("key", ""),
            issue_type=fields.get("issuetype", {}).get("name", "N/A"),
            summary=summary,
            description=description,
            priority=fields.get("priority", {}).get("name", "N/A"),
            additional_fields=additional,
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "이 티켓을 분석하고 가이드를 제공해주세요."},
        ]

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3,
        )

        return response.choices[0].message.content

    def _parse_json_response(self, content: str) -> dict:
        content = content.strip()
        # Strip markdown code fences if present
        if content.startswith("```"):
            lines = content.split("\n")
            lines = lines[1:]  # remove opening fence
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            content = "\n".join(lines)

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            logger.warning("Failed to parse AI JSON response: %s", content)
            return {
                "action": "clarify",
                "question": "죄송합니다, 다시 한번 말씀해 주시겠어요? 좀 더 구체적으로 설명해 주시면 도움이 됩니다.",
                "candidates": [],
            }

    def _extract_text_from_adf(self, adf: dict) -> str:
        texts = []
        for block in adf.get("content", []):
            for inline in block.get("content", []):
                if inline.get("type") == "text":
                    texts.append(inline.get("text", ""))
        return "\n".join(texts) if texts else "N/A"
