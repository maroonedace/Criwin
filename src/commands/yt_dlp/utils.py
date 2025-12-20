import os
from pathlib import Path
from yt_dlp import YoutubeDL

from src.commands.constants import DOWNLOAD_DIR
from src.commands.utils import is_supported_url

# yt-dlp configuration
YTDL_META = {
    "quiet": True, 
    "skip_download": True, 
    "noplaylist": True
}

YTDL_AUDIO = {
    "format": "bestaudio/best",
    "outtmpl": os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
        "preferredquality": "320",
    }],
    "quiet": True,
    "noplaylist": True,
}

YTDL_VIDEO = {
    "format": "best[height<=480][ext=mp4]/best[height<=480]/best",
    "outtmpl": os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
    "quiet": True,
    "noplaylist": True,
}

# Configuration constants
MAX_AUDIO_DURATION = 4 * 60
MAX_VIDEO_DURATION = 30
NOT_VIDEO_MESSAGE = '⚠️ This is not a video.'
PLAYLIST_MESSAGE = '⚠️ This is a playlist.'
LIVE_STREAM_MESSAGE = '⚠️ This is a live stream.'
LONG_AUDIO_MESSAGE = f'⚠️ Audio video is too long (maximum {MAX_AUDIO_DURATION / 60} minutes).'
LONG_VIDEO_MESSAGE = f'⚠️ Video is too long for video download (maximum {MAX_VIDEO_DURATION} seconds).'
URL_INVALID_MESSAGE = '⚠️ This URL is invalid or the video could not be downloaded.'
UNSUPPORTED_URL_MESSAGE = '⚠️ This URL is not from a supported platform.'


def video_converter(url: str, is_video_download: bool) -> Path:
    if not is_supported_url(url):
        raise ValueError(UNSUPPORTED_URL_MESSAGE)
    
    try:
        # Extract video metadata
        ydl = YoutubeDL(YTDL_META)
        video_info = ydl.extract_info(url, download=False)
        
        # Ensure it's not a live stream
        is_live = video_info.get("is_live", False)
        was_live = video_info.get("was_live", False)
        if is_live or was_live:
            raise ValueError(LIVE_STREAM_MESSAGE)
        
        duration = int(video_info.get("duration", 0))
        
        if is_video_download:
            # Check video duration limit
            if duration > MAX_VIDEO_DURATION:
                raise ValueError(LONG_VIDEO_MESSAGE)    
            
            # Download video
            ydl = YoutubeDL(YTDL_VIDEO)
            info = ydl.extract_info(url, download=True)
            downloaded_file_path = ydl.prepare_filename(info)
            return Path(downloaded_file_path)

        else:
            # Check audio duration limit
            if duration > MAX_AUDIO_DURATION:
                raise ValueError(LONG_AUDIO_MESSAGE)    
            
            # Download audio
            ydl = YoutubeDL(YTDL_AUDIO)
            info = ydl.extract_info(url, download=True)
            downloaded_file_path = ydl.prepare_filename(info)
            base_name = os.path.splitext(downloaded_file_path)[0]
            return Path(f"{base_name}.mp3")
    
    except ValueError:
        # Re-raise validation errors (like duration limits)
        raise
        
    except Exception as error:
        raise ValueError(URL_INVALID_MESSAGE) from error