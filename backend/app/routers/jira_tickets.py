from fastapi import APIRouter, HTTPException

from app.dependencies import get_jira_service, get_template_service
from app.schemas.jira import JiraCreateRequest, JiraTicketResponse

router = APIRouter(prefix="/api/jira", tags=["jira"])


@router.post("/create", response_model=JiraTicketResponse)
async def create_ticket(request: JiraCreateRequest):
    jira = get_jira_service()
    templates = get_template_service()

    template = templates.get_template(request.template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")

    try:
        result = await jira.create_issue(
            issue_type=template.jira_issue_type, fields=request.fields
        )
        ticket_key = result.get("key", "")
        return JiraTicketResponse(
            key=ticket_key,
            url=f"{jira.base_url}/browse/{ticket_key}",
            summary=request.fields.get("summary", ""),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Jira 티켓 생성 실패: {str(e)}",
        )


@router.get("/ticket/{issue_key}")
async def get_ticket(issue_key: str):
    jira = get_jira_service()
    try:
        return await jira.get_issue(issue_key)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"티켓 조회 실패: {str(e)}"
        )
