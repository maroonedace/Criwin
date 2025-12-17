import os
from pathlib import Path
import gallery_dl
from yt_dlp import YoutubeDL
import re
from gallery_dl import job, config as gconfig

# Download Directory
DOWNLOAD_DIR = str(Path.home() / "Downloads")

YTDL_REEL_CONFIG = {
    "format": "bestvideo+bestaudio/best",
    'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
    "merge_output_format": "mp4",
    "prefer_ffmpeg": True,
    "quiet": True, 
    "noplaylist": True,
    "extract_flat": False,
}

# Configuration constants
MAX_VIDEO_LENGTH = 5 * 60  # 5 minutes in seconds
LONG_DURATION_MESSAGE = '⚠️ Video is too long (maximum 5 minutes).'
URL_INVALID_MESSAGE = '⚠️ Invalid Instagram URL.'

def is_post_url(url: str) -> bool:
    """Check if URL is an Instagram post (single image/video or carousel)"""
    if not url or not isinstance(url, str):
        return False
    
    pattern = r'^https?://(?:www\.)?instagram\.com/p/[A-Za-z0-9_-]+/?(\?.*)?$'
    return bool(re.match(pattern, url))

def is_reel_url(url: str) -> bool:
    """Check if URL is an Instagram reel (video)"""
    if not url or not isinstance(url, str):
        return False
    
    pattern = r'^https?://(?:www\.)?instagram\.com/reel/[A-Za-z0-9_-]+/?(\?.*)?$'
    return bool(re.match(pattern, url))

def get_instagram_type(url: str) -> str:
    """Get the type of Instagram content"""
    if is_post_url(url):
        return "post"
    elif is_reel_url(url):
        return "reel"
    else:
        return "invalid"

def download_post(url: str) -> Path:
    download_path = Path("downloads/posts").resolve()
    download_path.mkdir(parents=True, exist_ok=True)
    
    gconfig.clear()
    gconfig.load({
        "cookies-from-browser": "vivaldi",
        "base-directory": str(download_path),
        "directory": "{category}/{author}",
        "filename": "{title}_{num}.{extension}",
        "extractor": {
            "instagram": {
                 "cookies": "C:\Users\mexim\Documents\GitHub\Python-Discord-Bot\cookies.txt"
            }
        }
    })
    
    before = set(download_path.rglob("*"))
    
    try:
        job.DownloadJob(url).run()
    except Exception as e:
        raise RuntimeError(f"Download failed: {e}")

    after = set(download_path.rglob("*"))
    new_files = [p for p in after - before if p.is_file()]

    return new_files
    
def download_reel(url: str) -> Path:
    try:
        # Download the reel
        ydl = YoutubeDL(YTDL_REEL_CONFIG)
        info = ydl.extract_info(url, download=True)
        downloaded_file_path = ydl.prepare_filename(info)
        
        base_name = os.path.splitext(downloaded_file_path)[0]
        downloaded_file_path = Path(f"{base_name}.mp4")
        
        return downloaded_file_path
    
    except ValueError:
        # Re-raise validation errors (like duration limits)
        raise
        
    except Exception as error:
        raise ValueError(URL_INVALID_MESSAGE) from error