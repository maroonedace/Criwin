import pytest
from unittest.mock import AsyncMock, Mock, patch
from discord import Interaction, User, VoiceState
from src.commands.soundboard.play_soundboard.file import VOICE_STATE_INVALID_MESSAGE, setup_soundboard_play

class TestSoundboard:
    user_id = 123456789

    @pytest.fixture
    def mock_interaction(self):
        """Create a mock interaction object"""
        interaction = Mock(spec=Interaction)
        interaction.user = Mock(spec=User)
        interaction.user.id = self.user_id
        interaction.user.voice = Mock(spec=VoiceState)
        interaction.user.voice = None
        interaction.response.defer = AsyncMock()
        return interaction

    @pytest.mark.asyncio
    async def test_invalid_voice_state(self, mock_interaction):
        sound_name = "Sus"
        
        with patch('src.commands.soundboard.play_soundboard.file.send_message', new_callable=AsyncMock) as mock_send_message:
            # Add user to active downloads
            await setup_soundboard_play(mock_interaction, sound_name)
            
            # Assert that send_message was called with correct arguments
            mock_send_message.assert_called_once_with(
                mock_interaction, 
                VOICE_STATE_INVALID_MESSAGE
            )
