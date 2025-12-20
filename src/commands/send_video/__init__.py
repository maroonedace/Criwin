from discord import Member, app_commands, Interaction

from src.commands.send_video.setup import setup_send_video_command


def setup_send_video(tree: app_commands.CommandTree):
    """Setup YouTube related commands"""
    
    @tree.command(name="send-video", description="Send a video file (Limited to 30 seconds)")
    @app_commands.describe(url="Video URL")
    async def send_video(interaction: Interaction, url: str, member: Member):
        await setup_send_video_command(interaction, url, member)