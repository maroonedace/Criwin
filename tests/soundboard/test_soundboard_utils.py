import re
import pytest
from unittest.mock import MagicMock, patch

from src.commands.soundboard.utils import CLOUDFLARE_DATABASE_CLIENT_ERROR_MESSAGE, CLOUDFLARE_DATABASE_ERROR_MESSAGE, CLOUDFLARE_S3_CLIENT_ERROR_MESSAGE, NO_DOWNLOAD_SOUND_ERROR_MESSAGE, NO_SOUNDS_ERROR_MESSAGE, get_cloudflare_database_client, get_cloudflare_s3_client, download_sound_file, get_sounds

class TestGetSounds:
    def test_invalid_cloudflare_database_client(self):
        with patch('src.commands.soundboard.utils.Cloudflare') as mock_cloudflare:
            # Set the return value for extract_info
            mock_cloudflare.side_effect = Exception("Cloudflare Database API token invalid")
            
            # Assert that send_message was called with correct arguments
            with pytest.raises(ValueError, match=re.escape(CLOUDFLARE_DATABASE_CLIENT_ERROR_MESSAGE)):
                get_cloudflare_database_client()
    
    def test_invalid_cloudflare_s3_client(self):
        with patch('src.commands.soundboard.utils.boto3') as mock_boto3:
            # Set the return value for extract_info
            mock_boto3_instance = MagicMock()
            mock_boto3.return_value = mock_boto3_instance
            mock_boto3.client.side_effect = Exception("Cloudflare S3 API token invalid")
            
            # Assert that send_message was called with correct arguments
            with pytest.raises(ValueError, match=re.escape(CLOUDFLARE_S3_CLIENT_ERROR_MESSAGE)):
                get_cloudflare_s3_client()
    

    def test_invalid_cloudflare_database_query(self):
        with patch('src.commands.soundboard.utils.Cloudflare') as mock_cloudflare:
            # Set the return value for extract_info
            mock_client_instance = MagicMock()
            mock_cloudflare.return_value = mock_client_instance
            mock_client_instance.d1.database.query.side_effect = Exception("Database query failed")
            
            # Assert that send_message was called with correct arguments
            with pytest.raises(ValueError, match=re.escape(CLOUDFLARE_DATABASE_ERROR_MESSAGE)):
                get_sounds()
    
    def test_empty_cloudflare_database(self):
        with patch('src.commands.soundboard.utils.Cloudflare') as mock_cloudflare:
            # Set the return value for extract_info
            mock_client_instance = MagicMock()
            mock_cloudflare.return_value = mock_client_instance

            mock_query_result = MagicMock()
            mock_query_result.results = []

            mock_response = MagicMock()
            mock_response.result = [mock_query_result]

            mock_client_instance.d1.database.query.return_value = mock_response
            
            # Assert that send_message was called with correct arguments
            with pytest.raises(ValueError, match=re.escape(NO_SOUNDS_ERROR_MESSAGE)):
                get_sounds()


    def test_no_download_sound(self):
        mock_file_name = "Test File"
        with patch('src.commands.soundboard.utils.get_cloudflare_s3_client') as mock_s3_client:
            # Set the return value for extract_info
            mock_boto3_instance = MagicMock()
            mock_s3_client.return_value = mock_boto3_instance
            mock_s3_client.client.return_value = []
            mock_boto3_instance.download_file.side_effect = Exception("Database query failed")
            
            # Assert that send_message was called with correct arguments
            with pytest.raises(ValueError, match=re.escape(NO_DOWNLOAD_SOUND_ERROR_MESSAGE)):
                download_sound_file(mock_file_name)
    