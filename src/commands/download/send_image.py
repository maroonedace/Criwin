import asyncio
from pathlib import Path
from typing import Optional
from discord import ButtonStyle, Interaction, File, Member
from discord.ui import View, Button
from src.commands.download.constants import UNSUPPORTED_DOMAIN_MESSAGE, LIMIT_DOWNLOAD_MESSAGE
from src.commands.download.utils import gallery_downloader, is_supported_url
from src.commands.utils import send_message

async def setup_send_image(interaction: Interaction, active_downloads: set[int], url: str, member: Member) -> None:
    # Acknowledge the interaction and defer response
    await interaction.response.defer(ephemeral=True)
    
    view = View(timeout=60)
    send_button = Button(
        label="Copy to clipboard", 
        style=ButtonStyle.primary, 
        emoji="📤"
    )
    view.add_item(send_button)
    
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
    
    image_urls = []

    try:
        file_path = await asyncio.to_thread(
            gallery_downloader, 
            url,
        )
        
        await send_message(interaction, f"Succesfully sent to {member}")
        message = await member.send(content=f" Sent by {interaction.user.display_name}", files=[File(str(f)) for f in file_path], view=view)
        if message.attachments:
            image_urls.append(message.attachments[0].url)
            
        print(image_urls)
        

    except Exception as error:
        await send_message(interaction, str(error))
        
    finally:
        for file in file_path:
            if file is not None:
                file.unlink(missing_ok=True)
        active_downloads.discard(user_id)