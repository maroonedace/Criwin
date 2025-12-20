from discord import Member, app_commands, Interaction

from src.commands.send_image.setup import setup_send_image_command


def setup_send_image(tree: app_commands.CommandTree):
    """Setup Instagram related commands"""
    
    @tree.command(name="send-image", description="Send an image to a user.")
    @app_commands.describe(
        url="Image URL",
        member="Member you are sending to"
    )
    async def send_image(interaction: Interaction, url: str, member: Member):
        await setup_send_image_command(interaction, url, member)