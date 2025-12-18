from src.commands.insta_download.setup import setup_insta_download
from src.commands.yt_to_mp3.setup import setup_yt_to_mp3
from src.commands.soundboard.setup import setup_soundboard
from .leave.leave import setup_leave
from discord import Interaction, app_commands

def setup_commands(tree: app_commands.CommandTree):
    setup_leave(tree)

    @tree.command(name="yt-to-mp3", description="Convert a Youtube video into an MP3 file.")
    @app_commands.describe(
        url="YouTube Share URL",
    )
    async def file(interaction: Interaction, url: str):
        await setup_yt_to_mp3(interaction, url)
        
    @tree.command(name="insta-download", description="Download an instagram reel or post.")
    @app_commands.describe(
        url="Instagram URL",
        is_visible="Make the download visible to others in the channel",
    )
    async def file(interaction: Interaction, url: str, is_visible: bool = False):
        await setup_insta_download(interaction, url, is_visible)
    
    setup_soundboard(tree)

