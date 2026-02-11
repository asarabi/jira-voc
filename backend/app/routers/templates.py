from fastapi import APIRouter, HTTPException

from app.schemas.template import JiraTemplate, TemplateSummary
from app.dependencies import get_template_service

router = APIRouter(prefix="/api/templates", tags=["templates"])


@router.get("", response_model=list[TemplateSummary])
async def list_templates():
    service = get_template_service()
    return service.get_summaries()


@router.get("/{template_id}", response_model=JiraTemplate)
async def get_template(template_id: str):
    service = get_template_service()
    template = service.get_template(template_id)
    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")
    return template
