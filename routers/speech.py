from fastapi import APIRouter, UploadFile, File, Depends
from services.speech_service import SpeechService
from schemas.schemas import SpeechTranscriptionResponse

router = APIRouter()


@router.post("/stt", response_model=SpeechTranscriptionResponse)
async def speech_to_text(
    audio_file: UploadFile = File(...),
    speech_service: SpeechService = Depends()
):
    transcription = await speech_service.transcribe_audio(audio_file)
    return {"transcription": transcription}
    