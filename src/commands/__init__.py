from src.commands.download_image import setup_download_image
from src.commands.leave import setup_leave
from src.commands.soundboard import setup_soundboard
from src.commands.audio_converter import setup_audio_converter
from discord import app_commands

def setup_commands(tree: app_commands.CommandTree):
    setup_leave(tree)
    setup_audio_converter(tree)
    setup_download_image(tree)
    setup_soundboard(tree)

