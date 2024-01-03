from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.media_group import MediaGroupBuilder

from src.bot.admin.utils.resource import text
from src.bot.admin.filters import IsAdmin
from src.bot.admin.states import ParsingStates, AddVkGroupStates, SelectiveModeStates
from src.bot.admin.keyboards import (
    AdminPanelKeyboard,
    AdminVkConsoleKeyboard,
    AdminParseInlineKeyboard,
    AdminAddGroupInlineKeyBoard, SelectiveModeInlineKeyboard, get_link_channel_kb
)
from src.bot.config import Config
# from src.bot.db.db_manager import get_vk_groups, add_vk_group, get_vk_group_by_id, get_tg_channel_list, \
#     get_tg_channel_by_id, update_vk_group
from src.bot.db.db_manager import VkGroupManager, TGChannelManager
from src.bot.utils.tasks.manager import GroupTask

from src.bot.utils.vk_api.utils.groups import check_vk_group
from src.bot.utils.vk_api.base import Bot as VkBot
from src.bot.utils.vk_api.utils.wall import get_posts

from sqlalchemy.exc import IntegrityError

router = Router()


def data_group_response_message(group):
    formatted_text = f'<b>{group["name"]}</b>\n' \
                     f'id: {group["id"]}\n' \
                     f'domain: {group["screen_name"]}'
    photo = group['photo_200']
    return photo, formatted_text


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
    # check group
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


@router.message(IsAdmin(), ParsingStates.GET_COUNT_OF_POSTS)
async def get_count_of_posts(message: Message, state: FSMContext):
    if message.text.isdigit():
        await message.answer(text.READY_TO_PARSE_TEXT)
        await state.update_data(count_of_posts=message.text)
        await message.answer_photo(
            *data_group_response_message((await state.get_data())['group']),
            reply_markup=AdminParseInlineKeyboard().get_keyboard()
        )
    else:
        await message.answer(text.INCORRECT_COUNT_OF_POSTS)


