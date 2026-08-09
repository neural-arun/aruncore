from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User input message text")
    session_id: str = Field(..., description="Unique session identifier")
    tutor_id: Optional[str] = Field("arun", description="Optional tenant or tutor ID")


class ChatMessageEntry(BaseModel):
    id: str
    sender: str
    name: str
    text: str
    timestamp: str
    thoughts: Optional[List[str]] = None


class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: List[ChatMessageEntry] = Field(default_factory=list)


class NDJSONStreamChunk(BaseModel):
    type: str = Field(..., description="'status', 'token', 'final', or 'error'")
    content: Optional[str] = None
    reply: Optional[str] = None
    thoughts: Optional[List[str]] = None
    session_id: Optional[str] = None
