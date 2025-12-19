from discord import app_commands, Interaction

from src.commands.audio_converter.setup import setup_audio_converter_command

def setup_audio_converter(tree: app_commands.CommandTree):
    """Setup YouTube related commands"""
    
    @tree.command(name="audio-converter", description="Convert a video into an audio file (Limited to 4 minutes)")
    @app_commands.describe(url="Video URL")
    async def audio_converter(interaction: Interaction, url: str):
        await setup_audio_converter_command(interaction, url)