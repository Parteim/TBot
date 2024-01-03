from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    await message.answer('Hello')
