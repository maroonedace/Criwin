import os
from pathlib import Path
import re
from yt_dlp import YoutubeDL
from typing import List, Union
from gallery_dl import config, job
from PIL import Image

from src.commands.constants import DOWNLOAD_DIR
from src.commands.download.constants import SUPPORTED_DOMAINS, VIDEO_EXTENSIONS

# yt-dlp configuration
YTDL_META = {"quiet": True, "skip_download": True, "noplaylist": True}

YTDL_AUDIO = {
    "format": "bestaudio/best",
    "outtmpl": os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s"),
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "128",
        }
    ],
    "quiet": True,
    "noplaylist": True,
}

YTDL_VIDEO = {
    "format": "best[height<=480]/bestvideo[height<=480]+bestaudio/best",
    "merge_output_format": "mp4",
    "outtmpl": os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s"),
    "quiet": True,
    "noplaylist": True,
}

# Configuration messages
NOT_VIDEO_MESSAGE = "⚠️ This is not a video."
PLAYLIST_MESSAGE = "⚠️ This is a playlist."
LIVE_STREAM_MESSAGE = "⚠️ This is a live stream."
URL_INVALID_MESSAGE = "⚠️ This URL is invalid or the video could not be downloaded."
UNSUPPORTED_URL_MESSAGE = "⚠️ This URL is not from a supported platform."


def is_file_too_large(file_path: str, max_size_mb: int):
    file_size_bytes = os.path.getsize(file_path)
    file_size_mb = file_size_bytes / (1024 * 1024)
    return file_size_mb > max_size_mb


def is_supported_url(url: str) -> bool:
    """Check if the URL is from a supported domain."""
    return any(domain in url for domain in SUPPORTED_DOMAINS)


def is_instagram_reel(url: str) -> bool:
    reel_pattern = r"https?://(?:www\.)?instagram\.com/reel/[^/\s]+/?"
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

        if is_video_download:
            # Download video
            ydl = YoutubeDL(YTDL_VIDEO)
            video_info = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(video_info)
            return Path(file_name)

        else:
            # Download audio
            ydl = YoutubeDL(YTDL_AUDIO)
            audio_info = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(audio_info)
            base_name = f"{os.path.splitext(file_name)[0]}.mp3"
            return Path(base_name)

    except ValueError:
        # Re-raise validation errors (like duration limits)
        raise

    except Exception as error:
        raise ValueError(URL_INVALID_MESSAGE) from error


def convert_to_png(file_path: Path) -> Path:
    try:
        # Open the image
        with Image.open(file_path) as img:
            stem = file_path.stem.rstrip(".")
            png_path = file_path.parent / f"{stem}.png"
            img.save(png_path, "PNG")
            return png_path

    except Exception as e:
        print(f"Failed to convert {file_path} to PNG: {e}")
        return None


def gallery_downloader(url: str) -> Union[List[Path], Path]:
    download_path = Path("downloads").resolve()
    download_path.mkdir(parents=True, exist_ok=True)

    # Load existing configuration
    config.load()

    # Set base directory
    config.set((), "base-directory", str(download_path))

    # Set extractor configuration
    config.set(
        ("extractor",),
        "instagram",
        {
            "cookies": "cookies.txt",
        },
    )

    try:
        download_job = job.DownloadJob(url)
        download_job.run()
    except Exception as error:
        raise ValueError(f"Failed to download {url}", error)

    downloaded_files = [f for f in download_path.rglob("*") if f.is_file()]
    
    if len(downloaded_files) == 1 and downloaded_files[0].suffix.lower() in VIDEO_EXTENSIONS:
        return downloaded_files[0]

    # Convert images to PNG
    converted_files = []
    for file_path in downloaded_files:
        # Skip conversion if already PNG
        if file_path.suffix.lower() == ".png":
            converted_files.append(file_path)
            continue
        
        png_path = convert_to_png(file_path)
        
        if png_path:
            converted_files.append(png_path)
            file_path.unlink()
        else:
            converted_files.append(file_path)

    return converted_files[::-1]
