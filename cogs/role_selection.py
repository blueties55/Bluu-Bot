import discord
from discord.ext import commands
import json
from utils.db import Database

class RoleSelection(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db: Database = bot.db
        self.reaction_message_id = None
        self.default_roles = []
        self.role_data = {}
        self.owner_role = ""
        self.load_settings()

    def load_settings(self):
        # Load owner role and default roles from settings.json
        with open("settings.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        bot_settings = config.get("bot_settings", {})
        roles_config = bot_settings.get("roles", {})
        self.owner_role = roles_config.get("owner_role", "Owner 👑")
        self.default_roles = roles_config.get("default_roles", ["Newborns 👶"])

    async def load_roles_from_db(self):
        """Fetch role selection info from DB table `roles`"""
        self.role_data = {}
        async with self.db.pool.acquire() as conn:
            rows = await conn.fetch("SELECT emoji, display_name, role_name FROM roles")
            for row in rows:
                self.role_data[row["emoji"]] = {
                    "name": row["display_name"],
                    "role_name": row["role_name"]
                }

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        for role_name in self.default_roles:
            role = discord.utils.get(guild.roles, name=role_name)
            if role:
                await member.add_roles(role)

    @commands.command()
    async def roleselection(self, ctx):
        if not any(role.name == self.owner_role for role in ctx.author.roles):
            await ctx.send("You don't have the required role to use this command.")
            return

        await self.load_roles_from_db()  # fetch latest roles from DB

        embed = discord.Embed(title="Role Shop", description="React to get a role!", color=discord.Color.blurple())
        for emoji, item_data in self.role_data.items():
            embed.add_field(name=f"{item_data['name']}", value=f"{emoji}", inline=True)

        message = await ctx.send(embed=embed)
        self.reaction_message_id = message.id
        for emoji in self.role_data.keys():
            await message.add_reaction(emoji)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id != self.reaction_message_id or payload.user_id == self.bot.user.id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        member = guild.get_member(payload.user_id)
        if not member:
            return

        emoji = payload.emoji.name if payload.emoji.is_custom_emoji() else str(payload.emoji)
        role_name = self.role_data.get(emoji, {}).get("role_name")
        if role_name:
            role = discord.utils.get(guild.roles, name=role_name)
            if role:
                await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.message_id != self.reaction_message_id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        member = guild.get_member(payload.user_id)
        if not member:
            return

        emoji = payload.emoji.name if payload.emoji.is_custom_emoji() else str(payload.emoji)
        role_name = self.role_data.get(emoji, {}).get("role_name")
        if role_name:
            role = discord.utils.get(guild.roles, name=role_name)
            if role:
                await member.remove_roles(role)

async def setup(bot):
    await bot.add_cog(RoleSelection(bot))