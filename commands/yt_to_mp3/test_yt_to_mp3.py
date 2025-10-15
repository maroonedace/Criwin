import pytest
from unittest.mock import Mock, patch
from discord import Interaction, User
from commands.yt_to_mp3.file import setup_yt_to_mp3, active_downloads


@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Fixture to reset active_downloads before and after each test"""
    active_downloads.clear()
    yield
    active_downloads.clear()
    # send_message()

@pytest.fixture
def mock_interaction():
    """Create a mock interaction object"""
    interaction = Mock(spec=Interaction)
    interaction.user = Mock()
    interaction.user.id = 123456789
    return interaction

def test(mock_interaction):   
    with patch('commands.utils.send_message') as mock_send_message:
        url = ""
        setup_yt_to_mp3(
                mock_interaction, 
                url,
            )
        mock_send_message.assert_not_called()