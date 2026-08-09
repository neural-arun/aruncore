from typing import Optional
from fastapi import APIRouter
from backend.app.services.tenant_service import tenant_service

router = APIRouter()


@router.get("/config")
@router.get("/api/v1/config")
async def get_tutor_config_endpoint(tutor: Optional[str] = None):
    """Dynamic multi-tenant metadata resolution endpoint powering 1-click demos (?tutor=ed_donner)."""
    full_cfg = tenant_service.load_tenant_config(tutor)
    return full_cfg.to_legacy_dict()
