from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from src.Bot.admin.keyboards import AdminPanelKeyboard, AdminVkConsoleKeyboard
from src.Bot.admin.resource import text
from src.Bot.admin import AdminCommands

from src.Bot.filters import IsAdmin
from src.Bot.comands import Commands as BotCommands
from src.Bot.states import ParsingStates

router = Router()


@router.message(IsAdmin(), F.text == AdminPanelKeyboard().VK_CONSOLE_BTN.text)
async def vk_console(message: Message):
    await message.answer(text.VK_CONSOLE_TEXT, reply_markup=AdminVkConsoleKeyboard().get_keyboard())


@router.message(IsAdmin(), F.text == AdminVkConsoleKeyboard().FAST_PARSE_BTN.text)
async def parse(message: Message, state: FSMContext):
    await message.answer(text.GET_GROUP_TEXT)
    await state.set_state(ParsingStates.GET_GROUP)


@router.message(IsAdmin(), ParsingStates.GET_GROUP)
async def get_group(message: Message, state: FSMContext):
    domain = message.text.split('/')[-1]
    group = await check_vk_group(VkBot(Config.VK_ACCESS_TOKEN), domain)
    if group:
        if group['is_closed'] == 1:
            await message.answer(text.CLOSED_GROUP_TEXT)
        else:
            await state.update_data(group=group)
            await state.set_state(ParsingStates.GET_COUNT_OF_POSTS)
            await message.answer(text.GET_COUNT_OF_POSTS_TEXT)
    else:
        await message.answer(text.INCORRECT_GROUP_TEXT)
