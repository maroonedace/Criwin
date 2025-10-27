import os
from typing import List
import boto3
from cloudflare import Cloudflare
from discord import app_commands
from dotenv import load_dotenv
from src.commands.utils import send_message

class Sounds:
    name: str
    file_name: str
    
# Setting up to load ENV values
load_dotenv()

# Get Cloudflare Database tokens
cloudflare_api_token = os.getenv('CLOUDFLARE_API_TOKEN')
cloudflare_account_id = os.getenv('CLOUDFLARE_ACCOUNT_ID')
cloudflare_database_id = os.getenv('CLOUDFLARE_DATABASE_ID')
cloudflare_table_name = os.getenv('CLOUDFLARE_TABLE_NAME')

# Get Cloudflare S3 tokens
cloudflare_endpoint_url = os.getenv('CLOUDFLARE_ENDPOINT_URL')
cloudflare_access_key_id = os.getenv('CLOUDFLARE_ACCESS_KEY_ID')
cloudflare_secret_access_key = os.getenv('CLOUDFLARE_SECRET_ACCESS_KEY')
cloudflare_bucket_name = os.getenv('CLOUDFLARE_BUCKET_NAME')
cloudflare_region_name = os.getenv('CLOUDFLARE_REGION_NAME')

CLOUDFLARE_CLIENT_ERROR_MESSAGE = "❌ Could not connect to Cloudflare client."
CLOUDFLARE_DATABASE_ERROR_MESSAGE = "❌ Could not connect to database."
NO_SOUNDS_ERROR_MESSAGE = "❌ No sounds available."

def get_sounds() -> List[Sounds]:
    try:
        client = Cloudflare(api_token=cloudflare_api_token)
    
    except Exception:
        raise ValueError(CLOUDFLARE_CLIENT_ERROR_MESSAGE)
    
    try:
        query = f"SELECT * FROM {cloudflare_table_name};"
        
        response = client.d1.database.query(
            database_id=cloudflare_database_id,
            account_id=cloudflare_account_id,
            sql=query
        )

    except Exception:
        raise ValueError(CLOUDFLARE_DATABASE_ERROR_MESSAGE)
    
    sound_items = response.result[0].results
    
    if not sound_items:
        raise ValueError(NO_SOUNDS_ERROR_MESSAGE)
    return sound_items

async def get_sound_file(interaction, file_name) -> None:
    try:
        s3 = boto3.client(
        service_name ="s3",
        endpoint_url = cloudflare_endpoint_url,
        aws_access_key_id = cloudflare_access_key_id,
        aws_secret_access_key = cloudflare_secret_access_key,
        region_name=cloudflare_region_name
    )
    
    except Exception:
        await send_message(interaction, "❌ Could not connect to Cloudflare S3 client.")
        return 
    
    try:
        s3.download_file(cloudflare_bucket_name, f"soundboard/{file_name}", f"sounds/{file_name}")
    except Exception as e:
        print(f"Error downloading file from R2: {e}")

async def autocomplete_sound_name(current: str) -> List[app_commands.Choice[str]]:
    """Generate autocomplete choices for sound names."""
    sounds = get_sounds()
    return [
        app_commands.Choice(name=sound["name"], value=sound["name"])
        for sound in sounds
    ]