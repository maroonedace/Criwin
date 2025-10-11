import re
from pathlib import Path
from typing import Optional, Tuple, Union
from urllib.parse import urlparse, parse_qs
from yt_dlp import YoutubeDL

# Constants
MAX_CLIP_SECONDS = 5 * 60
AUDIO_CODEC = "mp3"
AUDIO_QUALITY = "192"

# Download Directory
DOWNLOAD_DIR = Path("downloads")

# Regular expressions for URL validation
SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9 _.-]+")
YTD_BE_RE = re.compile(r'^https?://(?:www\.)?youtu\.be/(?P<id>[\w-]{11})(?:\?.*)?$', re.I)
SHORTS_RE = re.compile(r'^https?://(?:www\.|m\.)?youtube\.com/shorts/(?P<id>[\w-]{11})(?:\?.*)?$', re.I)

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
        "preferredcodec": AUDIO_CODEC, 
        "preferredquality": AUDIO_QUALITY
    }],
    "quiet": True, 
    "noplaylist": True,
}

# Parse the start time provided from the url
def parse_start_time(raw: str) -> Optional[int]:
    if not raw:
        return None
    
    sec = raw.rstrip('s')
    try:
        return int(sec)
    except ValueError:
        return None

# Ensure the URL matches the expected Youtube Share link structure
def validate_youtube_url(url: str) -> None:
    if not (YTD_BE_RE.match(url) or SHORTS_RE.match(url)):
        raise ValueError(
            "Only short or video share links are accepted "
            "(youtu.be/... or youtube.com/shorts/...)."
        )
    
# Pull the video id and start time from the url
def extract_youtube_url(url: str) -> Tuple[str, int]:
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    
    # Extract start time from query parameters
    start_time = 0
    if query_params.get("t"):
        query_param_start_time = parse_start_time(query_params["t"][0]) or 0
        start_time = max(0, query_param_start_time)
        
    # Extract and validate video ID
    video_id = parsed.path.strip("/").split("/")[-1]
    if not re.fullmatch(r"[\w-]{11}", video_id):
        raise ValueError("Invalid video ID format.")
    
    return video_id, start_time


def parse_ts(value: Optional[Union[str, int]]) -> Optional[int]:
    if value is None:
        return None
        
    # Handle string input
    parts = value.strip().split(":")
    if not parts or not all(p.isdigit() for p in parts):
        raise ValueError("Invalid time format. Use SS or MM:SS")
        
    parts = [int(p) for p in parts]
    
    # Parse time components
    if len(parts) == 1:
        mm, ss = 0, parts[0]
    elif len(parts) == 2:
        mm, ss = parts
    else:
        raise ValueError("Invalid time format. Use SS or MM:SS.")
        
    # Validate time values
    if ss >= 60 or mm >= 60 or min(mm, ss) < 0:
        raise ValueError("Invalid timestamp values.")
        
    return mm * 60 + ss

def fetch_info(url: str) -> dict:
    with YoutubeDL(YTDL_META) as ydl:
        return ydl.extract_info(url, download=False)

def sanitize_filename(name: str) -> str:
    """
    Sanitize a filename by removing invalid characters.
    
    Args:
        name (str): Original filename
        
    Returns:
        str: Sanitized filename
    """
    return SAFE_NAME_RE.sub("", name).strip()

def generate_output_path(outdir: Path, title: str, ext: str = ".mp3") -> Path:
    """
    Generate a safe output path for the audio file.
    
    Args:
        outdir (Path): Output directory
        title (str): File title
        ext (str): File extension
        
    Returns:
        Path: Safe output file path
    """
    filename = sanitize_filename(title)
    return outdir / f"{filename}{ext}"

def validate_clip_parameters(
    duration: int,
    start_time: int,
    clip_length: int,
) -> Tuple[int, int]:
    if start_time >= duration:
        raise ValueError("Start time is beyond the end of the video.")
        
    # Clamp clip length to maximum
    clip_length = min(clip_length, max_clip_seconds)
    
    # Adjust clip length if it exceeds video duration
    if start_time + clip_length > duration:
        clip_length = duration - start_time
        if clip_length <= 0:
            raise ValueError("No valid clip can be extracted with the given parameters.")
            
    return start_time, clip_length

def download_clip_mp3(
    canonical: str, 
    start_time: int, 
    provided_clip_length: Optional[int], 
    filename_opt: Optional[str]
) -> Path:
    try:
        # Fetch video metadata
        info = fetch_info(canonical)
        duration = int(info.get("duration") or 0)

        if duration <= 0:
            raise ValueError("Video duration is zero or invalid.")

        # Validate and adjust clip parameters
        if not provided_clip_length:
            provided_clip_length = MAX_CLIP_SECONDS

        clip_length = max(1, provided_clip_length)
        start_time, provided_clip_length = validate_clip_parameters(duration, start_time, clip_length)

        # Create output directory
        DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
        
        # Generate output path
        title = filename_opt or (info.get("title") or "clip")
        output_path = generate_output_path(DOWNLOAD_DIR, title)

        # Configure yt-dlp options
        ydl_opts = dict(YTDL_BASE)
        ydl_opts["outtmpl"] = str(output_path.with_suffix(".%(ext)s"))
        ydl_opts["postprocessor_args"] = ["-ss", str(start_time), "-t", str(provided_clip_length)]

        # Download the clip
        with YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(canonical, download=True)

        return output_path

    except Exception as e:
        raise RuntimeError(f"Failed to download clip: {str(e)}") from e