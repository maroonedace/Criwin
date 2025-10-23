import pytest
from unittest.mock import AsyncMock, Mock, patch
from discord import Interaction, User
from src.commands.yt_to_mp3 import FILE_INVALID_MESSAGE, LONG_DURATION_MESSAGE
from src.commands.yt_to_mp3.file import LIMIT_DOWNLOAD_MESSAGE, INVALID_URL_STRUCTURE_MESSAGE, is_url_valid, setup_yt_to_mp3, active_downloads

class TestYtToMp3:
    user_id = 123456789

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
        interaction.response.defer = AsyncMock()
        return interaction

    def test_if_url_valid(self):
        # Add user to active downloads
        valid_url_structures = [
            "https://www.youtube.com/watch?v=ZX3Rioe-WB8",
            "https://youtu.be/0tdyU_gW6WE?si=49enz2ukzDfX2zaP",
            "https://www.youtube.com/shorts/Uw9XGagnDZo",
            "https://youtube.com/shorts/Uw9XGagnDZo?si=4E3G1wya05Ky986V",
            "https://www.youtube.com/watch?v=0tdyU_gW6WE&list=RD0tdyU_gW6WE&start_radio=1",
            "https://m.youtube.com/watch?v=DfWooe9-zOg&pp=ugUEEgJlbg%3D%3D",
            "https://m.youtube.com/shorts/8PDlV8htpFo",
        ]

        for url in valid_url_structures:
            is_valid = is_url_valid(url)

            assert is_valid

    @pytest.mark.asyncio
    async def test_multiple_downloads(self, mock_interaction):
        # Add user to active downloads
        active_downloads.add(mock_interaction.user.id)

        url = "https://youtu.be/GFokXnCCMf8?si=ie8ydID-XH0F2yrM"
        
        with patch('src.commands.yt_to_mp3.file.send_message', new_callable=AsyncMock) as mock_send_message:
            # Run the async function
            await setup_yt_to_mp3(mock_interaction, url)
            
            # Assert that send_message was called with correct arguments
            mock_send_message.assert_called_once_with(
                mock_interaction, 
                LIMIT_DOWNLOAD_MESSAGE
            )
    
    @pytest.mark.asyncio
    async def test_invalid_url_structure(self, mock_interaction):
        url = "https://youtu.be/GFsdsdsdsdsdsdsd"

        with patch('src.commands.yt_to_mp3.file.send_message', new_callable=AsyncMock) as mock_send_message:
            # Run the async function
            await setup_yt_to_mp3(mock_interaction, url)
            
            # Assert that send_message was called with correct arguments
            mock_send_message.assert_called_once_with(
                mock_interaction, 
                INVALID_URL_STRUCTURE_MESSAGE
            )
    
    @pytest.mark.asyncio
    async def test_invalid_video(self, mock_interaction):
        url = "https://youtu.be/GFsdsdsdsds"
        with patch('src.commands.yt_to_mp3.file.send_message', new_callable=AsyncMock) as mock_send_message:
            # Run the async function
            await setup_yt_to_mp3(mock_interaction, url)
            
            # Assert that send_message was called with correct arguments
            mock_send_message.assert_called_once_with(
                mock_interaction, 
                FILE_INVALID_MESSAGE
            )
    
    @pytest.mark.asyncio
    async def test_long_duration(self, mock_interaction):
        url="https://youtu.be/oIpuh9B54_Y?si=xPBGuRBJLQDTyTA3"
        with patch('src.commands.yt_to_mp3.file.send_message', new_callable=AsyncMock) as mock_send_message:
            # Run the async function
            await setup_yt_to_mp3(mock_interaction, url)
            
            # Assert that send_message was called with correct arguments
            mock_send_message.assert_called_once_with(
                mock_interaction, 
                LONG_DURATION_MESSAGE
            )
        
