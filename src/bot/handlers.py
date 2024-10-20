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


@router.message(Command(commands="cancel"), StateFilter(default_state))
async def process_cancel_command(message: Message):
    await message.answer(text="Отменять нечего.\n\n" "Отправьте команду /new")
