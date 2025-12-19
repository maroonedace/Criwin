from src.commands.instagram import setup_instagram_commands
from src.commands.leave import setup_leave
from src.commands.youtube import setup_youtube_commands
from src.commands.soundboard.setup import setup_soundboard
from discord import app_commands

def setup_commands(tree: app_commands.CommandTree):
    setup_leave(tree)
    setup_youtube_commands(tree)
    setup_instagram_commands(tree)
    setup_soundboard(tree)

