from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from src.Bot.comands import Commands
from src.Bot.resource import text

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    await message.answer(text=text.WELCOME_TEXT)


@router.message(Command(Commands.HELP_COMMAND.command))
async def help_handler(message: Message):
    await message.answer(text=text.HELP_TEXT)


@router.message(Command(Commands.CANCEL_COMMAND.command))
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text=text.CANCEL_TEXT)
