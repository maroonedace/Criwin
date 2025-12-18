import os
import discord
from dotenv import load_dotenv
from discord import Intents, app_commands, Object
from src.commands import setup_commands

# Setting up to load ENV values
load_dotenv()

# Get Discord tokens
discord_token = os.getenv('DISCORD_TOKEN')
guild_id = os.getenv('GUILD_ID')

# Set up Guild Object
GUILD = Object(id=guild_id)

# Set up message and voice state permissions for bot
intents = Intents.default()
intents.voice_states = True  
intents.message_content = True

# Set up client and command tree
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# Set up commands 
@client.event
async def setup_hook():
    # Clear existing commands to remove deprecated commands
    tree.clear_commands(guild=GUILD)
    
    # Function to set up discord commands
    setup_commands(tree)
    
    # Sync to guild to sync commands immediately
    tree.copy_global_to(guild=GUILD)
    await tree.sync(guild=GUILD)
    

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

client.run(discord_token)