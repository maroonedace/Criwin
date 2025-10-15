from typing import Optional
from discord import Interaction
from commands.utils import send_message

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
    
    active_downloads.add(user_id)

        


