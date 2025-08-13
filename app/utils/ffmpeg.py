import subprocess
from pathlib import Path
import shutil
import mimetypes

def ensure_ffmpeg():
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg not found in PATH")

def is_video(p: Path) -> bool:
    # crude sniff – rely on mimetypes; override if needed
    mtype, _ = mimetypes.guess_type(str(p))
    return (mtype or "").startswith("video")

def run_ffmpeg(args: list[str]) -> None:
    proc = subprocess.run(["ffmpeg", "-y", *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.decode("utf-8", errors="ignore"))

def extract_audio(in_video: Path, out_wav: Path) -> None:
    # 16kHz mono PCM for ASR/TTS friendliness
    run_ffmpeg(["-i", str(in_video), "-vn", "-ac", "1", "-ar", "16000", "-f", "wav", str(out_wav)])

def merge_video_with_audio(in_video: Path, in_wav: Path, out_video: Path) -> None:
    # keep original video stream; replace audio; truncate to shortest
    run_ffmpeg(["-i", str(in_video), "-i", str(in_wav), "-c:v", "copy", "-map", "0:v:0", "-map", "1:a:0", "-shortest", str(out_video)])
