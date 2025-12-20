from discord import Client, Interaction, InteractionCallbackResponse

from src.commands.constants import SUPPORTED_DOMAINS

async def send_message(interaction: Interaction, message: str) -> InteractionCallbackResponse[Client]:
    return await interaction.followup.send(message, ephemeral=True)


def is_supported_url(url: str) -> bool:
    """Check if the URL is from a supported domain."""
    return any(domain in url for domain in SUPPORTED_DOMAINS)