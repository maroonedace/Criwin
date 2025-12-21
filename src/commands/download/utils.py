import os
from pathlib import Path
import re
from yt_dlp import YoutubeDL
from typing import List
from gallery_dl import config, job
from PIL import Image
import mimetypes

from src.commands.constants import DOWNLOAD_DIR
from src.commands.download.constants import MAX_AUDIO_LENGTH, MAX_VIDEO_LENGTH, SUPPORTED_DOMAINS

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

# Configuration messages
NOT_VIDEO_MESSAGE = '⚠️ This is not a video.'
PLAYLIST_MESSAGE = '⚠️ This is a playlist.'
LIVE_STREAM_MESSAGE = '⚠️ This is a live stream.'
LONG_AUDIO_MESSAGE = f'⚠️ Audio video is too long (maximum {MAX_VIDEO_LENGTH / 60} minutes).'
LONG_VIDEO_MESSAGE = f'⚠️ Video is too long for video download (maximum {MAX_AUDIO_LENGTH} seconds).'
URL_INVALID_MESSAGE = '⚠️ This URL is invalid or the video could not be downloaded.'
UNSUPPORTED_URL_MESSAGE = '⚠️ This URL is not from a supported platform.'

def is_supported_url(url: str) -> bool:
    """Check if the URL is from a supported domain."""
    return any(domain in url for domain in SUPPORTED_DOMAINS)

def is_instagram_reel(url: str) -> bool: 
    reel_pattern = r'https?://(?:www\.)?instagram\.com/reel/[^/\s]+/?'
    return bool(re.match(reel_pattern, url))

def video_downloader(url: str, is_video_download: bool) -> Path:
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
            if duration > MAX_VIDEO_LENGTH:
                raise ValueError(LONG_VIDEO_MESSAGE)    
            
            # Download video
            ydl = YoutubeDL(YTDL_VIDEO)
            info = ydl.extract_info(url, download=True)
            downloaded_file_path = ydl.prepare_filename(info)
            return Path(downloaded_file_path)

        else:
            # Check audio duration limit
            if duration > MAX_AUDIO_LENGTH:
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
    
def convert_to_png(file_path: Path) -> Path:
    try:
        # Open the image
        with Image.open(file_path) as img:
            png_path = file_path.with_suffix('.png')
            img.save(png_path, 'PNG')
            return png_path
        
    except Exception as e:
        print(f"Failed to convert {file_path} to PNG: {e}")
        return None

def gallery_downloader(url: str) -> List[Path]:
    download_path = Path("downloads").resolve()
    download_path.mkdir(parents=True, exist_ok=True)

    # Load existing configuration
    config.load()

    # Set base directory
    config.set((), "base-directory", str(download_path))
    
    # Set extractor configuration
    config.set(("extractor",), "instagram", {
        "cookies": "cache/cookies.txt",
    })

    try:
        download_job = job.DownloadJob(url)
        download_job.run()
    except Exception as error:
        raise ValueError(f"Failed to download {url}", error)

    downloaded_files = [f for f in download_path.rglob("*") if f.is_file()]
    
    # Convert images to PNG
    converted_files = []
    for file_path in downloaded_files:
        png_path = convert_to_png(file_path)
        if png_path:
            converted_files.append(png_path)
            file_path.unlink()
        else:
            converted_files.append(file_path)
    
    return converted_files[::-1]