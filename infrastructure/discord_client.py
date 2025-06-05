# infrastructure/discord_client.py

import discord
from app.interfaces.discord_event_handler import handle_on_message

class DiscordBotClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)

    async def on_ready(self):
        print(f"✅ ログインしました: {self.user}")

    async def on_message(self, message: discord.Message):
        await handle_on_message(message)
