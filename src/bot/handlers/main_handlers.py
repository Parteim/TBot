from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery, KeyboardButton, ReplyKeyboardMarkup
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.media_group import MediaGroupBuilder

from contextlib import suppress
from aiogram.exceptions import TelegramBadRequest

from src.bot.keyboards.keybiard_paginator import ReplyKeyboardPaginator
from src.bot.utils.commands import Commands
from src.bot.utils.resource import text

# from src.bot.keyboards.main_keyboards import Pagination, get_pagination_kb, PAGE_SIZE

router = Router()

# @router.callback_query(Pagination.filter(F.action.in_(['prev', 'next'])))
# async def pagination_handler(callback: CallbackQuery, callback_data: Pagination):
#     page_num = int(callback_data.page)
#     page = page_num - 1 if page_num > 0 else 0
#     if callback_data.action == 'next':
#         page = page_num + 1 if page_num < (len(smiles) - 1) else page_num
#
#     with suppress(TelegramBadRequest):
#         await callback.message.edit_text('', reply_markup=paginator(page))
#     await callback.answer()

value_list = [i for i in range(23)]

kb = ReplyKeyboardPaginator(value_list)


@router.message(Command(Commands.START_COMMAND.command))
async def start(message: Message, state: FSMContext):
    last_message = await message.answer(text.WELCOME_TEXT, reply_markup=kb.get_keyboard())
    await state.update_data(page=0, message_id=last_message.message_id)


@router.message()
async def all_message(message: Message):
    print(message.from_user)
