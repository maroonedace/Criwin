from unittest.mock import AsyncMock, MagicMock, Mock, patch
from discord import Interaction, InteractionCallbackResponse
import pytest

from src.commands.utils import send_message

@pytest.mark.asyncio
async def test_send_message():
    mock_interaction = MagicMock(spec=Interaction)
    mock_followup = AsyncMock()
    mock_interaction.followup = mock_followup

    mock_response = MagicMock(spec=InteractionCallbackResponse)
    mock_followup.send.return_value = mock_response

    test_message = "Hello, World!"

    result = await send_message(mock_interaction, test_message)

    mock_followup.send.assert_called_once_with(test_message, ephemeral=True)

    assert result == mock_response