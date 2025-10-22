import os
import asyncio
from typing import List
import boto3
from discord import Interaction, FFmpegPCMAudio, app_commands
from cloudflare import Cloudflare
from dotenv import load_dotenv

from src.commands.utils import send_message

class Sounds:
    name: str
    file_path: str

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


async def get_sounds(interaction) -> List[Sounds]:
    try:
        query = f"SELECT * FROM {cloudflare_table_name};"
        client = Cloudflare(api_token=cloudflare_api_token)
    
    except Exception:
        # Handle all download/conversion errors
        await send_message(interaction, "❌ Could not connect to Cloudflare client.")
        return
    
    try:
        d1 = client.d1.database.query(
        database_id=cloudflare_database_id,
        account_id=cloudflare_account_id,
        sql=query
        )
    except Exception:
        await send_message(interaction, "❌ Could not connect to database.")
        return
    
    page = d1.result[0]
    if not page.results:
        await send_message(interaction, "❌ No sounds available.")
        return
    return page.results

async def get_sound_file(interaction, file_path) -> List[Sounds]:
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
    
    object_information = s3.head_object(Bucket=cloudflare_bucket_name, Key="soundboard/Im_Still_Standing.mp3")
    print(object_information)
    if not object_information:
        await send_message(interaction, "❌ Could not get s3 item.")
        return
    return object_information

async def autocomplete_sound_name(interaction, current: str) -> List[app_commands.Choice[str]]:
    """Generate autocomplete choices for sound names."""
    sounds = await get_sounds(interaction)
    return [
        app_commands.Choice(name=sound["name"], value=sound["name"])
        for sound in sounds
    ]

def setup_soundboard(tree: app_commands.CommandTree):
    @tree.command(name="soundboard", description="Play a sound in your voice channel.")
    @app_commands.describe(sound_name="Select a sound to play")
    async def soundboard(interaction: Interaction, sound_name: str):
        # Acknowledge the interaction and defer response
        await interaction.response.defer(ephemeral=True)

        # Check user's voice state
        user = interaction.user
        if not user.voice or not user.voice.channel:
            await send_message(interaction, "❌ You must be in a voice channel.")
            return

        sounds = await get_sounds(interaction)
        
        # Find the requested sound
        sound_entry = next((sound for sound in sounds if sound["name"] == sound_name), None)

        if not sound_entry:
            await send_message(interaction, "❌ That sound isn't available.")
            return

        file_path = sound_entry["file_path"]

        sound = await get_sound_file(interaction, file_path)

        channel = user.voice.channel
        vc = interaction.guild.voice_client

        # Connect to voice channel
        try:
            if vc and vc.is_connected():
                await vc.move_to(channel)
            else:
                vc = await channel.connect(timeout=10.0, reconnect=True)
        except Exception:
            await send_message(interaction, "❌ Failed to join voice channel.")
            return

        # Play the sound
        try:
            source = FFmpegPCMAudio(str(file_path))
            done = asyncio.Event()
            
            def after_playing(error: Exception = None):
                if error:
                    print(f"Error playing sound: {error}")
                interaction.client.loop.call_soon_threadsafe(done.set)
            
            vc.play(source, after=after_playing)
            await send_message(interaction, f"▶️ Playing **{sound_name}**.")
            
            # Wait for playback to finish
            await done.wait()
            
            # Disconnect after playback
            if vc and vc.is_connected():
                await vc.disconnect()
            
        except Exception as e:
            # Ensure cleanup on error
            try:
                if vc and vc.is_connected():
                    await vc.disconnect()
            except Exception:
                pass
            await send_message(interaction, f"❌ Could not play sound: {e}")

    # Autocomplete for delete command
    @soundboard.autocomplete("sound_name")
    async def sound_autocomplete(interaction: Interaction, current: str) -> List[app_commands.Choice[str]]:
        return await autocomplete_sound_name(interaction, current)
