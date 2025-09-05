# Import requirements
import discord
import random
import asyncio
from discord.ext import commands
from utils.minigame import MiniGame

# Create the Roulette class
class Roulette(MiniGame):
    @commands.command(name='roulette', aliases=['rl'])
    async def roulette(self, ctx, bet: int, member: discord.Member = None):
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

        # Generate roulette result
        result_number = random.randint(0, 9)
        result_color = 'red' if result_number % 2 != 0 else 'black'

        # Build embed
        embed = discord.Embed(
            title="Roulette",
            description=f"Bet {bet} coins! Choose a color or number to play.",
            color=discord.Color.red()
        )
        embed.add_field(
            name="Colors",
            value="🔴 = red (odd numbers)\n⚫ = black (even numbers)",
            inline=False
        )
        embed.add_field(
            name="Numbers",
            value="0️⃣ - 9️⃣ to pick a specific number",
            inline=False
        )
        embed.set_footer(text=f"Your current coins: {user_coins}")
        message = await ctx.send(embed=embed)

        # Add reactions
        await message.add_reaction('🔴')
        await message.add_reaction('⚫')
        for i in range(0, 10):
            await message.add_reaction(f'{i}\N{COMBINING ENCLOSING KEYCAP}')

        # Check for valid reaction
        def check(reaction, user):
            valid_emojis = ['🔴', '⚫'] + [f'{i}\N{COMBINING ENCLOSING KEYCAP}' for i in range(10)]
            return user == ctx.author and reaction.message.id == message.id and str(reaction.emoji) in valid_emojis

        try:
            reaction, _ = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond.")
            return
        choice = str(reaction.emoji)

        # Determine outcome and payout
        if choice in ['🔴', '⚫']:
            # Color bet
            if (choice == '🔴' and result_color == 'red') or (choice == '⚫' and result_color == 'black'):
                outcome = "win"
                payout = bet * 2
            else:
                outcome = "lose"
                payout = bet
        else:
            # Number bet
            chosen_number = int(choice[0])
            if chosen_number == result_number:
                outcome = "win"
                payout = bet * 3
            else:
                outcome = "lose"
                payout = bet

        # Set amount to the calculated payout for game_result
        amount = payout
        # Use game_result helper
        await self.db.game_result(ctx, user_id, member, outcome, amount, description=f"The roulette landed on {result_number} ({result_color})!")

async def setup(bot):
    db = bot.db
    await bot.add_cog(Roulette(bot, db))