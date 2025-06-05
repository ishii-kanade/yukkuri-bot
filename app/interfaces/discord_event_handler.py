# app/interfaces/discord_event_handler.py

import discord
from app.usecases.reply_to_message import ReplyToMessageUseCase

# ここでUseCaseを呼び出す
async def handle_on_message(message: discord.Message):
    if message.author.bot:
        return  # Botの投稿は無視

    # ユースケースに処理を委譲
    await ReplyToMessageUseCase().execute(message)
