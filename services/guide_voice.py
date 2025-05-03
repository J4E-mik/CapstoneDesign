from gtts import gTTS
from datetime import datetime
from typing import List
import os

VOICE_DIR = "static/voices"

def ensure_voice_dir():
    os.makedirs(VOICE_DIR, exist_ok=True)

def guide_messages_to_voice(guides: List[str]) -> List[str]:
    ensure_voice_dir()
    voice_files = []

    for idx, guide in enumerate(guides):
        filename = f"guide_{datetime.now().strftime('%Y%m%d%H%M%S')}_{idx}.mp3"
        path = os.path.join(VOICE_DIR, filename)
        tts = gTTS(text=guide, lang='ko')
        tts.save(path)
        voice_files.append(path)
    
    return voice_files

def voice_steps_to_files(step_list: List[dict]) -> List[str]:
    ensure_voice_dir()
    voice_paths = []

    for step in step_list:
        text = step["text"]
        filename = f"walk_leg{step['leg_idx']}_step{step['step_idx']}_{datetime.now().strftime('%H%M%S')}.mp3"
        path = os.path.join(VOICE_DIR, filename)

        tts = gTTS(text=text, lang='ko')
        tts.save(path)
        voice_paths.append(path)

    return voice_paths