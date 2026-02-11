from fastapi import APIRouter, HTTPException

from app.dependencies import get_chat_service, get_session_store
from app.schemas.chat import ChatRequest, ChatResponse, ConfirmRequest

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    service = get_chat_service()
    return await service.handle_message(request.session_id, request.message)


@router.get("/{session_id}/history")
async def get_history(session_id: str):
    store = get_session_store()
    session = store.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"messages": session.messages}


@router.post("/{session_id}/confirm")
async def confirm_ticket(session_id: str, request: ConfirmRequest):
    service = get_chat_service()
    try:
        result = await service.confirm_and_create(
            session_id=session_id,
            template_id=request.template_id,
            fields=request.fields,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Jira 티켓 생성 중 오류가 발생했습니다: {str(e)}",
        )
