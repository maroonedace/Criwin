from discord import Interaction


async def setup_soundboard(interaction: Interaction, sound_name: str):
     # Acknowledge the interaction and defer response
    await interaction.response.defer(ephemeral=True)

    