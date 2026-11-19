"""Local media retention policy. Run periodically in a single-worker deployment."""
from pathlib import Path
import time

def cleanup_media(media_dir: Path, max_age_hours=24, now=None):
    if max_age_hours <= 0:
        raise ValueError("max_age_hours must be positive")
    now = time.time() if now is None else now
    threshold = now - max_age_hours * 3600
    removed = []
    for path in media_dir.iterdir():
        if not path.is_file() or path.is_symlink() or path.suffix.lower() not in {".mp4", ".srt"}:
            continue
        try:
            if path.stat().st_mtime < threshold:
                path.unlink()
                removed.append(path.name)
        except FileNotFoundError:
            pass
    return removed
