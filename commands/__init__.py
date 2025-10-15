from typing import Optional

from commands.yt_to_mp3.file import setup_yt_to_mp3
from .leave import setup_leave
from .audioclip import setup_audioclip
from .soundboard import setup_soundboard
from discord import Interaction, app_commands

def setup_commands(tree: app_commands.CommandTree):
    setup_audioclip(tree)
    setup_soundboard(tree)
    setup_leave(tree)

    @tree.command()
    @app_commands.rename(yt_to_mp3='yttomp3')
    @app_commands.describe(
        url="YouTube Share URL",
        length="Clip length (SS or MM:SS). Max 5m.",
        file_name="Optional custom file name"
    )
    async def _(interaction: Interaction, 
        url: str, 
        length: Optional[str] = None, 
        file_name: Optional[str] = None):

        await setup_yt_to_mp3(interaction, url, length, file_name)

