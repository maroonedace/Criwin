from discord import app_commands, Interaction

from src.commands.download_image.setup import setup_download_image_command

def setup_download_image(tree: app_commands.CommandTree):
    """Setup Instagram related commands"""
    
    @tree.command(name="download-image", description="Download an image from the provided url.")
    @app_commands.describe(
        url="Image URL",
        is_visible="Make the download visible to others in the channel"
    )
    async def download_image(interaction: Interaction, url: str, is_visible: bool = False):
        await setup_download_image_command(interaction, url, is_visible)