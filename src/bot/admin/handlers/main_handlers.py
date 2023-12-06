from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from src.bot.admin.utils.commands import Commands
from src.bot.admin.utils.resource import text
from src.bot.admin.filters import IsAdmin
from src.bot.admin.keyboards import (
    AdminPanelKeyboard,
    AdminVkConsoleKeyboard,
    AdminParseInlineKeyboard,
)
from src.bot.db.db_manager import add_tg_channel, get_tg_channel_by_id

router = Router()


@router.callback_query(F.data == AdminParseInlineKeyboard().CANCEL_BTN.callback_data)
async def cancel(callback: CallbackQuery, state: FSMContext):
    await callback.answer(text.CANCEL_TEXT)
    await state.clear()


@router.message(F.text == AdminVkConsoleKeyboard().BACK_BTN.text)
async def cancel(message: Message, state: FSMContext):
    await message.answer(text.CANCEL_TEXT)
    await state.clear()


@router.message(IsAdmin(), Command(Commands.ADMIN_PANEL.command))
async def show_admin_panel(message: Message, bot: Bot):
    await message.answer(text.ADMIN_PANEL_TEXT, reply_markup=AdminPanelKeyboard().get_keyboard())


@router.channel_post(Command(Commands.SAVE_CHAT_IN_DB.command))
@router.message(IsAdmin(), Command(Commands.SAVE_CHAT_IN_DB.command))
async def save_channel(message: Message, bot: Bot):
    chanel = message.chat
    await add_tg_channel(chanel)
    await message.answer('-DONE-')


@router.channel_post(Command(Commands.LINK_CHANEL_WITH_GROUP.command))
async def link_with_group(message: Message, bot: Bot):
    chanel = message.chat
    check = await get_tg_channel_by_id(chanel.id)
    print(check)
    # await add_tg_channel(chanel)
    await message.answer(str(check))
