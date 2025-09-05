import discord
from discord.ext import commands, tasks
import time
from utils.db import Database

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db  # Use the shared Database instance
        self.cooldowns = {}
        self.owner_role = ""
        self.allowed_channel_id = 0
        self.load_settings()
        self.update_bal_task.start()

    def load_settings(self):
        import configparser
        config = configparser.ConfigParser()
        config.read('settings.txt', encoding='utf-8')
        self.owner_role = config.get('DEFAULT', 'owner_role')
        self.allowed_channel_id = int(config.get('DEFAULT', 'bot_commands_channel_id'))

    # ---------------------
    # Commands
    # ---------------------
    @commands.command(name='addcoins', aliases=['ac'], hidden=True)
    async def addcoins(self, ctx, member: discord.Member, amount: int):
        if not any(role.name == self.owner_role for role in ctx.author.roles):
            await ctx.send("You don't have the required role to use this command.")
            return
        if amount <= 0:
            await ctx.send("Please provide a positive amount of coins to add.")
            return
        new_balance = await self.db.add_coins(member.id, amount)
        await ctx.send(f"Added {amount} coins to {member.display_name}. New balance: {new_balance}")

    @commands.command(name='removecoins', aliases=['rc'], hidden=True)
    async def removecoins(self, ctx, member: discord.Member, amount: int):
        if not any(role.name == self.owner_role for role in ctx.author.roles):
            await ctx.send("You don't have the required role to use this command.")
            return
        if amount <= 0:
            await ctx.send("Please provide a positive amount of coins to remove.")
            return
        new_balance = await self.db.subtract_coins(member.id, amount)
        await ctx.send(f"Removed {amount} coins from {member.display_name}. New balance: {new_balance}")

    @commands.command(name='payment', aliases=['pay'])
    async def payment(self, ctx, recipient: discord.Member, amount: int):
        if ctx.channel.id != self.allowed_channel_id:
            await ctx.send(f"Please use <#{self.allowed_channel_id}> for that command.")
            return
        if amount <= 0:
            await ctx.send("Please provide a positive amount of coins to pay.")
            return
        payer_id = ctx.author.id
        payer_bal = await self.db.get_coins(payer_id)
        if payer_bal < amount:
            await ctx.send("You do not have enough coins to make this payment.")
            return
        await self.db.subtract_coins(payer_id, amount)
        await self.db.add_coins(recipient.id, amount)
        await ctx.send(f"Paid {amount} coins to {recipient.display_name}.")

    @commands.command(name='bal')
    async def show_bal(self, ctx, member: discord.Member = None):
        if ctx.channel.id != self.allowed_channel_id:
            await ctx.send(f"Please use <#{self.allowed_channel_id}> for that command.")
            return
        if member is None:
            member = ctx.author
        bal = await self.db.get_coins(member.id)
        embed = discord.Embed(
            title=f"{member}'s current balance",
            colour=discord.Colour.dark_magenta(),
            description=f"{member} | Coins: {bal}"
        )
        embed.set_footer(text="Please report any issues to server admin!")
        await ctx.send(embed=embed)

    @commands.command(name='economy', aliases=['econ'])
    async def economy_command(self, ctx):
        if ctx.channel.id != self.allowed_channel_id:
            await ctx.send(f"Please use <#{self.allowed_channel_id}> for that command.")
            return

        economy_data = []
        async with self.db.pool.acquire() as conn:
            rows = await conn.fetch('SELECT user_id, coins FROM economy ORDER BY coins DESC LIMIT 15')
            for row in rows:
                user = await self.bot.fetch_user(row['user_id'])
                username = user.display_name if user else f"Unknown User({row['user_id']})"
                economy_data.append((username, row['coins']))

        embed = discord.Embed(title="Server Economy: Top 15 🪙", colour=0x480476)
        medals = ["🥇", "🥈", "🥉"]
        
        for idx, (username, coins) in enumerate(economy_data, start=1):
            medal = medals[idx-1] if idx <= 3 else ""
            embed.add_field(
                name=f"{medal} {idx}. {username}",
                value=f"{coins:,} coins",
                inline=False
            )

        embed.set_footer(text="Please report any issues to server admin!")
        await ctx.send(embed=embed)

    @commands.command(name='daily')
    async def daily(self, ctx):
        if ctx.channel.id != self.allowed_channel_id:
            await ctx.send(f"Please use <#{self.allowed_channel_id}> for that command.")
            return

        user_id = ctx.author.id
        last_claim = await self.db.get_last_daily_claim(user_id)

        if time.time() - last_claim < 24*60*60:
            await ctx.send("You've already claimed your daily coins. Please try again later.")
            return

        await self.db.add_coins(user_id, 500)
        await self.db.update_last_daily_claim(user_id)
        await ctx.send("500 coins have been added to your account. Come back tomorrow for more!")


    # ---------------------
    # Passive earnings
    # ---------------------
    @tasks.loop(minutes=2)
    async def update_bal_task(self):
        for guild in self.bot.guilds:
            for member in guild.members:
                if member.voice and member.voice.channel:
                    await self.db.add_coins(member.id, 2)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        user_id = message.author.id
        if user_id in self.cooldowns and time.time() - self.cooldowns[user_id] < 60:
            return
        await self.db.add_coins(user_id, 2)
        self.cooldowns[user_id] = time.time()

    def cog_unload(self):
        self.update_bal_task.cancel()

async def setup(bot):
    await bot.add_cog(Economy(bot))