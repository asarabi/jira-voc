from pydantic import BaseModel


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatMessage(BaseModel):
    id: str
    role: str  # user, assistant, system
    content: str
    type: str = "text"  # text, template_preview, ticket_created
    metadata: dict | None = None
    timestamp: str = ""


class ChatResponse(BaseModel):
    session_id: str
    message: str
    type: str = "text"  # text, template_preview, ticket_created
    metadata: dict | None = None


class ConfirmRequest(BaseModel):
    template_id: str
    fields: dict
