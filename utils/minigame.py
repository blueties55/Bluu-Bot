import discord
from discord.ext import commands
from utils.db import Database
import json

class MiniGame(commands.Cog):
    def __init__(self, bot, db: Database):
        self.bot = bot
        self.db = db
        self.allowed_channel_id = 0
        self.load_settings()

    def load_settings(self):
        # Load settings.json
        with open("settings.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        channels = config.get("bot_settings", {}).get("channels", {})
        self.allowed_channel_id = int(channels.get("mini_games_channel_id", 0))

    async def send_game_result(self, ctx, user_id, member, outcome, amount, description=None):
        """Helper for games to handle coins and output"""
        await self.db.game_result(ctx, user_id, member, outcome, amount, description)