@router.callback_query(F.data == AdminParseInlineKeyboard().PARSE_BTN.callback_data)
async def run_parsing(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer(text.PARSING_PROCESS)
    await state.set_state(ParsingStates.PARSING_PROCESS)

    data = await state.get_data()
    posts = await get_posts(
        VkBot(Config.VK_ACCESS_TOKEN),
        domain=data['group']['screen_name'],
        count_of_posts=int(data['count_of_posts'])
    )
    for post in posts:
        if await state.get_state() == ParsingStates.PARSING_PROCESS:
            group_post_images = MediaGroupBuilder()
            if len(post['attachments']) > 0:
                for image in post['attachments']:
                    group_post_images.add_photo(media=image)
                await callback.message.answer(post['text']) if post['text'] else None
                await callback.message.answer_media_group(media=group_post_images.build())
            else:
                await callback.message.answer('--')
        else:
            break
    await callback.message.answer(text.PARSING_COMPLETE)
    await state.clear()


# =========================================

@router.message(F.text == AdminVkConsoleKeyboard().GROUP_LIST_BTN.text)
async def group_list(message: Message):
    groups = await VkGroupManager().get_all()
    response_text = '\n\n'.join(f'➡{group}' for group in groups)
    await message.answer(response_text)


@router.message(F.text == AdminVkConsoleKeyboard().ADD_GROUP_BTN.text)
async def add_group(message: Message, state: FSMContext):
    await message.answer(text.GET_GROUP_TEXT)
    await state.set_state(AddVkGroupStates.GET_GROUP)


@router.message(IsAdmin(), AddVkGroupStates.GET_GROUP)
async def get_group(message: Message, state: FSMContext):
    domain = message.text.split('/')[-1]
    group = await check_vk_group(VkBot(Config.VK_ACCESS_TOKEN), domain)
    if group:
        if group['is_closed'] == 1:
            await message.answer(text.CLOSED_GROUP_TEXT)
        else:
            await state.update_data(group=group)
            await state.set_state(AddVkGroupStates.READY_TO_ADD)
            await message.answer_photo(
                *data_group_response_message(group),
                reply_markup=AdminAddGroupInlineKeyBoard().get_keyboard()
            )
    else:
        await message.answer(text.INCORRECT_GROUP_TEXT)


@router.callback_query(IsAdmin(), AddVkGroupStates.READY_TO_ADD,
                       F.data == AdminAddGroupInlineKeyBoard().ADD_BTN.callback_data)
async def add_group_in_db(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    try:
        group_data = (await state.get_data())['group']
        group = VkGroupManager.model(
            vk_id=group_data['id'],
            domain=group_data['screen_name'],
            name=group_data['name'],
            is_closed=group_data['is_closed'],
            logo=group_data['photo_200'],
        )
        await VkGroupManager().create(group)
        # await add_vk_group((await state.get_data())['group'])
        await callback.answer(text.ADD_GROUP_SUCCESSFUL_CB)
        await callback.message.answer(text.ADD_GROUP_SUCCESSFUL_TEXT)

    except IntegrityError:
        await callback.answer(text.ADD_GROUP_UNIQUE_ERROR_CB)
        await callback.message.answer(text.ADD_GROUP_UNIQUE_ERROR_TEXT)

    await state.clear()


@router.message(IsAdmin(), F.text == AdminVkConsoleKeyboard().SELECTIVE_MODE_BTN.text)
async def selective_mode(message: Message, state: FSMContext):
    groups = await VkGroupManager().get_all()
    massages_id = []
    for group in groups:
        print(group)
        answer_message = group.response_message_repr()
        print(answer_message)
        answered_message = await message.answer_photo(
            *answer_message,
            reply_markup=SelectiveModeInlineKeyboard().get_selection_keyboard(group)
        )
        massages_id.append(answered_message.message_id)
    await state.update_data(massages_id=massages_id)


@router.callback_query(IsAdmin(), F.data.startswith('_select_'))
async def select_group(callback: CallbackQuery, bot: Bot, state: FSMContext):
    for message_id in (await state.get_data())['massages_id']:
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=int(message_id))
    group_id = callback.data.split('_')[-1]
    print(group_id)
    group = await VkGroupManager().get_by_id(group_id)
    print(group)
    await state.update_data(group_id=group.vk_id)
    message_answer = group.response_message_repr()
    selected_group_massage = await callback.message.answer_photo(
        *message_answer,
        reply_markup=SelectiveModeInlineKeyboard().get_action_keyboard()
    )
    await state.update_data(selected_group_massage_id=selected_group_massage.message_id)
    await state.set_state(SelectiveModeStates.GROUP_SELECTED)


@router.callback_query(IsAdmin(), F.data == SelectiveModeInlineKeyboard().PARSE_BTN.callback_data)
async def parse(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await callback.message.answer(text.GET_COUNT_OF_POSTS_TEXT)
    await state.set_state(SelectiveModeStates.GET_COUNT_OF_POSTS)


@router.message(IsAdmin(), SelectiveModeStates.GET_COUNT_OF_POSTS)
async def get_count_of_posts(message: Message, state: FSMContext, bot: Bot):
    await message.delete()
    selected_group_massage_id = (await state.get_data())['selected_group_massage_id']
    if message.text.isdigit():
        await message.answer(text.READY_TO_PARSE_TEXT)
        await state.update_data(count_of_posts=message.text)
        await state.set_state(SelectiveModeStates.READY_TO_PARSE)
        await bot.edit_message_reply_markup(
            chat_id=message.chat.id,
            message_id=selected_group_massage_id,
            reply_markup=SelectiveModeInlineKeyboard().get_parse_keyboard(),
        )
    else:
        await message.answer(text.INCORRECT_COUNT_OF_POSTS)


@router.callback_query(IsAdmin(),
                       F.data == SelectiveModeInlineKeyboard().PARSE_TO_THIS_CHAT_BTN.callback_data,
                       SelectiveModeStates.READY_TO_PARSE)
async def parse_to_this_chat(callback: CallbackQuery, bot: Bot, state: FSMContext):
    await callback.answer(text.PARSING_PROCESS)
    await state.set_state(SelectiveModeStates.PARSING_PROCESS)

    data = await state.get_data()
    group = await VkGroupManager().get_by_id(data['group_id'])
    posts = await get_posts(
        VkBot(Config.VK_ACCESS_TOKEN),
        domain=group.domain,
        count_of_posts=int(data['count_of_posts'])
    )
    for post in posts:
        if await state.get_state() == SelectiveModeStates.PARSING_PROCESS:
            group_post_images = MediaGroupBuilder()
            if len(post['attachments']) > 0:
                for image in post['attachments']:
                    group_post_images.add_photo(media=image)
                await callback.message.answer(post['text']) if post['text'] else None
                await callback.message.answer_media_group(media=group_post_images.build())
            else:
                await callback.message.answer('--')
        else:
            break
    await callback.message.answer(text.PARSING_COMPLETE)
    await state.clear()


# @router.callback_query(IsAdmin(), F.data == SelectiveModeInlineKeyboard().PARSE_TO_CHANEL_BTN.callback_data)
@router.callback_query(IsAdmin(), F.data == SelectiveModeInlineKeyboard().SET_TASK_BTN.callback_data)
async def set_task(callback: CallbackQuery, bot: Bot, state: FSMContext):
    group_id = (await state.get_data())['group_id']
    group = await VkGroupManager().get_by_id(group_id)
    group_task_manager = GroupTask(group)
    await group_task_manager.load_posts()
    group_task_manager.create_send_post_task()
    await callback.answer('task created')


@router.callback_query(IsAdmin(), F.data == SelectiveModeInlineKeyboard().LINK_WITH_CHANNEL_BTN.callback_data)
async def link_with_channel(callback: CallbackQuery, bot: Bot, state: FSMContext):
    channel_list = await TGChannelManager().get_all()

    for channel in channel_list:
        await callback.message.answer(str(channel), reply_markup=get_link_channel_kb(channel))


@router.callback_query(IsAdmin(), F.data.startswith('_link_'))
async def link(callback: CallbackQuery, bot: Bot, state: FSMContext):
    tg_channel = await TGChannelManager().get_by_id(callback.data.split('_')[-1])
    group = await VkGroupManager().get_by_id((await state.get_data())['group_id'])
    print('=' * 10, group)
    print('=' * 10, tg_channel)
    print(tg_channel.id)
    group.tg_channel_id = tg_channel.id
    await VkGroupManager().update(group)
    await callback.answer('-DONE-')


""" user_id 123412 date_time: 341242141 city: Moscow temp: 21C """
