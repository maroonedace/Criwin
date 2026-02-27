import os
import sys
import asyncio
import signal
import logging

from dotenv import load_dotenv

from src import DiscordBot

# Load environment variables before internal imports
load_dotenv()


def setup_logging() -> None:
    """Configure root logger for the application."""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

def load_config() -> dict:
    """Load and validate required configuration from environment variables."""
    logger = logging.getLogger(__name__)

    discord_token = os.getenv("DISCORD_TOKEN")
    guild_id = os.getenv("GUILD_ID")

    if not discord_token:
        logger.critical("DISCORD_TOKEN is not set")
        sys.exit(1)

    if not guild_id:
        logger.critical("GUILD_ID is not set")
        sys.exit(1)

    try:
        guild_id_int = int(guild_id)
    except ValueError:
        logger.critical("GUILD_ID must be a valid integer, got: %s", guild_id)
        sys.exit(1)

    return {
        "discord_token": discord_token,
        "guild_id": guild_id_int,
    }


async def main() -> None:
    logger = logging.getLogger(__name__)
    config = load_config()

    bot = DiscordBot(guild_id=config["guild_id"])

    # Handle signals
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown(bot, logger)))

    try:
        logger.info("Starting bot")
        async with bot:
            await bot.start(config["discord_token"])
    except Exception:
        logger.exception("Bot encountered a fatal error")
        sys.exit(1)

async def shutdown(bot: DiscordBot, logger: logging.Logger) -> None:
    """Handle graceful shutdown."""
    logger.info("Shutdown signal received, closing bot")
    await bot.close()

if __name__ == "__main__":
    setup_logging()
    asyncio.run(main())