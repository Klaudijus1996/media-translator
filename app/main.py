from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from pathlib import Path

import shutil
import uuid
import mimetypes
import logging

from app.config import settings
from app.domain.ports import SpeechToText, TextTranslator, TextToSpeech
from app.services.transcriber_openai import OpenAIWhisperTranscriber
from app.services.translator_openai import OpenAITextTranslator
from app.services.tts_openai import OpenAITTS
from app.services.media_mux import MediaMux
from app.utils.ffmpeg import (
    is_video, extract_audio, merge_video_with_audio, ensure_ffmpeg
)
from app.utils.logging_config import setup_logging

app = FastAPI(title="Media Translator POF", version="0.1.0")

DATA_DIR = Path(settings.DATA_DIR)
INPUT_DIR = DATA_DIR / "input"
OUT_DIR = DATA_DIR / "output"
for p in (INPUT_DIR, OUT_DIR):
    p.mkdir(parents=True, exist_ok=True)

setup_logging()
logger = logging.getLogger(__name__)

# Wiring (DIP) – could be swapped with different implementations
stt: SpeechToText = OpenAIWhisperTranscriber()
translator: TextTranslator = OpenAITextTranslator()
tts: TextToSpeech = OpenAITTS()
mux = MediaMux()

class Health(BaseModel):
    status: str

@app.get("/health", response_model=Health)
def health():
    ensure_ffmpeg()
    return {"status": "ok"}

@app.post("/translate")
async def translate(
    file: UploadFile = File(...),
    target_lang: str = Form(...),     # e.g. "en", "es", "de", "fr", "lt"
    voice: str = Form("alloy")        # OpenAI TTS voice hint; configurable
):
    ensure_ffmpeg()

    # Persist uploaded file
    job_id = str(uuid.uuid4())
    infile = INPUT_DIR / f"{job_id}_{file.filename}"
    with infile.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        # If video -> extract audio; if audio -> just use as-is
        if is_video(infile):
            audio_path = OUT_DIR / f"{job_id}_extracted.wav"
            extract_audio(infile, audio_path)
            work_audio = audio_path
        else:
            work_audio = infile

        # 1) ASR (transcribe to source text)
        #    If the target language is English, we can set "translate" in Whisper.
        #    For other targets, we do: transcribe -> text translate -> TTS.
        source_text = stt.transcribe(work_audio, translate_to_english=(target_lang.lower() == "en"))

        # Save transcription to file
        transcription_file = OUT_DIR / f"{job_id}_source.txt"
        transcription_file.write_text(source_text, encoding="utf-8")

        # 2) NMT (translate text to target language) – no-op if already in target
        text_out = translator.translate(source_text, target_lang=target_lang)
         # Save translation to file
        text_out_file = OUT_DIR / f"{job_id}_text_out.txt"
        text_out_file.write_text(text_out, encoding="utf-8")

        # 3) TTS (synthesize target language speech)
        dubbed_wav = OUT_DIR / f"{job_id}_dubbed.wav"
        tts.synthesize(text_out, dubbed_wav, voice=voice, language=target_lang)

        # 4) If original was video -> mux dubbed audio over muted video
        if is_video(infile):
            out_video = OUT_DIR / f"{job_id}_translated.mp4"
            merge_video_with_audio(infile, dubbed_wav, out_video)
            return FileResponse(
                path=out_video,
                media_type="video/mp4",
                filename=out_video.name,
            )
        else:
            # Audio in -> return dubbed audio out
            return FileResponse(
                path=dubbed_wav,
                media_type="audio/wav",
                filename=dubbed_wav.name,
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error during translation process")
        raise HTTPException(status_code=500, detail="Internal server error")
