import discord
from discord.ext import commands
import configparser
from utils.db import Database

class MiniGame(commands.Cog):
    def __init__(self, bot, db: Database):
        self.bot = bot
        self.db = db
        self.allowed_channel_id = 0
        self.load_settings()

    def load_settings(self):
        config = configparser.ConfigParser()
        config.read('settings.txt', encoding='utf-8')
        self.allowed_channel_id = int(config.get('DEFAULT', 'mini_games_channel_id'))

    async def send_game_result(self, ctx, user_id, member, outcome, amount, description=None):
        """Helper for games to handle coins and output"""
        await self.db.game_result(ctx, user_id, member, outcome, amount, description)