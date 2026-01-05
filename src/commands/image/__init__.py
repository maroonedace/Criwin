from discord import Interaction, app_commands
from src.commands.image.setup import handle_image
from src.commands.leave.setup import handle_leave

def setup_image(tree: app_commands.CommandTree):
    """Setup the leave command"""
    
    @tree.command(name="image", description="Upload a photo to this")
    async def leave(interaction: Interaction):
        await handle_image(interaction)