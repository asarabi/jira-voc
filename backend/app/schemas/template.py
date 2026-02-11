from pydantic import BaseModel


class TemplateField(BaseModel):
    key: str
    label: str
    type: str  # string, text, select, multiselect, number, date
    required: bool = False
    options: list[str] | None = None
    ai_instruction: str = ""
    default: str | None = None


class JiraTemplate(BaseModel):
    id: str
    name: str
    description: str
    jira_issue_type: str
    keywords: list[str] = []
    fields: list[TemplateField] = []


class TemplateSummary(BaseModel):
    id: str
    name: str
    description: str
    jira_issue_type: str
    keywords: list[str] = []
