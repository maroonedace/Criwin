from src.commands.insta_to_mp4.setup import setup_insta_to_mp4
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
        
    @tree.command(name="insta-to-mp4", description="Convert a Instagram reel into an MP4 file.")
    @app_commands.describe(
        url="Instagram reel URL",
    )
    async def file(interaction: Interaction, url: str):
        await setup_insta_to_mp4(interaction, url)
    
    setup_soundboard(tree)

