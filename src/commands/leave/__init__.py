from discord import Interaction, app_commands
from src.commands.leave.setup import handle_leave

def setup_leave(tree: app_commands.CommandTree):
    """Setup the leave command"""
    
    @tree.command(name="leave", description="Kick the bot from your voice channel.")
    async def leave(interaction: Interaction):
        await handle_leave(interaction)