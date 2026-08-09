from fastapi import APIRouter
from backend.app.api.v1.config import router as config_router
from backend.app.api.v1.voice import router as voice_router
from backend.app.api.v1.webhook import router as webhook_router

api_v1_router = APIRouter()
api_v1_router.include_router(config_router)
api_v1_router.include_router(voice_router)
api_v1_router.include_router(webhook_router)
