from fastapi import APIRouter, UploadFile, File, Depends
from services.speech_service import SpeechService
from schemas.schemas import SpeechTranscriptionResponse
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/stt", response_model=SpeechTranscriptionResponse)
async def speech_to_text(
    audio_file: UploadFile = File(...),
    speech_service: SpeechService = Depends()
):
    transcription = await speech_service.transcribe_audio(audio_file)
    logger.info(f"변환 된 텍스트: {transcription}")
    return {"transcription": transcription}
    