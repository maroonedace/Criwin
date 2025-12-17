import asyncio
from pathlib import Path
from typing import Optional
from discord import Interaction, File
from src.commands.insta_to_mp4.utils import (
    download_post,
    download_reel,
    get_instagram_type,
)
from src.commands.utils import send_message

# Global set to track active downloads per user
active_downloads: set[int] = set()

# Configuration constants
MAX_VIDEO_LENGTH = 5 * 60  # 5 minutes in seconds
LIMIT_DOWNLOAD_MESSAGE = "⚠️ You already have a download in progress."
INVALID_URL_STRUCTURE_MESSAGE = (
    "⚠️ Invalid URL structure: Only reel or post links are accepted."
)

async def setup_insta_to_mp4(interaction: Interaction, url: str) -> None:
    # Acknowledge the interaction and defer response
    await interaction.response.defer(ephemeral=True)

    # Get user ID for download tracking
    user_id = interaction.user.id

    content_type = get_instagram_type(url)

    # Limit to one download at a time per user
    if user_id in active_downloads:
        await send_message(interaction, LIMIT_DOWNLOAD_MESSAGE)
        return

    # Validate URL structure - must match Instagram URL patterns
    if content_type == "invalid":
        await send_message(interaction, INVALID_URL_STRUCTURE_MESSAGE)
        return

    # Add user to active downloads tracking
    active_downloads.add(user_id)

    # Initialize file_path for cleanup
    file_path: Optional[Path] = None

    if content_type == "post":
        try:
            file_path = await asyncio.to_thread(
                download_post,
                url,
            )

            # Send the file to the user
            await interaction.followup.send(files=[File(str(f)) for f in file_path], ephemeral=True)

        except Exception as error:
            # Handle all download/conversion errors
            await send_message(interaction, str(error))

        finally:
            for file in file_path:
                if file is not None:
                    file.unlink(missing_ok=True)
            active_downloads.discard(user_id)

    else:
        try:
            file_path = await asyncio.to_thread(
                download_reel,
                url,
            )

            # Send the file to the user
            await interaction.followup.send(file=File(str(file_path)), ephemeral=True)

        except Exception as error:
            # Handle all download/conversion errors
            await send_message(interaction, str(error))

        finally:
            # Cleanup: remove temporary file and release download lock
            if file_path is not None:
                file_path.unlink(missing_ok=True)
            active_downloads.discard(user_id)
