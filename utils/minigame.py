import discord
from discord.ext import commands
from utils.db import Database

class MiniGame(commands.Cog):
    def __init__(self, bot, db: Database):
        self.bot = bot
        self.db = db
        self.allowed_channel_id = 0

    async def cog_load(self):
        """Load mini games channel ID from the database"""
        async with self.db.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT channels->>'mini_games_channel_id' AS mini_games_channel_id
                FROM bot_settings
                WHERE id = 1
                """
            )
            if row and row['mini_games_channel_id']:
                self.allowed_channel_id = int(row['mini_games_channel_id'])

    async def send_game_result(self, ctx, user_id, member, outcome, amount, description=None):
        """Helper for games to handle coins and output"""
        await self.db.game_result(ctx, user_id, member, outcome, amount, description)