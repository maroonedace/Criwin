import re
import pytest
import yt_dlp
from unittest.mock import MagicMock, patch
from src.commands.audio_converter.utils import LONG_DURATION_MESSAGE, MAX_VIDEO_LENGTH, URL_INVALID_MESSAGE, video_converter

class TestDownloadClip:
    def test_long_duration_error(self):
        url = "https://youtu.be/invalid_video"
        mock_video_info = {
        'title': 'Test Video',
        'duration': MAX_VIDEO_LENGTH + 1,
        'url': url
        }

        with patch('src.commands.audio_converter.utils.YoutubeDL') as mock_ydl:
            # Create mock instance
            mock_ydl_instance = MagicMock()
            # Mock the context manager behavior
            mock_ydl.return_value = mock_ydl_instance
            # Set the return value for extract_info
            mock_ydl_instance.extract_info.return_value = mock_video_info

            with pytest.raises(ValueError, match=re.escape(LONG_DURATION_MESSAGE)):
                video_converter(url)
    
    def test_invalid_url_error(self):
        url = "https://youtu.be/invalid_video"
        with patch('src.commands.audio_converter.utils.YoutubeDL') as mock_ydl:
            # Create mock instance
            mock_ydl_instance = MagicMock()
            # Mock the context manager behavior
            mock_ydl.return_value = mock_ydl_instance
            # Set the return value for extract_info
            mock_ydl_instance.extract_info.side_effect = yt_dlp.DownloadError("Video unavailable")

            with pytest.raises(ValueError, match=re.escape(URL_INVALID_MESSAGE)):
                video_converter(url)