from aiogram import Bot
from config import settings

bot: Bot = Bot(settings.TOKEN_BOT)

async def send_notify(user_id: int):
    await bot.send_message(
        chat_id=user_id,
        text=f'Вы получили новое сообщение, перейдите на сайте чтобы посмотреть.'
    )