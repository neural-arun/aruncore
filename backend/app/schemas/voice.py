from typing import Optional
from pydantic import BaseModel, Field


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000, description="Text snippet to synthesize into audio")
    voice: Optional[str] = Field("alloy", description="TTS voice identifier")
    tutor_id: Optional[str] = Field("arun", description="Optional tenant identifier")
