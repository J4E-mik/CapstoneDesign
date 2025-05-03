import os
import whisper
import tempfile
from gtts import gTTS
from datetime import datetime, timedelta

model = whisper.load_model("base")


# STT
async def transcribe_audio(audio_file) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp:
        content = await audio_file.read()
        temp.write(content)
        temp_path = temp.name

    result = model.transcribe(temp_path, language='ko')
    os.remove(temp_path)
    return result.get("text", "")


# TTS (현재 미사용)
def text_to_speech(text: str) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3", dir="static/voices", mode="wb") as temp:
        tts = gTTS(text=text, lang='ko')
        tts.save(temp.name)
        return temp.name
    

# 임시저장 파일 삭제
def cleanup_old_files(directory: str, expire_minutes: int = 10):
    now = datetime.now()
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path):
                created = datetime.fromtimestamp(os.path.getctime(file_path))
                if now - created > timedelta(minutes=expire_minutes):
                    os.remove(file_path)
        except Exception as e:
            print(f"파일 삭제 실패: {file_path}, 에러: {e}")