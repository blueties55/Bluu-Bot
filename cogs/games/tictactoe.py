import discord
from discord.ext import commands
from utils.minigame import MiniGame
import asyncio

class TicTacToe(MiniGame):
    number_emojis = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣"]

    @commands.command(name="tictactoe", aliases=["ttt"])
    async def start_game(self, ctx, opponent: discord.Member, bet: int):
        """!ttt @user bet - Starts a TicTacToe game"""
        if ctx.channel.id != self.allowed_channel_id:
            await ctx.send(f"Please use <#{self.allowed_channel_id}> for this command.")
            return

        user_id = ctx.author.id
        opponent_id = opponent.id

        # Check both players' balance
        user_coins = await self.db.get_coins(user_id)
        opponent_coins = await self.db.get_coins(opponent_id)

        if user_coins < bet or opponent_coins < bet:
            await ctx.send("Both players must have enough coins to place the bet.")
            return

        # Deduct bet from both players
        await self.db.subtract_coins(user_id, bet)
        await self.db.subtract_coins(opponent_id, bet)

        # Initialize game state
        self.board = [" "]*9
        self.current_player = ctx.author
        self.player_x = ctx.author
        self.player_o = opponent
        self.bet = bet
        self.game_over = False

        # Send initial board embed
        embed = self.create_board_embed(f"{self.current_player.mention}'s turn (❌)")
        self.game_message = await ctx.send(embed=embed)

        # Add reactions 1️⃣–9️⃣
        for emoji in self.number_emojis:
            await self.game_message.add_reaction(emoji)

        # Start listening for moves
        await self.wait_for_moves(ctx)

    def create_board_embed(self, title):
        board_str = ""
        for i in range(0, 9, 3):
            row_cells = []
            for j in range(3):
                idx = i + j
                if self.board[idx] == " ":
                    # Show number emoji for empty cell
                    row_cells.append(self.number_emojis[idx])
                else:
                    row_cells.append(self.board[idx])
            row = " | ".join(row_cells)
            board_str += f"{row}\n"
            if i < 6:
                board_str += "---------\n"
        embed = discord.Embed(title="TicTacToe", description=board_str, color=discord.Color.gold())
        embed.set_footer(text=f"Playing for: {self.bet*2} coins")
        embed.title = title
        return embed

    async def wait_for_moves(self, ctx):
        def check(reaction, user):
            return (
                user == self.current_player and 
                reaction.message.id == self.game_message.id and
                str(reaction.emoji) in self.number_emojis
            )

        while not self.game_over:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send("Game timed out due to inactivity. Bets refunded.")
                await self.db.add_coins(self.player_x.id, self.bet)
                await self.db.add_coins(self.player_o.id, self.bet)
                self.game_over = True
                return

            move = self.number_emojis.index(str(reaction.emoji))

            if self.board[move] == " ":
                self.board[move] = "❌" if self.current_player == self.player_x else "⭕"
                await self.game_message.edit(embed=self.create_board_embed(f"{self.current_player.mention}'s turn"))

                # Remove player's reaction to keep it clean
                await self.game_message.remove_reaction(reaction.emoji, user)

                winner = self.check_winner()
                if winner or all(cell != " " for cell in self.board):
                    await self.end_game(ctx, winner)
                    return

                # Switch turn
                self.current_player = self.player_o if self.current_player == self.player_x else self.player_x

    def check_winner(self):
        lines = [
            [0,1,2],[3,4,5],[6,7,8],   # rows
            [0,3,6],[1,4,7],[2,5,8],   # columns
            [0,4,8],[2,4,6]            # diagonals
        ]
        for line in lines:
            a,b,c = line
            if self.board[a] == self.board[b] == self.board[c] != " ":
                return self.board[a]  # returns "❌" or "⭕"
        return None

    async def end_game(self, ctx, winner):
        self.game_over = True
        if winner == "❌":
            await self.db.game_result(ctx, self.player_x.id, self.player_x, "win", self.bet*2)
            await self.db.game_result(ctx, self.player_o.id, self.player_o, "lose", 0)
            result_msg = f"{self.player_x.mention} (❌) wins!"
        elif winner == "⭕":
            await self.db.game_result(ctx, self.player_o.id, self.player_o, "win", self.bet*2)
            await self.db.game_result(ctx, self.player_x.id, self.player_x, "lose", 0)
            result_msg = f"{self.player_o.mention} (⭕) wins!"
        else:
            await self.db.game_result(ctx, self.player_x.id, self.player_x, "tie", self.bet)
            await self.db.game_result(ctx, self.player_o.id, self.player_o, "tie", self.bet)
            result_msg = "It's a tie! Bets refunded."

        await self.game_message.edit(embed=self.create_board_embed(result_msg))

async def setup(bot):
    db = bot.db
    await bot.add_cog(TicTacToe(bot, db))
