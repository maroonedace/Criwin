from src.commands.instagram import setup_instagram_commands
from src.commands.leave import setup_leave
from src.commands.soundboard import setup_soundboard
from src.commands.audio_converter import setup_audio_converter
from discord import app_commands

def setup_commands(tree: app_commands.CommandTree):
    setup_leave(tree)
    setup_audio_converter(tree)
    setup_instagram_commands(tree)
    setup_soundboard(tree)

