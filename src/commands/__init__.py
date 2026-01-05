from src.commands.download import setup_download
from src.commands.image import setup_image
from src.commands.leave import setup_leave
from src.commands.soundboard import setup_soundboard
from discord import app_commands

def setup_commands(tree: app_commands.CommandTree):
    setup_soundboard(tree)
    setup_download(tree)
    setup_image(tree)
    setup_leave(tree)

    @tree.command(name="yt-to-mp3", description="Convert a Youtube video into an MP3 file.")
    @app_commands.describe(
        url="YouTube Share URL",
    )
    async def file(interaction: Interaction, url: str):
        await setup_yt_to_mp3(interaction, url)
    
    setup_soundboard(tree)
    setup_download(tree)
    setup_leave(tree)
