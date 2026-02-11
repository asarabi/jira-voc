import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class ChatSession:
    id: str
    messages: list = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    pending_template_id: str | None = None
    pending_fields: dict | None = None

    def add_message(
        self, role: str, content: str, msg_type: str = "text", metadata: dict | None = None
    ):
        self.messages.append(
            {
                "id": str(uuid.uuid4()),
                "role": role,
                "content": content,
                "type": msg_type,
                "metadata": metadata,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    def recent_messages(self, limit: int = 10) -> list[dict]:
        return [
            {"role": m["role"], "content": m["content"]}
            for m in self.messages[-limit:]
        ]


class SessionStore:
    def __init__(self, ttl_hours: int = 24):
        self._sessions: dict[str, ChatSession] = {}
        self._ttl = timedelta(hours=ttl_hours)

    def get_or_create(self, session_id: str) -> ChatSession:
        self._cleanup_expired()
        if session_id not in self._sessions:
            self._sessions[session_id] = ChatSession(id=session_id)
        return self._sessions[session_id]

    def get(self, session_id: str) -> ChatSession | None:
        return self._sessions.get(session_id)

    def _cleanup_expired(self):
        now = datetime.utcnow()
        expired = [
            sid
            for sid, s in self._sessions.items()
            if now - s.created_at > self._ttl
        ]
        for sid in expired:
            del self._sessions[sid]
