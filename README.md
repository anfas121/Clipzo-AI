# Clipzo AI — Prototype

Expo React Native app + FastAPI/FFmpeg backend. Only process videos you own or are authorized to edit.

## Features
1. Upload local video (up to 250 MB).
2. Rank candidate 5–60-second clips by audio volume.
3. **Optional Whisper transcription** (faster-whisper tiny CPU model); speech-density sorting when a transcript exists.
4. Export captioned MP4s with burned-in SRT subtitles, or fetch SRT separately.
5. Preview/export via the phone's browser; exact save behavior varies by OS/browser.
6. Docker Compose development backend.

**Not yet included:** semantic AI highlight ranking, automatic YouTube downloads, integrated native video player, cloud-hosted backend, authentication, queueing, production-ready storage management, or verified APK/IPA. Transcripts are held in process memory and lost on restart. Initial Whisper model download requires network access and may take time.

## Run backend locally

Requires Python 3.11 and FFmpeg/ffprobe:

```bash
cd backend
pip install -r requirements-ai.txt
uvicorn main:app --host 127.0.0.1 --port 8000
```

For basic clipping without transcription, install `requirements.txt` instead.

Or run `docker compose up --build` from repo root; the included Compose config binds **only localhost** and installs optional AI dependencies. For mobile use, deploy behind an authenticated HTTPS gateway with upload limits, rate limiting, and private storage. Do **not** expose this unauthenticated API directly to the internet.

## Mobile

```bash
cd app
npm install
npx expo start
```

Set the Backend URL to a reachable server; the default IP is only an example. Upload a video, generate suggestions, optionally transcribe, then preview/export. Subtitle rendering requires FFmpeg compiled with the subtitles/libass filter.

## Validation

```bash
cd backend
python -m unittest test_highlights.py test_captions.py
```

GitHub Actions validates Python and Expo configuration. Android APK builds use the separate manual GitHub Actions / Expo EAS workflow and require a valid EXPO_TOKEN and initialized signing credentials. A green GitHub submission does **not** mean the EAS APK build is finished.

## Security and operational limitations

This is an MVP, not a production service. There is no user authentication, file cleanup, malware scanning, content moderation, or job queue. Local video files and generated clips persist in `backend/media`. Keep the service private until these safeguards are implemented. Avoid uploading copyrighted or private content without authorization.
