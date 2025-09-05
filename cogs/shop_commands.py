import discord
from discord.ext import commands, tasks
import asyncio
from datetime import datetime
from utils.db import Database
import json

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db: Database = bot.db
        self.shop_items = {}
        self.allowed_channel_id = 0
        self.load_settings()
        self.remove_roles.start()

    async def cog_load(self):
        async with self.db.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT channels->>'shop_channel_id' AS shop_channel_id FROM bot_settings WHERE id = 1")
            if row and row['shop_channel_id']:
                self.allowed_channel_id = int(row['shop_channel_id'])

    async def load_shop_items_from_db(self):
        """Fetch shop items from DB table `shop_items`"""
        self.shop_items = {}
        async with self.db.pool.acquire() as conn:
            rows = await conn.fetch("SELECT emoji, display_name, item_name, price FROM shop_items ORDER BY id")
            for row in rows:
                self.shop_items[row["emoji"]] = {
                    "name": row["display_name"],
                    "shop_item": row["item_name"],
                    "price": row["price"]
                }

    @tasks.loop(minutes=15)
    async def remove_roles(self):
        today = datetime.now()
        # Thursday at 8am
        if today.weekday() != 3 or today.hour != 8:
            return

        guild = self.bot.get_guild(814609575990263818)
        role_name = "Movie Night 🎬"
        if guild:
            role = discord.utils.get(guild.roles, name=role_name)
            if role:
                for member in guild.members:
                    await member.remove_roles(role)
                    await asyncio.sleep(1)

        channel = self.bot.get_channel(892876332155957248)
        if channel:
            await channel.send(f"The role '{role_name}' has been removed from all members.")

    @commands.command()
    async def shop(self, ctx, member: discord.Member = None):
        """Show the server shop and allow buying items"""
        if ctx.channel.id != self.allowed_channel_id:
            await ctx.send(f"Please use <#{self.allowed_channel_id}> for that command.")
            return

        if member is None:
            member = ctx.author
        user_id = member.id

        user_coins = await self.bot.db.get_coins(user_id)
        if user_coins == 0:
            await ctx.send("You don't have enough coins to shop right now. Come back later!")
            return

        await self.load_shop_items_from_db()  # fetch latest shop items from DB

        embed = discord.Embed(
            title="Welcome to the shop!",
            description="React with the corresponding emoji to buy an item."
        )
        for emoji, item_data in self.shop_items.items():
            embed.add_field(
                name=f"{item_data['name']} {emoji}",
                value=f"Price: {item_data['price']} coins",
                inline=False
            )
        embed.set_thumbnail(url="https://i.imgur.com/Z4pIaTR.png")

        message = await ctx.send(embed=embed)
        for emoji in self.shop_items.keys():
            await message.add_reaction(emoji)

        def check(reaction, user):
            return user == ctx.author and reaction.message.id == message.id

        try:
            reaction, _ = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("The shop has closed! Use !shop again to continue shopping")
            await message.delete()
            return

        await message.delete()

        item_data = self.shop_items.get(str(reaction.emoji))
        if not item_data:
            await ctx.send("Invalid choice!")
            return

        item_name = item_data["name"]
        item_price = item_data["price"]
        shop_item = item_data["shop_item"]

        if item_price > user_coins:
            await ctx.send("You don't have enough coins.")
            return

        # Subtract coins using db.py
        await self.bot.db.subtract_coins(user_id, item_price)
        await ctx.send(f"{member} bought {item_name}!")

        guild = ctx.guild
        role = discord.utils.get(guild.roles, name=shop_item)
        if role:
            await member.add_roles(role)
            await ctx.send(f"{member} has been given the {shop_item} role!")
        else:
            await ctx.send("Error: Role not found. Please contact a server admin.")

    def cog_unload(self):
        self.remove_roles.cancel()


async def setup(bot):
    cog = Shop(bot)
    await cog.cog_load()
    await bot.add_cog(cog)