from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from src.Bot.admin.keyboards import AdminPanelKeyboard, AdminVkConsoleKeyboard
from src.Bot.admin.resource import text
from src.Bot.admin import AdminCommands

from src.Bot.filters import IsAdmin
from src.Bot.comands import Commands as BotCommands

router = Router()


@router.message(IsAdmin(), F.text == AdminPanelKeyboard().VK_CONSOLE_BTN.text)
async def vk_console(message: Message):
    await message.answer(text.VK_CONSOLE_TEXT, reply_markup=AdminVkConsoleKeyboard().get_keyboard())
