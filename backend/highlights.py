"""Lightweight audio-activity highlight suggestions (heuristic, not ML)."""
import math
import re
import subprocess

def rank_windows(length, clip_seconds, sample_fn, limit=5):
    """Choose high-activity non-overlapping clips with deterministic ties."""
    span = min(float(clip_seconds), float(length))
    if span <= 0:
        return []
    if length <= span:
        return [{"start": 0.0, "end": round(length, 2), "score": 0.0}]
    step = max(span / 2, (length - span) / 23)
    count = min(24, math.ceil((length - span) / step) + 1)
    starts = sorted({round((length - span) * i / max(1, count - 1), 2) for i in range(count)})
    candidates = []
    for start in starts:
        try:
            score = float(sample_fn(start, span))
        except (ValueError, OSError, subprocess.SubprocessError):
            score = -100.0
        if not math.isfinite(score):
            score = -100.0
        candidates.append((score, start))
    chosen = []
    for score, start in sorted(candidates, key=lambda item: (-item[0], item[1])):
        if all(start + span <= other or other + span <= start for other in chosen):
            chosen.append(start)
        if len(chosen) == limit:
            break
    return [{"start": start, "end": round(min(length, start + span), 2),
             "score": round(next(s for s, t in candidates if t == start), 2)}
            for start in sorted(chosen)]

def audio_activity(path, start, span):
    """Mean volume in dB; louder audio is a rough proxy for activity."""
    proc = subprocess.run(
        ["ffmpeg", "-nostdin", "-hide_banner", "-ss", str(start), "-t", str(span),
         "-i", str(path), "-vn", "-af", "volumedetect", "-f", "null", "-"],
        capture_output=True, text=True, timeout=90, check=False)
    if proc.returncode != 0:
        return -100.0
    match = re.search(r"mean_volume:\s*(-?(?:\d+(?:\.\d+)?|inf))\s*dB", proc.stderr)
    if not match:
        return -100.0
    return float(match.group(1))
