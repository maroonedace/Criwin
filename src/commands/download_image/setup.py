import asyncio
from pathlib import Path
from typing import Optional
from discord import Interaction, File
from src.commands.download_image.utils import (
    download_image,
)
from src.commands.utils import send_message

# Global set to track active downloads per user
active_downloads: set[int] = set()

# Configuration constants
LIMIT_DOWNLOAD_MESSAGE = "⚠️ You already have a download in progress."

async def setup_download_image_command(interaction: Interaction, url: str, is_visible: bool) -> None:
    # Acknowledge the interaction and defer response
    await interaction.response.defer(ephemeral=True)

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
            download_image,
            url,
        )
        
        channel = interaction.channel

        # Send the file to the user
        if is_visible:
            # Send public message to channel
            await channel.send(files=[File(str(f)) for f in file_path])
            # Optional: ephemeral confirmation to user
            await interaction.followup.send("Download sent to channel!", ephemeral=True)
        else:
            # Send ephemeral message to user
            await interaction.followup.send(files=[File(str(f)) for f in file_path], ephemeral=True)
        

    except Exception as error:
        # Handle all download/conversion errors
        await send_message(interaction, str(error))

    finally:
        for file in file_path:
            if file is not None:
                file.unlink(missing_ok=True)
        active_downloads.discard(user_id)
