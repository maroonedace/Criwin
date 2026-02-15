import os
from dotenv import load_dotenv
from src.logger import setup_logging

# Load environment variables
load_dotenv()

# Setup logging
setup_logging()

# Import DiscordBot
from src import DiscordBot

def main():
    # Get configuration
    discord_token = os.getenv('DISCORD_TOKEN')
    guild_id = os.getenv('GUILD_ID')
    
    if not discord_token or not guild_id:
        raise ValueError("Missing required environment variables")
    
    # Create and run bot
    bot = DiscordBot(guild_id=int(guild_id))
    bot.run(discord_token)

if __name__ == "__main__":
    main()