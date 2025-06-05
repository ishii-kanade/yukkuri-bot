# app/usecases/reply_to_message.py
from infrastructure.senryu_detector import extract_random_senryu

import discord

TARGET_CHANNEL_ID = 965883155544428656  # ← 書き換えてね

class ReplyToMessageUseCase:
    async def execute(self, message: discord.Message):
        if message.channel.id != TARGET_CHANNEL_ID:
            return

        content = message.content.strip()

        # 川柳チェック
        senryu = extract_random_senryu(content)
        if senryu:
            formatted = "📜 川柳を検知しました\n" + "\n".join(senryu)
            await message.channel.send(formatted)
            return
