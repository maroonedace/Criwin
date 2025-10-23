import asyncio
import re
from pathlib import Path
from typing import Optional
from discord import Interaction, File
from src.commands.utils import send_message

from src.commands.yt_to_mp3 import download_clip, is_url_valid

# Global set to track active downloads per user
active_downloads: set[int] = set()

# Configuration constants
MAX_VIDEO_LENGTH = 5 * 60  # 5 minutes in seconds
LIMIT_DOWNLOAD_MESSAGE = '⚠️ You already have a download in progress.'
INVALID_URL_STRUCTURE_MESSAGE = '⚠️ Invalid URL structure: Only short or video share links are accepted.'

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
