from fastapi import APIRouter, UploadFile, File, Form
from services.speech_service import transcribe_audio, text_to_speech, cleanup_old_files

router = APIRouter()
# 현재 미사용
@router.post("/stt")
async def speech_to_text(audio: UploadFile = File(...)):
    cleanup_old_files("static/voices")
    result = await transcribe_audio(audio)
    return {"transcribed_text": result}


@router.post("/tts")
async def text_to_voice(text: str = Form(...)):
    cleanup_old_files("static/voices")
    file_path = text_to_speech(text)
    return {"voice_path": file_path}