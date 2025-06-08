# app/usecases/reply_to_message.py
from infrastructure.senryu_detector import SenryuExtractor
import discord

# 複数のチャンネルIDをリストまたは集合で指定
TARGET_CHANNEL_IDS = {
    767778360133812234,
    965883155544428656,
    713763994690650193
}

class ReplyToMessageUseCase:
    def __init__(self):
        self.extractor = SenryuExtractor()

    async def execute(self, message: discord.Message):
        if message.channel.id not in TARGET_CHANNEL_IDS:
            return

        content = message.content.strip()

        senryu = self.extractor.extract(content, debug=True)
        if senryu:
            formatted = "📜 川柳を検知しました\n" + "\n".join(senryu)
            await message.channel.send(formatted)
