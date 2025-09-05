import discord
from discord.ext import commands
import requests
import json
import os
import yaml
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_TOKEN')

with open('OpenAIConfig.yml', 'r', encoding='utf-8') as file:
    openai_config = yaml.safe_load(file)

class ChatGPTCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.openai_model = openai_config['openai']['model']
        self.temperature = openai_config['openai']['temperature']
        self.max_tokens = openai_config['openai']['max_tokens']
        self.top_p = openai_config['openai']['top_p']
        self.frequency_penalty = openai_config['openai']['frequency_penalty']
        self.presence_penalty = openai_config['openai']['presence_penalty']
        self.instructions = openai_config['instructions']

    def get_chatgpt_response(self, message):
        headers = {
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json'
        }
        data = {
            'model': self.openai_model,
            'messages': [
                {'role': 'system', 'content': self.instructions},
                {'role': 'user', 'content': message}
            ],
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'top_p': self.top_p,
            'frequency_penalty': self.frequency_penalty,
            'presence_penalty': self.presence_penalty
        }
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            data=json.dumps(data)
        )
        response_json = response.json()
        if 'choices' in response_json:
            return response_json['choices'][0]['message']['content']
        else:
            print(f"Error in OpenAI API response: {response_json}")
            return "Sorry, I couldn't generate a response."

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        # Only respond when bot is mentioned in a guild channel
        if self.bot.user in message.mentions:
            user_message = message.content.replace(f'<@!{self.bot.user.id}>', '').strip()
            response = self.get_chatgpt_response(user_message)
            await message.channel.send(response)

async def setup(bot):
    await bot.add_cog(ChatGPTCog(bot))