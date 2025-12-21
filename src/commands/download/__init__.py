from discord import Interaction, Member, app_commands

from src.commands.download.download_audio import setup_download_audio
from src.commands.download.download_image import setup_download_image
from src.commands.download.download_video import setup_download_video
from src.commands.download.send_image import setup_send_image
from src.commands.download.send_video import setup_send_video

# Global set to track active downloads per user
active_downloads: set[int] = set()

def setup_download(tree: app_commands.CommandTree):
    @tree.command(name="download-audio", description="Convert a video into an audio file (Limited to 4 minutes)")
    @app_commands.describe(url="Video URL", is_visible="Make the download visible to others in the channel")
    async def download_audio(interaction: Interaction, url: str, is_visible: bool = False):
        await setup_download_audio(interaction, active_downloads, url, is_visible)
        
    @tree.command(name="download-image", description="Download an image from the provided url.")
    @app_commands.describe(url="Image URL", is_visible="Make the download visible to others in the channel")
    async def download_image(interaction: Interaction, url: str, is_visible: bool = False):
        await setup_download_image(interaction, active_downloads, url, is_visible)
    
    @tree.command(name="download-video", description="Download a video file (Limited to 30 seconds)")
    @app_commands.describe(url="Video URL", is_visible="Make the download visible to others in the channel")
    async def download_video(interaction: Interaction, url: str, is_visible: bool = False):
        await setup_download_video(interaction, active_downloads, url, is_visible)
        
    @tree.command(name="send-image", description="Download and send an image to the channel to a user")
    @app_commands.describe(url="Image URL", member="Member that will recieve image")
    async def send_image(interaction: Interaction, url: str, member: Member):
        await setup_send_image(interaction, active_downloads, url, member)
    
    @tree.command(name="send-video", description="Download and send a video to a user (Limited to 30 seconds)")
    @app_commands.describe(url="Video URL", member="Member that will recieve image")
    async def send_video(interaction: Interaction, url: str, member: Member):
        await setup_send_video(interaction, active_downloads, url, member)