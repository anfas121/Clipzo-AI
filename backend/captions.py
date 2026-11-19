"""Optional on-device/server Whisper transcription and caption helpers."""
from functools import lru_cache
import re

@lru_cache(maxsize=1)
def model():
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError("Transcription requires pip install -r requirements-ai.txt") from exc
    return WhisperModel("tiny", device="cpu", compute_type="int8")

def transcribe(path):
    segments, info = model().transcribe(str(path), vad_filter=True, beam_size=1)
    return {"language": info.language, "segments": [
        {"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()}
        for s in segments if s.text.strip()
    ]}

def score_speech(start, end, segments):
    """Simple speech density proxy, not a semantic AI highlight score."""
    words = 0
    for segment in segments:
        overlap = max(0, min(end, segment["end"]) - max(start, segment["start"]))
        duration = max(0.01, segment["end"] - segment["start"])
        words += len(segment["text"].split()) * overlap / duration
    return round(words / max(1, end - start), 3)

def timestamp(seconds):
    millis = max(0, round(seconds * 1000))
    h, rem = divmod(millis, 3600000)
    m, rem = divmod(rem, 60000)
    s, ms = divmod(rem, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def srt_for_clip(segments, start, end):
    lines = []
    for segment in segments:
        a = max(start, segment["start"])
        b = min(end, segment["end"])
        if a >= b:
            continue
        text = re.sub(r"[\\r\\n]+", " ", segment["text"]).strip()
        if text:
            lines.extend([str(len(lines) // 4 + 1), f"{timestamp(a-start)} --> {timestamp(b-start)}", text, ""])
    return "\\n".join(lines).replace("\\n", "\n")
