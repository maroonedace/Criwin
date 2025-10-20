from src.commands.yt_to_mp3.file import setup_yt_to_mp3
from src.commands.soundboard.file import setup_soundboard
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

    @tree.command(name="soundboard", description="Play a sound in your voice channel.")
    @app_commands.describe(sound_name="Select a sound to play")
    async def file(interaction: Interaction, sound_name: str):
        await setup_soundboard(interaction, sound_name)

