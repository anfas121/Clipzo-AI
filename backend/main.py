"""Clipzo AI MVP API: local upload, candidate clips, vertical exports."""
from pathlib import Path
from uuid import uuid4
import json
import re
import shutil
import subprocess

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from highlights import rank_windows, audio_activity

app = FastAPI(title="Clipzo AI MVP")
MEDIA = Path(__file__).resolve().parent / "media"
MEDIA.mkdir(exist_ok=True)
MAX_BYTES = 250 * 1024 * 1024

def run(*args):
    try:
        return subprocess.run(args, check=True, capture_output=True, text=True, timeout=240).stdout
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as exc:
        raise HTTPException(422, f"Video processing failed: {str(exc)[:250]}") from exc

def duration(path):
    result = json.loads(run("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)))
    return float(result["format"]["duration"])

def video_path(video_id):
    if not re.fullmatch(r"[0-9a-f]{32}", video_id):
        raise HTTPException(400, "Invalid video ID")
    path = MEDIA / f"{video_id}.mp4"
    if not path.exists():
        raise HTTPException(404, "Video not found")
    return path

@app.get("/health")
def health():
    return {"status": "ok", "ffmpeg": shutil.which("ffmpeg") is not None}

@app.post("/videos")
async def upload(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("video/"):
        raise HTTPException(415, "Upload a video file")
    video_id = uuid4().hex
    path = MEDIA / f"{video_id}.mp4"
    total = 0
    try:
        with path.open("wb") as output:
            while chunk := await file.read(1024 * 1024):
                total += len(chunk)
                if total > MAX_BYTES:
                    raise HTTPException(413, "Maximum upload size is 250 MB")
                output.write(chunk)
        seconds = duration(path)
        if seconds <= 0:
            raise HTTPException(422, "Invalid video duration")
        return {"id": video_id, "duration": seconds}
    except Exception:
        path.unlink(missing_ok=True)
        raise
    finally:
        await file.close()

@app.get("/videos/{video_id}/suggestions")
def suggestions(video_id: str, clip_seconds: int = 30):
    path = video_path(video_id)
    length = duration(path)
    clip_seconds = max(5, min(60, clip_seconds))
    clips = rank_windows(length, clip_seconds, lambda start, span: audio_activity(path, start, span))
    return {"method": "audio_activity_heuristic", "ai_ranked": False,
            "note": "Louder sections are prioritized; this is not semantic AI highlight detection.",
            "clips": clips}

@app.get("/videos/{video_id}/export")
def export(video_id: str, start: float = 0, end: float = 30):
    source = video_path(video_id)
    length = duration(source)
    if not (0 <= start < end <= length + 0.01) or end - start > 60:
        raise HTTPException(400, "Choose a clip between 0 and 60 seconds")
    output = MEDIA / f"{video_id}_{int(start * 100)}_{int(end * 100)}.mp4"
    if not output.exists():
        run("ffmpeg", "-y", "-ss", str(start), "-i", str(source), "-t", str(end - start),
            "-vf", "scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "25", "-c:a", "aac",
            "-movflags", "+faststart", str(output))
    return FileResponse(output, media_type="video/mp4", filename="clipzo-short.mp4")
