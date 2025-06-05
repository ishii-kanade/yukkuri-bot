# main.py

import os
from dotenv import load_dotenv
from infrastructure.discord_client import DiscordBotClient
import discord

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = DiscordBotClient(intents=intents)
TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN is None:
    raise ValueError("環境変数 DISCORD_TOKEN が設定されていません")

client.run(TOKEN)
