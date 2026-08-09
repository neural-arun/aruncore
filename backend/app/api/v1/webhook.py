from fastapi import APIRouter, HTTPException
from backend.app.schemas.webhook import ActiveLearningWebhookPayload
from backend.app.services.active_learning_service import ActiveLearningService

router = APIRouter()


@router.post("/webhook/telegram")
@router.post("/api/v1/webhook")
async def telegram_webhook_endpoint(payload: ActiveLearningWebhookPayload):
    try:
        active_learning = ActiveLearningService(tenant_id=payload.tutor_id or "arun")
        success = active_learning.process_incoming_owner_reply(
            session_id=payload.session_id,
            question=payload.user_question,
            answer=payload.owner_answer,
        )
        return {"status": "success" if success else "failed", "session_id": payload.session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
