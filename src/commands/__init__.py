from src.commands.yt_to_mp3.file import setup_yt_to_mp3
from .leave import setup_leave
from .audioclip import setup_audioclip
from .soundboard import setup_soundboard
from discord import Interaction, app_commands

def setup_commands(tree: app_commands.CommandTree):
    setup_audioclip(tree)
    setup_soundboard(tree)
    setup_leave(tree)

    @tree.command(name="yt-to-mp3", description="Convert a Youtube video into an MP3 file.")
    @app_commands.describe(
        url="YouTube Share URL",
    )
    async def file(interaction: Interaction, url: str):
        await setup_yt_to_mp3(interaction, url)

