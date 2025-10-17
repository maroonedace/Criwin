import pytest
from unittest.mock import AsyncMock, Mock, patch
from discord import Interaction, User
from commands.yt_to_mp3.file import DURATION_INVALID_MESSAGE, LIMIT_DOWNLOAD_MESSAGE, URL_MISMATCH_MESSAGE, setup_yt_to_mp3, active_downloads

class TestYtToMp3:
    user_id = 123456789
    invalid_url = "https://youtu.be/GFsdsdsdsdsdsdsd"
    invalid_url_2 = "https://youtu.be/GFsdsdsdsds"
    valid_url = "https://youtu.be/GFokXnCCMf8?si=ie8ydID-XH0F2yrM"

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Fixture to reset active_downloads before and after each test"""
        active_downloads.clear()
        yield
        active_downloads.clear()

    @pytest.fixture
    def mock_interaction(self):
        """Create a mock interaction object"""
        interaction = Mock(spec=Interaction)
        interaction.user = Mock(spec=User)
        interaction.user.id = self.user_id
        return interaction

    @pytest.mark.asyncio
    async def test_multiple_downloads(self, mock_interaction):
        # Add user to active downloads
        active_downloads.add(mock_interaction.user.id)
        
        with patch('commands.yt_to_mp3.file.send_message', new_callable=AsyncMock) as mock_send_message:
            # Run the async function
            await setup_yt_to_mp3(mock_interaction, self.valid_url)
            
            # Assert that send_message was called with correct arguments
            mock_send_message.assert_called_once_with(
                mock_interaction, 
                LIMIT_DOWNLOAD_MESSAGE
            )
    
    @pytest.mark.asyncio
    async def test_invalid_url(self, mock_interaction):
        with patch('commands.yt_to_mp3.file.send_message', new_callable=AsyncMock) as mock_send_message:
            # Run the async function
            await setup_yt_to_mp3(mock_interaction, self.invalid_url)
            
            # Assert that send_message was called with correct arguments
            mock_send_message.assert_called_once_with(
                mock_interaction, 
                URL_MISMATCH_MESSAGE
            )
    
    @pytest.mark.asyncio
    async def test_invalid_duration(self, mock_interaction):
        with patch('commands.yt_to_mp3.file.send_message', new_callable=AsyncMock) as mock_send_message:
            # Run the async function
            await setup_yt_to_mp3(mock_interaction, self.invalid_url_2)
            
            # Assert that send_message was called with correct arguments
            mock_send_message.assert_called_once_with(
                mock_interaction, 
                DURATION_INVALID_MESSAGE
            )
        
