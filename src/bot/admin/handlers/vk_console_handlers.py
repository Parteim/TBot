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
    AdminAddGroupInlineKeyBoard, SelectiveModeInlineKeyboard
)
from src.bot.config import Config
from src.bot.db.db_manager import get_vk_groups, add_vk_group, get_vk_group_by_id

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
    groups = await get_vk_groups()
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
        await add_vk_group((await state.get_data())['group'])
        await callback.answer(text.ADD_GROUP_SUCCESSFUL_CB)
        await callback.message.answer(text.ADD_GROUP_SUCCESSFUL_TEXT)

    except IntegrityError:
        await callback.answer(text.ADD_GROUP_UNIQUE_ERROR_CB)
        await callback.message.answer(text.ADD_GROUP_UNIQUE_ERROR_TEXT)

    await state.clear()


@router.message(IsAdmin(), F.text == AdminVkConsoleKeyboard().SELECTIVE_MODE_BTN.text)
async def selective_mode(message: Message, state: FSMContext):
    groups = await get_vk_groups()
    massages_id = []
    for group in groups:
        answer_message = group.response_message_repr()
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
    group = await get_vk_group_by_id(group_id)
    await state.update_data(group=group)
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
    group = data['group']
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
