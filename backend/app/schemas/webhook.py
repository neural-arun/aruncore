from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class TelegramUpdate(BaseModel):
    update_id: int
    message: Optional[Dict[str, Any]] = None
    callback_query: Optional[Dict[str, Any]] = None


class ActiveLearningWebhookPayload(BaseModel):
    session_id: str
    user_question: str
    owner_answer: str
    tutor_id: Optional[str] = "arun"
