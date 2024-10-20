from aiogram import Bot, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state
from aiogram.types import (

    Message,
)


from config import settings


router: Router = Router()

bot: Bot = Bot(settings.TOKEN_BOT, default=DefaultBotProperties(parse_mode="HTML"))


@router.message(StateFilter(default_state))
async def echo(message: Message):
    await message.answer(text=f'Ваш ID: <b>{message.from_user.id}</b>\nВставьте его на сайте')
