# main.py

import os
import discord
from infrastructure.discord_client import DiscordBotClient

# ローカル開発時のみ .env を使う（本番RailwayではGUIで設定）
if os.getenv("RAILWAY_ENVIRONMENT") is None:
    from dotenv import load_dotenv
    load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = DiscordBotClient(intents=intents)
TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN is None:
    raise ValueError("環境変数 DISCORD_TOKEN が設定されていません")

client.run(TOKEN)
