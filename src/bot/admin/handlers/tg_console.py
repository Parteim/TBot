from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery

from src.bot.admin.filters import IsAdmin
from src.bot.admin.keyboards import AdminPanelKeyboard, AdminTgConsoleKeyboard

router = Router()


@router.message(IsAdmin(), F.text == AdminPanelKeyboard().TG_CONSOLE_BTN.tex)
async def tg_console(message: Message):
    await message.answer('TG Console', reply_markup=AdminTgConsoleKeyboard().get_keyboard())
