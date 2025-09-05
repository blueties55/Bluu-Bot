import discord
from discord.ext import commands
from PIL import Image
import easyocr
from io import BytesIO
import tempfile
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot")

class Autoresponses(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.keyword_responses = []
        self.filter_terms = []
        self.reader = easyocr.Reader(['en'])
        self.keyword_reaction = "👀"  # Default reaction for all keywords
        self.filter_response = "The message was removed because it has 'a bad word' in it."
    
    async def load_settings(self):
        """Load keywords and filtered terms from the database."""
        # Load keywords from DB
        self.keyword_responses = []
        async with self.bot.db.pool.acquire() as conn:
            rows = await conn.fetch("SELECT keyword, responses FROM auto_responses")
            for row in rows:
                responses = row["responses"].split("\n") if row["responses"] else []
                self.keyword_responses.append({
                    "keyword": row["keyword"].lower(),
                    "responses": responses
                })
        
        # Load filtered terms from DB
        self.filter_terms = []
        async with self.bot.db.pool.acquire() as conn:
            rows = await conn.fetch("SELECT term FROM filtered_terms")
            for row in rows:
                self.filter_terms.append(row["term"].lower())

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        content_lower = message.content.lower()

        # Check image attachments with OCR
        if message.attachments:
            for attachment in message.attachments:
                if attachment.content_type and attachment.content_type.startswith("image"):
                    image_bytes = await attachment.read()
                    image = Image.open(BytesIO(image_bytes))
                    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_image:
                        temp_image_path = temp_image.name
                        image.save(temp_image_path)
                        result = self.reader.readtext(temp_image_path)
                    for text in result:
                        text_lower = text[1].lower()
                        for kw in self.keyword_responses:
                            if kw["keyword"] in text_lower:
                                for r in kw["responses"]:
                                    await message.channel.send(r)
                                await message.add_reaction(self.keyword_reaction)
                                return

        # Check keywords in message content
        for kw in self.keyword_responses:
            if kw["keyword"] in content_lower:
                for r in kw["responses"]:
                    await message.channel.send(r)
                await message.add_reaction(self.keyword_reaction)
                return

        # Check filtered terms
        for term in self.filter_terms:
            if term in content_lower:
                await message.delete()
                await message.channel.send(self.filter_response)
                return

async def setup(bot):
    cog = Autoresponses(bot)
    await cog.load_settings()
    await bot.add_cog(cog)