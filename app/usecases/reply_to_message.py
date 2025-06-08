# app/usecases/reply_to_message.py
from infrastructure.senryu_detector import extract_sequential_senryu
import discord

# 複数のチャンネルIDをリストまたは集合で指定
TARGET_CHANNEL_IDS = {
    767778360133812234,
    965883155544428656,
}

class ReplyToMessageUseCase:
    async def execute(self, message: discord.Message):
        if message.channel.id not in TARGET_CHANNEL_IDS:
            return

        content = message.content.strip()

        # 川柳チェック
        senryu = extract_sequential_senryu(content, True)
        if senryu:
            formatted = "📜 川柳を検知しました\n" + "\n".join(senryu)
            await message.channel.send(formatted)
            return
