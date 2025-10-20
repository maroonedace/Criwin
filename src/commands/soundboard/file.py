import os
from discord import Interaction
from cloudflare import Cloudflare
from dotenv import load_dotenv

async def setup_soundboard(interaction: Interaction, sound_name: str):
     # Setting up to load ENV values
    load_dotenv()
    
    # Get Cloudflare items
    cloudflare_api_token = os.getenv('CLOUDFLARE_API_TOKEN')
    cloudflare_account_id = os.getenv('CLOUDFLARE_ACCOUNT_ID')
    cloudflare_database_id = os.getenv('CLOUDFLARE_DATABASE_ID')
    
    TABLE_NAME = "sounds"  

     # Acknowledge the interaction and defer response
    await interaction.response.defer(ephemeral=True)
    
    query = f"SELECT * FROM {TABLE_NAME};"

    client = Cloudflare(api_token=cloudflare_api_token)
    d1 = client.d1.database.query(
     database_id=cloudflare_database_id,
     account_id=cloudflare_account_id,
     sql=query
     )
    page = d1.result[0]
    print(page.results)