from discord import app_commands, Interaction

from src.commands.instagram.setup import setup_insta_download

def setup_instagram_commands(tree: app_commands.CommandTree):
    """Setup Instagram related commands"""
    
    @tree.command(name="insta-download", description="Download an instagram reel or post.")
    @app_commands.describe(
        url="Instagram URL",
        is_visible="Make the download visible to others in the channel"
    )
    async def insta_download(interaction: Interaction, url: str, is_visible: bool = False):
        await setup_insta_download(interaction, url, is_visible)