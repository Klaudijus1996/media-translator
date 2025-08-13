from pathlib import Path
from app.config import settings
from app.domain.ports import SpeechToText
from openai import OpenAI
import os

class OpenAIWhisperTranscriber(SpeechToText):
    """
    Uses OpenAI audio.transcriptions. We ignore translate_to_english because
    the pipeline handles translation in TextTranslator.
    """
    def __init__(self, model: str | None = None):
        # Allow overriding via env; fall back to a widely supported model name.
        self.model = model or os.getenv("OPENAI_TRANSCRIBE_MODEL", "gpt-4o-transcribe")
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def transcribe(self, audio_path: Path, translate_to_english: bool = False) -> str:
        audio_file = audio_path.open("rb")
        resp = self.client.audio.transcriptions.create(
                file=audio_file,
                model=self.model,
                response_format="srt"
        )
        
        return resp
