import asyncio
from pathlib import Path
from typing import Optional
from discord import Interaction, File, Member
from src.commands.download.constants import UNSUPPORTED_DOMAIN_MESSAGE, LIMIT_DOWNLOAD_MESSAGE
from src.commands.download.utils import video_downloader, is_supported_url
from src.commands.utils import send_message

async def setup_send_video(interaction: Interaction, active_downloads: set[int], url: str, member: Member) -> None:
    # Acknowledge the interaction and defer response
    await interaction.response.defer(ephemeral=True)
    
    if not is_supported_url(url):
        await send_message(interaction, UNSUPPORTED_DOMAIN_MESSAGE)
        return

    # Get user ID for download tracking
    user_id = interaction.user.id

    # Limit to one download at a time per user
    if user_id in active_downloads:
        await send_message(interaction, LIMIT_DOWNLOAD_MESSAGE)
        return

    # Add user to active downloads tracking
    active_downloads.add(user_id)

    # Initialize file_path for cleanup
    file_path: Optional[Path] = None

    try:
        file_path = await asyncio.to_thread(
            video_downloader, 
            url,
            True 
        )
        
        await send_message(interaction, f"Succesfully sent to {member}")
        await member.send(content=f" Sent by {interaction.user.display_name}", file=File(str(file_path)))

    except Exception as error:
        await send_message(interaction, str(error))
        
    finally:
        if file_path is not None:
             file_path.unlink(missing_ok=True)
        active_downloads.discard(user_id)