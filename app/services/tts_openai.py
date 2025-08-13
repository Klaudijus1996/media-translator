from pathlib import Path
from app.domain.ports import TextToSpeech
from app.config import settings
from openai import OpenAI

class OpenAITTS(TextToSpeech):
    def __init__(self, model: str = "gpt-4o-mini-tts"):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = model

    def synthesize(self, text: str, out_path: Path, voice: str, language: str) -> None:
        # Create WAV output. (If MP3 preferred, adjust format and mux step accordingly.)
        resp = self.client.audio.speech.create(
            model=self.model,
            voice=voice,
            input=text,
        )
        audio_bytes = resp.read() if hasattr(resp, "read") else resp.content
        out_path.write_bytes(audio_bytes)
