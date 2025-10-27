
from typing import List
from discord import Interaction, app_commands

from src.commands.soundboard.play_soundboard.file import setup_soundboard_play
from src.commands.soundboard.utils import autocomplete_sound_name

def setup_soundboard(tree: app_commands.CommandTree):
    @tree.command(name="soundboard", description="Play a sound in your voice channel.")
    @app_commands.describe(sound_name="Select a sound to play")
    async def soundboard_play(interaction: Interaction, sound_name: str):
        await setup_soundboard_play(interaction, sound_name)

    @soundboard_play.autocomplete("sound_name")
    async def sound_autocomplete(_interaction: Interaction, current: str) -> List[app_commands.Choice[str]]:
        return await autocomplete_sound_name(current)
