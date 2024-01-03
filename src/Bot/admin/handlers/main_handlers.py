from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from src.Bot.admin.keyboards import AdminPanelKeyboard
from src.Bot.admin.resource import text
from src.Bot.admin import AdminCommands

from src.Bot.filters import IsAdmin
from src.Bot.comands import Commands as BotCommands

router = Router()


@router.message(Command(BotCommands.CANCEL_COMMAND.command))
async def cancel_handler(ctx: Message | CallbackQuery, state: FSMContext):
    await state.clear()
    await ctx.answer(text=text.CANCEL_TEXT)


@router.message(IsAdmin(), Command(AdminCommands.ADMIN_PANEL.command))
async def show_admin_panel(message: Message):
    await message.answer(text.ADMIN_PANEL_TEXT, reply_markup=AdminPanelKeyboard().get_keyboard())
