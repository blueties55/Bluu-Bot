import discord
from discord.ext import commands
import asyncio
import logging
import os
from dotenv import load_dotenv
from utils.db import Database
import settings

# Load .env
load_dotenv()
DISCORD_API_TOKEN = os.getenv("DISCORD_API_TOKEN")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot")

async def main():
    # ------------------------
    # Initialize settings from DB
    # ------------------------
    await settings.init_settings()  # Loads COMMAND_PREFIX, DM_RESPONSE, etc.

    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    intents.voice_states = True

    bot = commands.Bot(
        command_prefix=commands.when_mentioned_or(settings.COMMAND_PREFIX)
        if getattr(settings, "MENTIONS_AS_PREFIX", False) else settings.COMMAND_PREFIX,
        intents=intents
    )

    # Attach database
    bot.db = Database()
    await bot.db.init_pool()

    @bot.event
    async def on_ready():
        logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
        extensions = [
            "cogs.games.coinflip",
            "cogs.games.higherlower",
            "cogs.games.roulette",
            "cogs.games.rps",
            "cogs.games.tictactoe",
            "cogs.auto_responses_ocr",
            "cogs.chatgpt",
            "cogs.economy",
            "cogs.role_selection",
            "cogs.shop_commands"
        ]
        for ext in extensions:
            try:
                await bot.load_extension(ext)
                logger.info(f"{ext} loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load {ext}: {e}")

    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return
        if isinstance(message.channel, discord.DMChannel) and settings.DM_RESPONSE:
            await message.add_reaction("👋")
            await message.author.send(settings.DM_RESPONSE)
        else:
            await bot.process_commands(message)

    # Start the bot
    await bot.start(DISCORD_API_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())