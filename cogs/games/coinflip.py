# Import requirements
import discord
import random
import asyncio
from discord.ext import commands
from utils.minigame import MiniGame

# Create the Coinflip class
class CoinFlip(MiniGame):
    @commands.command(name='coinflip', aliases=['cf'])
    async def coinflip(self, ctx, bet: int, member: discord.Member = None):
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

        embed = discord.Embed(
            title="Coin Flip",
            description=f"Choose heads or tails to bet {bet} coins!",
            color=discord.Color.gold()
        )
        embed.add_field(name="React with 🟢 for heads", value=" ", inline=False)
        embed.add_field(name="React with 🔵 for tails", value=" ", inline=False)
        embed.set_footer(text=f"Your current coins: {user_coins}")

        message = await ctx.send(embed=embed)
        await message.add_reaction('🟢')  # Heads
        await message.add_reaction('🔵')  # Tails

        def check(reaction, user):
            return user == ctx.author and reaction.message.id == message.id and str(reaction.emoji) in ['🟢', '🔵']

        try:
            reaction, _ = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond.")
            return

        choice = 'heads' if str(reaction.emoji) == '🟢' else 'tails'
        result = random.choice(['heads', 'tails'])

        outcome = "win" if choice == result else "lose"

        # Set amount to the calculated payout for game_result
        amount = bet
        # Use game_result helper
        await self.db.game_result(ctx, user_id, member, outcome, amount, description=f"The coin landed on {result}!")

async def setup(bot):
    db = bot.db
    await bot.add_cog(CoinFlip(bot, db))