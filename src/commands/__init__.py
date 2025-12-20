from src.commands.audio_converter import setup_audio_converter
from src.commands.download_image import setup_download_image
from src.commands.download_video import setup_download_video
from src.commands.leave import setup_leave
from src.commands.send_image import setup_send_image
from src.commands.send_video import setup_send_video
from src.commands.soundboard import setup_soundboard
from discord import app_commands


def setup_commands(tree: app_commands.CommandTree):
    setup_leave(tree)
    setup_audio_converter(tree)
    setup_download_video(tree)
    setup_download_image(tree)
    setup_send_image(tree)
    setup_send_video(tree)
    setup_soundboard(tree)

