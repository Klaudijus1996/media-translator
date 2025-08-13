from app.domain.ports import TextTranslator
from app.config import settings
from openai import OpenAI
import os

_SYS = (
    "You are a professional translator. "
    "Translate the user's text to the requested target language. "
    "Preserve meaning and tone. Return only the translation."
)

class OpenAITextTranslator(TextTranslator):
    def __init__(self, model: str | None = None):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = model or os.getenv("OPENAI_TRANSLATE_MODEL", "whisper-1")

    def translate(self, text: str, target_lang: str) -> str:
        # If user already requested English via Whisper translate, model may already be English.
        # We still pass through here to allow target_lang != 'en'.
        msg = [
            {"role": "system", "content": _SYS},
            {"role": "user", "content": f"Target language: {target_lang}\n\nText:\n{text}"}
        ]
        resp = self.client.chat.completions.create(model=self.model, messages=msg, temperature=0)
        return resp.choices[0].message.content.strip()
