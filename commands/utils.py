from discord import Client, Interaction, InteractionCallbackResponse

async def send_message(interaction: Interaction, message: str) -> InteractionCallbackResponse[Client]:
    return await interaction.response.send_message(message, ephemeral=True)