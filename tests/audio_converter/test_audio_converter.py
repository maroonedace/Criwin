import pytest
from unittest.mock import AsyncMock, Mock, patch
from discord import Interaction, User
from src.commands.audio_converter.setup import LIMIT_DOWNLOAD_MESSAGE, setup_audio_converter_command, active_downloads

class TestYtToMp3:
    user_id = 123456789

    @pytest.fixture
    def mock_interaction(self):
        """Create a mock interaction object"""
        interaction = Mock(spec=Interaction)
        interaction.user = Mock(spec=User)
        interaction.user.id = self.user_id
        interaction.response.defer = AsyncMock()
        return interaction

    @pytest.mark.asyncio
    async def test_multiple_downloads(self, mock_interaction):
        # Add user to active downloads
        active_downloads.add(mock_interaction.user.id)

        url = "https://youtu.be/GFokXnCCMf8?si=ie8ydID-XH0F2yrM"
        
        with patch('src.commands.audio_converter.setup.send_message', new_callable=AsyncMock) as mock_send_message:
            # Run the async function
            await setup_audio_converter_command(mock_interaction, url)
            
            # Assert that send_message was called with correct arguments
            mock_send_message.assert_called_once_with(
                mock_interaction, 
                LIMIT_DOWNLOAD_MESSAGE
            )
        active_downloads.clear()
    
    @pytest.mark.asyncio
    async def test_download_clip(self, mock_interaction):
        url = "https://youtu.be/GFsdsdsdsds"
        error_message = "Video unavailable"
        with patch('src.commands.audio_converter.setup.send_message') as mock_send_message:
            with patch('src.commands.audio_converter.setup.download_audio_file') as mock_download_audio_file:
                mock_download_audio_file.side_effect = Exception(error_message)
                # Run the async function
                await setup_audio_converter_command(mock_interaction, url)
                
                # Assert that send_message was called with correct arguments
                mock_send_message.assert_called_once_with(
                    mock_interaction, 
                    error_message
                )
        
