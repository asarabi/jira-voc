import logging

from fastapi import APIRouter, Request

from app.dependencies import get_ai_service, get_jira_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


@router.post("/jira")
async def handle_jira_webhook(request: Request):
    payload = await request.json()
    event = payload.get("webhookEvent", "")

    logger.info("Received Jira webhook event: %s", event)

    if event == "jira:issue_created":
        issue = payload.get("issue", {})
        issue_key = issue.get("key")

        if not issue_key:
            return {"status": "ignored", "reason": "no issue key"}

        jira = get_jira_service()
        ai = get_ai_service()

        try:
            full_issue = await jira.get_issue(issue_key)
            analysis = await ai.analyze_ticket(full_issue)
            await jira.add_comment(issue_key, analysis)
            logger.info("AI analysis posted as comment on %s", issue_key)
        except Exception:
            logger.exception("Failed to analyze ticket %s", issue_key)

    return {"status": "ok"}
