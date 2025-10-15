import re
from typing import Optional
from discord import Interaction
from commands.utils import send_message

YTD_BE_RE = re.compile(r'^https?://(?:www\.)?youtu\.be/(?P<id>[\w-]{11})(?:\?.*)?$', re.I)
SHORTS_RE = re.compile(r'^https?://(?:www\.|m\.)?youtube\.com/shorts/(?P<id>[\w-]{11})(?:\?.*)?$', re.I)

# Ensure the URL matches the expected Youtube Share link structure
def validate_youtube_url(url: str) -> None:
    if not (YTD_BE_RE.match(url) or SHORTS_RE.match(url)):
        raise ValueError(
            "Only short or video share links are accepted "
            "(youtu.be/... or youtube.com/shorts/...)."
        )

active_downloads: set[int] = set()

async def setup_yt_to_mp3(
    interaction: Interaction, 
    url: str, 
    length: Optional[str] = None, 
    file_name: Optional[str] = None
):

    # Get user id
    user_id = interaction.user.id

    # Limit to one downloads at a time per user
    if user_id in active_downloads:
        await send_message(interaction, "⚠️ You already have a download in progress.")
        return
    
    active_downloads.add(user_id)

    # Ensure that url matches the expected Youtube share URL structure
    try:
        validate_youtube_url(url)
    except ValueError as ve:
        await send_message(interaction, f"❌ Invalid URL: {ve}")
        return

        


