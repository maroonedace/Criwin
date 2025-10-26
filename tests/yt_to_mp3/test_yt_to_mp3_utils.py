import re
import pytest
import yt_dlp
from unittest.mock import AsyncMock, MagicMock, Mock, patch
from src.commands.yt_to_mp3.utils import LONG_DURATION_MESSAGE, MAX_VIDEO_LENGTH, URL_INVALID_MESSAGE, download_clip, is_url_valid

def test_if_url_valid():
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

class TestDownloadClip:
    def test_long_duration_error(self):
        url = "https://youtu.be/invalid_video"
        mock_video_info = {
        'title': 'Test Video',
        'duration': MAX_VIDEO_LENGTH + 1,
        'url': url
        }

        with patch('src.commands.yt_to_mp3.utils.YoutubeDL') as mock_ydl:
            # Create mock instance
            mock_ydl_instance = MagicMock()
            # Mock the context manager behavior
            mock_ydl.return_value = mock_ydl_instance
            # Set the return value for extract_info
            mock_ydl_instance.extract_info.return_value = mock_video_info

            with pytest.raises(ValueError, match=re.escape(LONG_DURATION_MESSAGE)):
                download_clip(url)
    
    def test_invalid_url_error(self):
        url = "https://youtu.be/invalid_video"
        with patch('src.commands.yt_to_mp3.utils.YoutubeDL') as mock_ydl:
            # Create mock instance
            mock_ydl_instance = MagicMock()
            # Mock the context manager behavior
            mock_ydl.return_value = mock_ydl_instance
            # Set the return value for extract_info
            mock_ydl_instance.extract_info.side_effect = yt_dlp.DownloadError("Video unavailable")

            with pytest.raises(ValueError, match=re.escape(URL_INVALID_MESSAGE)):
                download_clip(url)