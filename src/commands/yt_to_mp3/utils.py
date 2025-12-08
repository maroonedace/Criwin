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

# yt-dlp configuration
YTDL_META = {
    "quiet": True, 
    "skip_download": True, 
    "noplaylist": True
}

YTDL_BASE = {
    "format": "bestaudio/best",
    "quiet": True, 
    "noplaylist": True,
}

# Configuration constants
MAX_VIDEO_LENGTH = 5 * 60  # 5 minutes in seconds
LONG_DURATION_MESSAGE = '⚠️ Video is too long (maximum 5 minutes).'
URL_INVALID_MESSAGE = '⚠️ Invalid Youtube URL.'

# Download Directory
DOWNLOAD_DIR = Path("downloads")

def download_clip(url: str) -> Path:
    """
    Download and convert a YouTube video to MP3 in a separate thread.
    
    Args:
        url: YouTube video URL
        
    Returns:
        Path to the downloaded MP3 file
        
    Raises:
        ValueError: For validation errors (duration)
        Exception: For download/conversion errors
    """
    try:
        # Extract video metadata
        ydl = YoutubeDL(YTDL_META)
        video_info = ydl.extract_info(url, download=False)
        
        # Extract video information
        title = video_info.get("title", "unknown")
        duration = int(video_info.get("duration", 0))

        # Check video duration limit
        if duration > MAX_VIDEO_LENGTH:
            raise ValueError(LONG_DURATION_MESSAGE)
        
        # Get the extension of the best audio format
        audio_ext = video_info.get("ext", "mp3")  # fallback to mp3
        if "audio_ext" in video_info:
            audio_ext = video_info["audio_ext"]

        # Prepare download path
        output_path = DOWNLOAD_DIR / f"{title}.{audio_ext}"
        ydl_opts = dict(YTDL_BASE)
        ydl_opts["outtmpl"] = str(output_path)

        # Download and convert the video to MP3
        ydl = YoutubeDL(ydl_opts)
        ydl.extract_info(url, download=True)
        
        return output_path
    
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