import os
from pathlib import Path
from yt_dlp import YoutubeDL

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
MAX_VIDEO_LENGTH = 4 * 60  # 4 minutes in seconds
NOT_VIDEO_MESSAGE = '⚠️ This is not a video.'
PLAYLIST_MESSAGE = '⚠️ This is a playlist.'
LIVE_STREAM_MESSAGE = '⚠️ This is a live stream.'
LONG_DURATION_MESSAGE = f'⚠️ Video is too long (maximum {MAX_VIDEO_LENGTH / 60} minutes).'
URL_INVALID_MESSAGE = '⚠️ This URL is invalid or the video could not be downloaded.'


def download_audio_file(url: str) -> Path:
    try:
        # Extract video metadata
        ydl = YoutubeDL(YTDL_META)
        video_info = ydl.extract_info(url, download=False)
        
        # Check 1: Ensure it's not a playlist
        if video_info.get("_type") == "playlist":
            raise ValueError(PLAYLIST_MESSAGE)
        
        
        # Check 2: Ensure it's not a live stream
        is_live = video_info.get("is_live", False)
        was_live = video_info.get("was_live", False)
        if is_live or was_live:
            raise ValueError(LIVE_STREAM_MESSAGE)
        
        # Multiple checks to confirm it's a video
        checks = [
            video_info.get("duration") is not None,  # Videos typically have duration
            video_info.get("width") is not None,     # Videos have width
            video_info.get("height") is not None,    # Videos have height
            len(video_info.get("formats", [])) > 0,  # Videos have formats
        ]
        
        is_video = any(checks)
        
        if not is_video:
            raise ValueError(NOT_VIDEO_MESSAGE)
        
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