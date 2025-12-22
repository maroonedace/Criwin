import asyncio
from pathlib import Path
from typing import Optional
from discord import Interaction, File
from src.commands.download.constants import BOOST_LEVEL_UPLOAD_SIZE, DOWNLOAD_SENT_TO_CHANNEL_MESSAGE, LARGE_FILE_MESSAGE, UNSUPPORTED_DOMAIN_MESSAGE, LIMIT_DOWNLOAD_MESSAGE
from src.commands.download.utils import is_file_too_large, is_supported_url, video_downloader
from src.commands.utils import send_message

async def setup_download_audio(interaction: Interaction, active_downloads: set[int], url: str, is_visible: bool) -> None:
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
            False 
        )
        
        max_size_mb = BOOST_LEVEL_UPLOAD_SIZE.get(interaction.guild.premium_tier, 10)
        is_file_large = is_file_too_large(str(file_path), max_size_mb)
        
        if is_file_large:
            raise ValueError(LARGE_FILE_MESSAGE)
        
        channel = interaction.channel
        
        if is_visible:
            # Send public message to channel
            await channel.send(file=File(str(file_path)))
            await interaction.followup.send(DOWNLOAD_SENT_TO_CHANNEL_MESSAGE, ephemeral=True)
        else:
            # Send ephemeral message to user
            await interaction.followup.send(file=File(str(file_path)), ephemeral=True)

    except Exception as error:
        await send_message(interaction, str(error))
        
    finally:
        active_downloads.discard(user_id)
        if file_path is not None:
             file_path.unlink(missing_ok=True)
