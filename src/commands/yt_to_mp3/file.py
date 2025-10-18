import asyncio
import re
from pathlib import Path
from typing import Optional
from discord import Interaction, File
from src.commands.utils import send_message
from yt_dlp import YoutubeDL

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
DOWNLOAD_DIR = Path("downloads")

# yt-dlp configuration
YTDL_META = {
    "quiet": True, 
    "skip_download": True, 
    "noplaylist": True
}

YTDL_BASE = {
    "format": "bestaudio/best",
    "postprocessors": [{
        "key": "FFmpegExtractAudio", 
        "preferredcodec": "mp3", 
        "preferredquality": 192
    }],
    "quiet": True, 
    "noplaylist": True,
}

# Global set to track active downloads per user
active_downloads: set[int] = set()

MAX_VIDEO_LENGTH = 5 * 60

# Configuration constants
MAX_VIDEO_LENGTH = 5 * 60  # 5 minutes in seconds
LIMIT_DOWNLOAD_MESSAGE = '⚠️ You already have a download in progress.'
INVALID_URL_STRUCTURE_MESSAGE = '⚠️ Invalid URL structure: Only short or video share links are accepted.'
FILE_INVALID_MESSAGE = '⚠️ Invalid Youtube URL.'
LONG_DURATION_MESSAGE = '⚠️ Video is too long (maximum 5 minutes).'

async def setup_yt_to_mp3(interaction: Interaction, url: str) -> None:
    """
    Convert a YouTube video to MP3 and send it to the user.
    
    Args:
        interaction: Discord interaction object
        url: YouTube video URL to convert
        
    Returns:
        None
    """

    # Acknowledge the interaction and defer response
    await interaction.response.defer(ephemeral=True)

    # Get user ID for download tracking
    user_id = interaction.user.id

    # Limit to one download at a time per user
    if user_id in active_downloads:
        await send_message(interaction, LIMIT_DOWNLOAD_MESSAGE)
        return
    
    # Validate URL structure - must match YouTube share URL patterns
    if not (is_url_valid(url)):
        await send_message(interaction, INVALID_URL_STRUCTURE_MESSAGE)
        return

    # Add user to active downloads tracking
    active_downloads.add(user_id)

    # Initialize file_path for cleanup
    file_path: Optional[Path] = None

    try:
        file_path = await asyncio.to_thread(
            download_clip, 
            url, 
        )
        
        # Send the MP3 file to the user
        await interaction.followup.send(
            file=File(str(file_path)), 
            ephemeral=True
        )

    except Exception as error:
        # Handle all download/conversion errors
        await send_message(interaction, str(error))
        
    finally:
        # Cleanup: remove temporary file and release download lock
        if file_path is not None:
             file_path.unlink(missing_ok=True)
        active_downloads.discard(user_id)


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
        with YoutubeDL(YTDL_META) as ydl:
            video_info = ydl.extract_info(url, download=False)
        
        # Extract video information
        title = video_info.get("title", "unknown")
        duration = int(video_info.get("duration", 0))

        # Check video duration limit
        if duration > MAX_VIDEO_LENGTH:
            raise ValueError(LONG_DURATION_MESSAGE)

        # Prepare download path
        output_path = DOWNLOAD_DIR / f"{title}.mp3"
        ydl_opts = dict(YTDL_BASE)
        ydl_opts["outtmpl"] = str(output_path.with_suffix(".%(ext)s"))

        # Download and convert the video to MP3
        with YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)
        
        return output_path
    
    except ValueError:
        # Re-raise validation errors (like duration limits)
        raise
        
    except Exception as error:
        raise ValueError(FILE_INVALID_MESSAGE) from error


def is_url_valid(url) -> bool:
    return (
        YOUTUBE_RE.match(url) or 
        YOUTUBE_SHORT_RE.match(url) or 
        YOUTUBE_SHORTENED_RE.match(url)
    )
