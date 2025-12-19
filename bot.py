from discord import Intents, app_commands, Object, Client
from src.commands import setup_commands

class DiscordBot(Client):
    def __init__(self, guild_id: int):
        # Set up intents
        intents = Intents.default()
        intents.voice_states = True
        intents.message_content = True
        
        super().__init__(intents=intents)
        
        self.guild = Object(id=guild_id)
        self.tree = app_commands.CommandTree(self)
    
    async def setup_hook(self):
        """Initialize commands and sync with Discord"""
        # Clear existing commands to remove deprecated commands
        self.tree.clear_commands(guild=self.guild)
        
        # Set up discord commands
        setup_commands(self.tree)
        
        # Sync to guild to sync commands immediately
        self.tree.copy_global_to(guild=self.guild)
        await self.tree.sync(guild=self.guild)
    
    async def on_ready(self):
        """Handle bot ready event"""
        print(f'We have logged in as {self.user}')