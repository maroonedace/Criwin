import re
from urllib.parse import parse_qs, urlparse
from discord import Interaction
from commands.utils import send_message
from yt_dlp import YoutubeDL

YOUTUBE_RE = re.compile(r'^https?://(?:www\.)?youtu\.be/(?P<id>[\w-]{11})(?:\?.*)?$', re.I)
SHORTS_RE = re.compile(r'^https?://(?:www\.|m\.)?youtube\.com/shorts/(?P<id>[\w-]{11})(?:\?.*)?$', re.I)

# yt-dlp configuration
YTDL_META = {
    "quiet": True, 
    "skip_download": True, 
    "noplaylist": True
}

active_downloads: set[int] = set()

LIMIT_DOWNLOAD_MESSAGE = '⚠️ You already have a download in progress.'
URL_MISMATCH_MESSAGE = '❌ Invalid URL: Only short or video share links are accepted.'
DURATION_INVALID_MESSAGE = '❌ Video duration is zero or invalid.'

async def setup_yt_to_mp3(
    interaction: Interaction, 
    url: str
):
    # Get user id
    user_id = interaction.user.id

    # Limit to one downloads at a time per user
    if user_id in active_downloads:
        await send_message(interaction, LIMIT_DOWNLOAD_MESSAGE)
        return
    
    # Ensure that url matches the expected Youtube share URL structure
    if not (YOUTUBE_RE.match(url) or SHORTS_RE.match(url)):
        await send_message(interaction, URL_MISMATCH_MESSAGE)
        return

    # Pull the video id from the url
    parsed = urlparse(url)
    video_id = parsed.path.strip("/").split("/")[-1]

    # # Construct canonical URL
    canonical_url = f"https://www.youtube.com/watch?v={video_id}"

    try:
        with YoutubeDL(YTDL_META) as ydl:
            video_info = ydl.extract_info(canonical_url, download=False)
    
    except Exception as e:
        await send_message(interaction, DURATION_INVALID_MESSAGE)
        return
        
    video_duration = int(video_info.get("duration"))

    active_downloads.add(user_id)
    


