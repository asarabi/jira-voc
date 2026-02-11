from pydantic import BaseModel


class JiraCreateRequest(BaseModel):
    template_id: str
    fields: dict
    session_id: str | None = None


class JiraTicketResponse(BaseModel):
    key: str
    url: str
    summary: str = ""
    status: str = "created"
