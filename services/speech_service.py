import whisper, tempfile, os
from schemas.schemas import SpeechTranscriptionResponse

class SpeechService:
    def __init__(self):
        self.model = whisper.load_model("base")

    async def transcribe_audio(self, audio_file) -> str:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp:
            temp.write(await audio_file.read())
            temp_path = temp.name
        
        result = self.model.transcribe(temp_path, language='ko')
        os.remove(temp_path)
        return result.get("text","")