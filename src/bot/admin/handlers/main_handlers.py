from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from src.bot.admin.states import LinkingStates
from src.bot.admin.utils.commands import Commands
from src.bot.admin.utils.resource import text
from src.bot.admin.filters import IsAdmin
from src.bot.admin.keyboards import (
    AdminPanelKeyboard,
    AdminVkConsoleKeyboard,
    AdminParseInlineKeyboard,
)
from src.bot.db.db_manager import save_tg_channel, get_tg_channel_by_id, update_tg_channel, get_vk_group_by_id
from src.bot.utils.tasks.manager import scheduler

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
    await save_tg_channel(chanel)
    await message.answer('-DONE-')


@router.channel_post(Command(Commands.LINK_CHANEL_WITH_GROUP.command))
async def link_with_group(message: Message, bot: Bot, state: FSMContext):
    chanel = message.chat
    channel_db_instance = await get_tg_channel_by_id(chanel.id)
    if channel_db_instance is None:
        channel_db_instance = await save_tg_channel(chanel)
    await state.update_data(channel_id=chanel.id)
    await message.answer(f'{channel_db_instance}\nNow give me id of vk group')
    await state.set_state(LinkingStates.GET_VK_GROUP_ID)


@router.channel_post(LinkingStates.GET_VK_GROUP_ID)
async def link_get_group_id(message: Message, bot: Bot, state: FSMContext):
    if not message.text.isdigit():
        await message.answer('Id should be integer!')
        return
    channel_id = (await state.get_data())['channel_id']
    group_id = int(message.text)
    chanel = await get_tg_channel_by_id(channel_id)
    group = await get_vk_group_by_id(group_id)
    chanel.vk_group_id = group.id
    await update_tg_channel(chanel)
    await message.answer('-DONE-')
    await state.clear()


@router.message(Command(Commands.SHOW_ACTIVE_TASKS))
async def show_tasks(message: Message):
    for task in scheduler.get_jobs():
        print(task)
        await message.answer(str(task))
