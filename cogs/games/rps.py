# Import requirements
import discord
import random
import asyncio
from discord.ext import commands
from utils.minigame import MiniGame

# Create the Coinflip class
class RPS(MiniGame):
    @commands.command(name="rps")
    async def rps(self, ctx, bet: int, member: discord.Member = None):
        if ctx.channel.id != self.allowed_channel_id:
            await ctx.send(f"Please use <#{self.allowed_channel_id}> for that command.")
            return

        if member is None:
            member = ctx.author
        user_id = member.id
        user_coins = await self.db.get_coins(user_id)

        if user_coins is None or bet <= 0 or bet > user_coins:
            await ctx.send("You don't have enough coins or the bet amount is invalid.")
            return

        embed = discord.Embed(title="Rock Paper Scissors", description=f"Choose rock paper or scissors to bet {bet} coins!", color=discord.Color.greyple())
        embed.add_field(name="React with 🪨 for rock", value=" ", inline=False)
        embed.add_field(name="React with 📰 for paper", value=" ", inline=False)
        embed.add_field(name="React with ✂️ for scissors", value=" ", inline=False)
        embed.set_footer(text=f"Your current coins: {user_coins}")

        message = await ctx.send(embed=embed)
        await message.add_reaction('🪨')
        await message.add_reaction('📰')
        await message.add_reaction('✂️')

        def check(reaction, user):
            return user == ctx.author and reaction.message.id == message.id and str(reaction.emoji) in ['🪨', '📰', '✂️']

        try:
            reaction, _ = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond.")
            return

        if str(reaction.emoji) == '🪨':
            choice = 'rock'
        elif str(reaction.emoji) == '📰':
            choice = 'paper'
        else:
            choice = 'scissors'

        result = random.choice(['rock', 'paper', 'scissors'])
        if choice == result:
            outcome = "tie"
            amount = bet
        elif (choice == 'rock' and result == 'scissors')or \
            (choice == 'scissors' and result == 'paper') or \
            (choice == 'paper' and result == 'rock'):
            outcome = "win"
            amount = bet
        else:
            outcome = "lose"
            amount = bet

        await self.db.game_result(ctx, user_id, member, outcome, amount, description=f"The bot chose {result}.")

async def setup(bot):
    db = bot.db
    await bot.add_cog(RPS(bot, db))