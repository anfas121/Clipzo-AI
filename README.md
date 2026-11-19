# Clipzo AI — MVP

Expo React Native mobile app and FastAPI/FFmpeg video clipping backend.

## Current functionality
- Select local video on iOS/Android and upload to the backend (250 MB limit)
- Suggest up to five evenly spaced 30-second segments (**not AI-ranked yet**)
- Export 9:16 720x1280 MP4 clips up to 60 seconds

## Backend
Requires Python 3.10+, ffmpeg and ffprobe installed on the server.

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Mobile app
Requires Node.js 20+ and Expo tooling.

```bash
cd app
npm install
npx expo start
```

Set the Backend URL in the app to an address reachable from your phone. For remote access deploy the backend with HTTPS. The example LAN IP is only a placeholder.

## Next steps
Add AI transcription/highlight ranking, subtitles, asynchronous processing, authentication, storage lifecycle and cloud deployment. The current API stores files on local disk and is **not safe to expose publicly** without access controls. Upload only videos you own or have permission to edit. No APK/IPA has been built yet.
