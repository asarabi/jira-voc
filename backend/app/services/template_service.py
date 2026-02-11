import os
from pathlib import Path

import yaml

from app.schemas.template import JiraTemplate, TemplateSummary


class TemplateService:
    def __init__(self, templates_dir: str | None = None):
        if templates_dir is None:
            templates_dir = str(
                Path(__file__).parent.parent.parent / "templates"
            )
        self._templates_dir = templates_dir
        self._templates: dict[str, JiraTemplate] = {}
        self._load_templates()

    def _load_templates(self):
        for filename in os.listdir(self._templates_dir):
            if filename.startswith("_") or not filename.endswith(".yaml"):
                continue
            filepath = os.path.join(self._templates_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            template = JiraTemplate(**data)
            self._templates[template.id] = template

    def get_all_templates(self) -> list[JiraTemplate]:
        return list(self._templates.values())

    def get_template(self, template_id: str) -> JiraTemplate | None:
        return self._templates.get(template_id)

    def get_summaries(self) -> list[TemplateSummary]:
        return [
            TemplateSummary(
                id=t.id,
                name=t.name,
                description=t.description,
                jira_issue_type=t.jira_issue_type,
                keywords=t.keywords,
            )
            for t in self._templates.values()
        ]

    def get_templates_summary_text(self) -> str:
        lines = []
        for t in self._templates.values():
            keywords = ", ".join(t.keywords[:5])
            lines.append(
                f"- ID: {t.id} | 이름: {t.name} | "
                f"설명: {t.description} | 키워드: {keywords}"
            )
        return "\n".join(lines)

    def get_fields_definition_text(self, template: JiraTemplate) -> str:
        lines = []
        for field in template.fields:
            parts = [
                f"  - key: {field.key}",
                f"    label: {field.label}",
                f"    type: {field.type}",
                f"    required: {field.required}",
            ]
            if field.options:
                parts.append(f"    options: {field.options}")
            if field.ai_instruction:
                parts.append(f"    ai_instruction: {field.ai_instruction}")
            lines.append("\n".join(parts))
        return "\n".join(lines)
