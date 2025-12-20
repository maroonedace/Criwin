from discord import app_commands, Interaction

from src.commands.download_video.setup import setup_download_video_command




def setup_download_video(tree: app_commands.CommandTree):
    """Setup YouTube related commands"""
    
    @tree.command(name="download-video", description="Download a video file (Limited to 30 seconds)")
    @app_commands.describe(url="Video URL")
    async def download_video(interaction: Interaction, url: str):
        await setup_download_video_command(interaction, url)