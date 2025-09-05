import discord
import asyncpg
import os
import time
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.pool = None

    async def init_pool(self):
        """Initialize asyncpg pool"""
        self.pool = await asyncpg.create_pool(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 5432))
        )

    # -------------------
    # Economy helpers
    # -------------------

    async def get_coins(self, user_id: int) -> int:
        """Return current coins for a user"""
        async with self.pool.acquire() as conn:
            result = await conn.fetchrow("SELECT coins FROM economy WHERE user_id=$1", user_id)
            return result['coins'] if result else 0

    async def update_coins(self, user_id: int, coins: int):
        """Set a user's coins to a specific value"""
        async with self.pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO economy (user_id, coins) VALUES ($1, $2) "
                "ON CONFLICT (user_id) DO UPDATE SET coins=$2",
                user_id, coins
            )

    async def add_coins(self, user_id: int, amount: int) -> int:
        """Add coins to a user and return new balance"""
        async with self.pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO economy (user_id, coins) VALUES ($1, $2) "
                "ON CONFLICT (user_id) DO UPDATE SET coins = economy.coins + $2",
                user_id, amount
            )
            result = await conn.fetchrow("SELECT coins FROM economy WHERE user_id=$1", user_id)
            return result['coins']

    async def subtract_coins(self, user_id: int, amount: int) -> int:
        """Subtract coins from a user, prevent negative balance, return new balance"""
        async with self.pool.acquire() as conn:
            result = await conn.fetchrow("SELECT coins FROM economy WHERE user_id=$1", user_id)
            current = result['coins'] if result else 0
            new_balance = max(current - amount, 0)
            await conn.execute(
                "INSERT INTO economy (user_id, coins) VALUES ($1, $2) "
                "ON CONFLICT (user_id) DO UPDATE SET coins=$2",
                user_id, new_balance
            )
            return new_balance
        
    # -------------------
    # Daily coins
    # -------------------
    async def get_last_daily_claim(self, user_id: int) -> int:
        """Return the timestamp of the last daily claim (or 0 if none)."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT last_claim FROM daily WHERE user_id=$1", user_id
            )
            return row['last_claim'] if row else 0

    async def update_last_daily_claim(self, user_id: int):
        """Update the last daily claim time to now."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO daily (user_id, last_claim) VALUES ($1, $2) "
                "ON CONFLICT (user_id) DO UPDATE SET last_claim=$2",
                user_id, int(time.time())
            )

    # -------------------
    # Game result handler
    # -------------------

    async def game_result(self, ctx, user_id: int, member: discord.Member, outcome: str, amount: int, description: str = None) -> int:
        """
        Handles updating coins and sending messages after a game.
        outcome: 'win', 'lose', or 'tie'
        """
        if outcome == "win":
            new_coins = await self.add_coins(user_id, amount)
            result_text = f"won {amount} coins!"
        elif outcome == "lose":
            new_coins = await self.subtract_coins(user_id, amount)
            result_text = f"lost {amount} coins."
        else:
            new_coins = await self.get_coins(user_id)
            result_text = f"tied - no coins changed."

        # Correctly reference member.mention
        msg = f"{member.mention} {result_text} New balance: {new_coins}"
        if description:
            msg = f"{description}\n{msg}"

        await ctx.send(msg)
        return new_coins