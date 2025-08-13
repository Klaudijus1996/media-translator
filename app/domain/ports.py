from pathlib import Path
from abc import ABC, abstractmethod

class SpeechToText(ABC):
    @abstractmethod
    def transcribe(self, audio_path: Path, translate_to_english: bool = False) -> str:
        ...

class TextTranslator(ABC):
    @abstractmethod
    def translate(self, text: str, target_lang: str) -> str:
        ...

class TextToSpeech(ABC):
    @abstractmethod
    def synthesize(self, text: str, out_path: Path, voice: str, language: str) -> None:
        ...
