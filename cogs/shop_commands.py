import discord
from discord.ext import commands, tasks
import configparser
import asyncio
from datetime import datetime

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.shop_items = {}
        self.load_settings()
        self.remove_roles.start()

    def load_settings(self):
        config = configparser.ConfigParser()
        config.read('shop_settings.txt', encoding='utf-8')

        # Load allowed channel ID
        self.allowed_channel_id = int(config.get('DEFAULT', 'allowed_channel_id'))

        # Load shop items
        self.shop_items = {}
        for i in range(1, 7):  # Assuming there are 6 items
            emoji = config.get('DEFAULT', f'shop_item_emoji_{i}', fallback=None)
            name = config.get('DEFAULT', f'shop_item_name_{i}', fallback=None)
            price = config.getint('DEFAULT', f'shop_item_price_{i}', fallback=None)
            shop_item = config.get('DEFAULT', f'shop_item_{i}', fallback=None)
            if emoji and name and price is not None and shop_item:
                self.shop_items[emoji] = {
                    "name": name,
                    "price": price,
                    "shop_item": shop_item
                }

    @tasks.loop(minutes=15)
    async def remove_roles(self):
        today = datetime.now()
        weekday = today.weekday()
        if weekday != 3 or today.hour != 8:  # Thursday at 8am
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
        """ Show the server shop and use your coins """
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
            return
        finally:
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
        new_coins = await self.bot.db.subtract_coins(user_id, item_price)
        await ctx.send(f"{member} bought {item_name}!")

        guild = ctx.guild
        role = discord.utils.get(guild.roles, name=shop_item)
        if role:
            await member.add_roles(role)
            await ctx.send(f"{member} has been given the {shop_item} role!")
        else:
            await ctx.send("Error: Role not found. Please contact a server admin.")

    async def get_username(self, user_id):
        user = await self.bot.fetch_user(user_id)
        return user.display_name if user else f"Unknown User({user_id})"

    def cog_unload(self):
        self.remove_roles.cancel()


async def setup(bot):
    await bot.add_cog(Shop(bot))