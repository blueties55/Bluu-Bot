# Import requirements
import discord
import random
import asyncio
from discord.ext import commands
from utils.minigame import MiniGame

# Create the Coinflip class
class HigherLower(MiniGame):
    @commands.command(name="higherlower", aliases=['hl'])
    async def hl(self, ctx, bet: int, member: discord.Member = None):
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

        embed = discord.Embed(title="Higher or Lower", description=f"Decide if The Bot chose a number higher or lower than 50!", color=discord.Colour.blue())
        embed.add_field(name="React with 🟢 for higher", value=" ", inline=False)
        embed.add_field(name="React with 🔴 for lower", value=" ", inline=False)
        embed.set_footer(text=f"Your current coins: {user_coins}")

        message = await ctx.send(embed=embed)
        await message.add_reaction('🟢')
        await message.add_reaction('🔴')

        def check(reaction, user):
            return user == ctx.author and reaction.message.id == message.id and str(reaction.emoji) in ['🟢', '🔴']

        try:
            reaction, _ = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond.")
            return

        choice = 'higher' if str(reaction.emoji) == '🟢' else 'lower'

        random_number = random.randint(1, 100)

        # Determine outcome
        if (random_number > 50 and choice == 'higher') or (random_number < 50 and choice == 'lower'):
            outcome = "win"
            amount = bet
        elif random_number == 50:
            outcome = "tie"
            amount = bet
        else:
            outcome = "lose"
            amount = bet

        # Use game_result helper
        await self.db.game_result(ctx, user_id, member, outcome, amount, description=f"The bot chose {random_number}. You guessed {choice}.")

async def setup(bot):
    db = bot.db
    await bot.add_cog(HigherLower(bot, db))