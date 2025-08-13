# Media Translator POF

Tiny service that:

1. Accepts an audio or video file.
2. Translates & dubs it into a target language.
3. Returns the dubbed audio, or re-muxed video with the dubbed audio track.

## Stack

- FastAPI
- ffmpeg (extract/mux)
- OpenAI (ASR: Whisper-like, NMT: chat, TTS: speech)
- Docker + Compose
- SOLID-ish with small ports (interfaces) for STT/NMT/TTS

## Run

```bash
cp .env.example .env   # add your OPENAI_API_KEY
make build
make dev
```

## Stop

```bash
make stop
```
