# 🎵 yt-music-downloader
(Interface in Spanish)

Downloads music from YouTube as MP3 with title, artist and cover art embedded.

## Requirements
- Python 3.8+
- FFmpeg
- A YouTube Data API v3 key ([get one here](https://console.cloud.google.com))

### Ubuntu/Debian
```bash
sudo apt install git python3 ffmpeg
```

### Termux (Android)
```bash
pkg install git python3 ffmpeg
termux-setup-storage
```

## Setup
```bash
git clone https://github.com/tuna-hub/yt-music-downloader
cd yt-music-downloader
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage
```bash
python3 descargador.py
```

Works with single videos and full playlists. Playlists get their own folder inside `musica/`. Already downloaded songs are skipped automatically. Artist is pulled from video metadata or channel name.
