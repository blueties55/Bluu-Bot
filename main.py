import discord
from discord.ext import commands
import asyncio
import logging
import json
import os
from dotenv import load_dotenv
from utils.db import Database

# Load .env
load_dotenv()
DISCORD_API_TOKEN = os.getenv("DISCORD_API_TOKEN")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot")

# Load settings.json
with open("settings.json", "r", encoding="utf-8") as f:
    config = json.load(f)

bot_settings = config.get("bot_settings", {})
COMMAND_PREFIX = bot_settings.get("command_prefix", "!")
MENTIONS_AS_PREFIX = bot_settings.get("mentions_as_prefix", False)
DM_RESPONSE = bot_settings.get("dm_response", "")

async def main():
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    intents.voice_states = True

    bot = commands.Bot(
        command_prefix=commands.when_mentioned_or(COMMAND_PREFIX) if MENTIONS_AS_PREFIX else COMMAND_PREFIX,
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
        if isinstance(message.channel, discord.DMChannel) and DM_RESPONSE:
            await message.add_reaction("👋")
            await message.author.send(DM_RESPONSE)
        else:
            await bot.process_commands(message)

    # Start the bot
    await bot.start(DISCORD_API_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())