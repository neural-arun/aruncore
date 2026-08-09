import io
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from backend.app.schemas.voice import TTSRequest
from backend.app.services.voice_service import VoiceService

router = APIRouter()


@router.post("/tts")
@router.post("/api/v1/voice/tts")
async def tts_endpoint(req: TTSRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text snippet cannot be empty.")

    try:
        audio_bytes = VoiceService.generate_tts_audio(req.text, voice=req.voice or "alloy")
        return StreamingResponse(io.BytesIO(audio_bytes), media_type="audio/mpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
