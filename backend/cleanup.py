"""Run with: python cleanup.py --hours 24 (cron or scheduled task)."""
import argparse
from pathlib import Path
from storage import cleanup_media

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--hours", type=float, default=24)
    args = parser.parse_args()
    directory = Path(__file__).resolve().parent / "media"
    directory.mkdir(exist_ok=True)
    deleted = cleanup_media(directory, args.hours)
    print(f"Deleted {len(deleted)} expired media files")
