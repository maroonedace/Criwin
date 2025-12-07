from src.commands.yt_to_mp3.file import setup_yt_to_mp3
from src.commands.soundboard.setup_soundboard import autocomplete_sound_name, setup_soundboard
from .leave import setup_leave
from discord import Interaction, app_commands

def setup_commands(tree: app_commands.CommandTree):
    setup_leave(tree)

    @tree.command(name="yt-to-mp3", description="Convert a Youtube video into an MP3 file.")
    @app_commands.describe(
        url="YouTube Share URL",
    )
    async def file(interaction: Interaction, url: str):
        await setup_yt_to_mp3(interaction, url)
    
    setup_soundboard(tree)

