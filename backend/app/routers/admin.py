from fastapi import APIRouter, Header, HTTPException

from app.dependencies import get_settings, get_settings_service, reinit_services
from app.schemas.settings import (
    AdminSettingsResponse,
    AdminSettingsUpdate,
    VerifyPasswordRequest,
)

router = APIRouter(prefix="/api/admin", tags=["admin"])


def _check_password(password: str) -> None:
    settings = get_settings()
    if not settings.admin_password:
        raise HTTPException(status_code=500, detail="Admin password not configured")
    if password != settings.admin_password:
        raise HTTPException(status_code=403, detail="Invalid admin password")


@router.post("/verify")
async def verify_password(request: VerifyPasswordRequest):
    _check_password(request.password)
    return {"ok": True}


@router.get("/settings", response_model=AdminSettingsResponse)
async def get_admin_settings(x_admin_password: str = Header()):
    _check_password(x_admin_password)
    svc = get_settings_service()
    return AdminSettingsResponse(**svc.get_masked())


@router.put("/settings", response_model=AdminSettingsResponse)
async def update_admin_settings(
    body: AdminSettingsUpdate,
    x_admin_password: str = Header(),
):
    _check_password(x_admin_password)
    svc = get_settings_service()
    updates = body.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    new_effective = svc.update(updates)
    await reinit_services(new_effective)
    return AdminSettingsResponse(**svc.get_masked())
