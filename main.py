import discord
from discord.ext import commands
import asyncio
import configparser
import logging
from utils.db import Database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot")

def read_settings(file_path):
    config = configparser.ConfigParser()
    with open(file_path, encoding='utf-8') as f:
        config.read_file(f)
    return config['DEFAULT']

def read_command_prefix(file_path):
    return read_settings(file_path).get("command_prefix", "!")

def read_mention_as_prefix(file_path):
    return read_settings(file_path).get("mention_as_prefix", "False").lower() == "true"

def read_dm_response(file_path):
    return read_settings(file_path).get("dm_response", "")

async def main():
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    intents.voice_states = True

    command_prefix = read_command_prefix('settings.txt')
    mention_as_prefix = read_mention_as_prefix('settings.txt')

    bot = commands.Bot(
        command_prefix=commands.when_mentioned_or(command_prefix) if mention_as_prefix else command_prefix,
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
        dm_response = read_dm_response('settings.txt')
        if message.author == bot.user:
            return
        if isinstance(message.channel, discord.DMChannel) and dm_response:
            await message.add_reaction("👋")
            await message.author.send(dm_response)
        else:
            await bot.process_commands(message)

    DISCORD_API_TOKEN = read_settings('settings.txt').get("DISCORD_API_TOKEN", "")
    await bot.start(DISCORD_API_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())