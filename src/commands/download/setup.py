from discord import Interaction, app_commands

from src.commands.download.download_audio import setup_download_audio
from src.commands.download.download_media import setup_download_media

active_downloads: set[int] = set()


def setup_download(tree: app_commands.CommandTree):
    @tree.command(
        name="download-audio",
        description="Download audio from a URL",
    )
    @app_commands.describe(
        url="The URL to download audio from",
        is_visible="Make the download visible to others in the channel",
    )
    async def download_audio(interaction: Interaction, url: str, is_visible: bool = False):
        await setup_download_audio(interaction, active_downloads, url, is_visible)

    @tree.command(
        name="download-media",
        description="Download video or images from a URL",
    )
    @app_commands.describe(
        url="The URL to download media from",
        is_visible="Make the download visible to others in the channel",
    )
    async def download_media(interaction: Interaction, url: str, is_visible: bool = False):
        await setup_download_media(interaction, active_downloads, url, is_visible)