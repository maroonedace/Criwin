from discord import app_commands, Interaction

from src.commands.youtube.setup import setup_yt_to_mp3

def setup_youtube_commands(tree: app_commands.CommandTree):
    """Setup YouTube related commands"""
    
    @tree.command(name="yt-to-mp3", description="Convert a Youtube video into an MP3 file.")
    @app_commands.describe(url="YouTube Share URL")
    async def yt_to_mp3(interaction: Interaction, url: str):
        await setup_yt_to_mp3(interaction, url)