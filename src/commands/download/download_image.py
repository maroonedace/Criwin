import asyncio
from pathlib import Path
from typing import Optional
from discord import Interaction, File
from src.commands.download.constants import UNSUPPORTED_DOMAIN_MESSAGE, LIMIT_DOWNLOAD_MESSAGE, DOWNLOAD_SENT_TO_CHANNEL_MESSAGE
from src.commands.download.utils import gallery_downloader, is_supported_url
from src.commands.utils import send_message

async def setup_download_image(interaction: Interaction, active_downloads: set[int], url: str, is_visible: bool) -> None:
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
            gallery_downloader, 
            url,
        )
        
        channel = interaction.channel
        
        if is_visible:
            # Send public message to channel
            await channel.send(files=[File(str(f)) for f in file_path])
            await interaction.followup.send(DOWNLOAD_SENT_TO_CHANNEL_MESSAGE, ephemeral=True)
        else:
            # Send ephemeral message to user
            await interaction.followup.send(files=[File(str(f)) for f in file_path], ephemeral=True)

    except Exception as error:
        await send_message(interaction, str(error))
        
    finally:
        if file_path:
            for file in file_path:
                if file is not None:
                    file.unlink(missing_ok=True)
        active_downloads.discard(user_id)