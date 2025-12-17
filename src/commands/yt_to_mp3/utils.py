import os
from pathlib import Path
from yt_dlp import YoutubeDL
import re

# Regular expressions for URL validation
YOUTUBE_RE = re.compile(
    r'^https?://(?:www\.|m\.)?youtube\.com/watch\?v=[A-Za-z0-9_-]{11}(?:[&#?][^#\s]*)*$', 
    re.I
)

YOUTUBE_SHORT_RE = re.compile(
    r'^https?://(?:www\.|m\.)?youtube\.com/shorts/[A-Za-z0-9_-]{11}(?:[&#?][^#\s]*)*$', 
    re.I
)

YOUTUBE_SHORTENED_RE = re.compile(
    r'^https?://youtu\.be/[A-Za-z0-9_-]{11}(?:[&#?][^#\s]*)*$', 
    re.I
)

# Download Directory
DOWNLOAD_DIR = str(Path.home() / "Downloads")

# yt-dlp configuration
YTDL_META = {
    "quiet": True, 
    "skip_download": True, 
    "noplaylist": True
}

YTDL_BASE = {
    "format": "bestaudio/best",
    'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
    "postprocessors": [{
        "key": "FFmpegExtractAudio", 
        "preferredcodec": "mp3",
        'preferredquality': '320',
    }],
    "quiet": True, 
    "noplaylist": True,
}

# Configuration constants
MAX_VIDEO_LENGTH = 5 * 60  # 5 minutes in seconds
LONG_DURATION_MESSAGE = '⚠️ Video is too long (maximum 5 minutes).'
URL_INVALID_MESSAGE = '⚠️ Invalid Youtube URL.'


def download_clip(url: str) -> Path:
    try:
        # Extract video metadata
        ydl = YoutubeDL(YTDL_META)
        video_info = ydl.extract_info(url, download=False)
        
        # Extract video information
        duration = int(video_info.get("duration", 0))

        # Check video duration limit
        if duration > MAX_VIDEO_LENGTH:
            raise ValueError(LONG_DURATION_MESSAGE)

        # Download and convert the video to an audio file
        ydl = YoutubeDL(YTDL_BASE)
        info = ydl.extract_info(url, download=True)
        downloaded_file_path = ydl.prepare_filename(info)
        
        base_name = os.path.splitext(downloaded_file_path)[0]
        downloaded_file_path = Path(f"{base_name}.mp3")
        
        return downloaded_file_path
    
    except ValueError:
        # Re-raise validation errors (like duration limits)
        raise
        
    except Exception as error:
        raise ValueError(URL_INVALID_MESSAGE) from error


def is_url_valid(url) -> bool:
    return (
        YOUTUBE_RE.match(url) or 
        YOUTUBE_SHORT_RE.match(url) or 
        YOUTUBE_SHORTENED_RE.match(url)
    )