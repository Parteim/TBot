import time
from src.bot.db.models import VkGroup, engin, TgChannel
from sqlalchemy.orm import Session

from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramRetryAfter
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.media_group import MediaGroupBuilder

from src.bot.admin.keyboards import admin_panel_kb, admin_vk_kb, admin_fast_parse_inline_kb, admin_cancel_kb, \
    admin_add_group_inline_kb, selective_mode_kb, sm_get_instance_group_kb, sm_channel_list_kb
from src.bot.admin.resurces import text
from src.bot.admin.states import FastParseStates, AddVkGroupStates, SelectiveModeState
from src.bot.admin.filters import IsAdmin

from src.bot.utils.vk_bot.utils.groups import check_vk_group
from src.bot.utils.vk_bot.utils.wall import get_posts

router = Router()


def format_to_str_group_data(data):
    return f"id:{data['id']}\n<b>{data['name']}</b>\n" \
           f"domain: {data['screen_name']}"


@router.message(IsAdmin(), Command('admin'))
async def show_admin_panel(message: Message):
    await message.answer(text.GET_ADMIN_PANEL_TEXT, reply_markup=admin_panel_kb)


@router.message(IsAdmin(), F.text == 'back')
@router.message(IsAdmin(), F.text == 'CANCEL')
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('ok', reply_markup=admin_panel_kb)


@router.callback_query(IsAdmin(), F.data == '_cancel_')
async def fp_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer('ok', reply_markup=admin_panel_kb)


@router.message(IsAdmin(), F.text == 'VK')
async def vk_console(message: Message):
    await message.answer(text.VK_CONSOLE, reply_markup=admin_vk_kb)


@router.message(IsAdmin(), F.text == 'fast parse')
async def fast_parse(message: Message, state: FSMContext):
    await message.answer(text.FAST_PARSE)
    await state.set_state(FastParseStates.GET_GROUP_ID)
    await message.answer(text.GET_GROUP_ID_TEXT)


@router.message(IsAdmin(), FastParseStates.GET_GROUP_ID)
async def fp_get_group_id(message: Message, state: FSMContext):
    domain = message.text.split('/')[-1]
    group_data = await check_vk_group(domain)
    if group_data:
        if group_data['is_closed'] == 1:
            await message.answer(text.CLOSED_GROUP_TEXT)
        else:
            await state.update_data(domain=domain)
            await state.update_data(group=group_data)
            await state.set_state(FastParseStates.GET_COUNT_OF_POSTS)
            await message.answer(text.GET_COUNT_OF_POSTS_TEXT)
    else:
        await message.answer(text.INCORRECT_GROUP_ID_TEXT)


@router.message(IsAdmin(), FastParseStates.GET_COUNT_OF_POSTS)
async def fp_get_count_of_posts(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(count_of_posts=message.text)
        await state.set_state(FastParseStates.READY_TO_PARSE)
        await message.answer(text.READY_TO_PARSE_TEXT)
        # ==
        data = await state.get_data()
        formatted_text = format_to_str_group_data(data['group']) + f"\ncount of posts:{data['count_of_posts']}"
        await message.answer_photo(
            data['group']['photo_200'],
            formatted_text,
            reply_markup=admin_fast_parse_inline_kb,
        )
        # ==
    else:
        await message.answer(text.INCORRECT_COUNT_OF_POSTS)


@router.callback_query(IsAdmin(), F.data == '_parse_')
async def fp_run(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(text.PARSING_PROCESS)
    data = await state.get_data()
    posts = await get_posts(data['domain'], int(data['count_of_posts']))
    for post in posts:
        group_post_images = MediaGroupBuilder()
        if len(post['attachments']) > 0:
            for image in post['attachments']:
                group_post_images.add_photo(media=image)
            await callback.message.answer(post['text']) if post['text'] else None
            await callback.message.answer_media_group(media=group_post_images.build())
        else:
            await callback.message.answer('--')
    await callback.answer(text.PARSING_COMPLETE)
    await state.clear()


@router.callback_query(IsAdmin(), F.data == '_parse_to_channel_')
async def fp_run_pars_to_channel(callback: CallbackQuery, state: FSMContext, bot: Bot):
    channel_id = -1002141893327
    data = await state.get_data()
    posts = await get_posts(data['domain'], int(data['count_of_posts']))
    await callback.message.delete()
    for post in posts:
        group_post_images = MediaGroupBuilder()
        if len(post['attachments']) > 0:
            for image in post['attachments']:
                group_post_images.add_photo(media=image)
            try:
                await bot.send_media_group(channel_id, media=group_post_images.build())
            except TelegramRetryAfter:
                time.sleep(120)
                await bot.send_media_group(channel_id, media=group_post_images.build())
        else:
            continue
    await callback.answer(text.PARSING_COMPLETE)
    await callback.message.answer(text.PARSING_COMPLETE)
    await state.clear()


@router.message(IsAdmin(), Command('add_group'))
@router.message(IsAdmin(), F.text == 'add group')
async def add_group(message: Message, state: FSMContext):
    await message.answer(text.GET_GROUP_ID_TEXT, reply_markup=admin_cancel_kb)
    await state.set_state(AddVkGroupStates.GET_GROUP_LINK)


@router.message(IsAdmin(), AddVkGroupStates.GET_GROUP_LINK)
async def get_group(message: Message, state: FSMContext):
    domain = message.text.split('/')[-1]
    data = await check_vk_group(domain)
    if data:
        if data['is_closed'] == 1:
            await message.answer(text.CLOSED_GROUP_TEXT)
        else:
            await state.update_data(group=data)
            await state.set_state(AddVkGroupStates.READY_TO_ADD)
            await message.answer_photo(
                data['photo_200'],
                format_to_str_group_data(data),
                reply_markup=admin_add_group_inline_kb,
            )
    else:
        await message.answer(text.INCORRECT_GROUP_ID_TEXT)


@router.callback_query(IsAdmin(), AddVkGroupStates.READY_TO_ADD, F.data == '_add_group_')
async def save_in_db(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    with Session(bind=engin) as session:
        group = VkGroup(
            group_id=int(data['group']['id']),
            domain=data['group']['screen_name'],
            group_name=data['group']['name'],
            is_closed=True if int(data['group']['is_closed']) == 1 else False,
            logo=data['group']['photo_200'],
        )
        session.add(group)
        session.commit()

        group = session.query(VkGroup).filter_by(id=1).first()
        print(group)
        await callback.message.delete()
        await callback.answer(text.GROUP_ADDED)
        await callback.message.answer(str(group), reply_markup=admin_vk_kb)
        await state.clear()


@router.message(IsAdmin(), F.text == 'group list')
async def group_list(message: Message):
    with Session(bind=engin) as session:
        groups = session.query(VkGroup).all()

        for group in groups:
            await message.answer(str(group))


@router.message(IsAdmin(), F.text == 'selective mode')
async def selective_mode(message: Message):
    with Session(bind=engin) as session:
        groups = session.query(VkGroup).all()

        for group in groups:
            await message.answer(str(group), reply_markup=sm_get_instance_group_kb(group))


@router.callback_query(IsAdmin(), F.data.startswith('_select_'))
async def select_group(callback: CallbackQuery, state: FSMContext):
    group_id = int(callback.data.split('_')[-1])
    await state.set_state(SelectiveModeState.SELECT_GROUP)
    await state.update_data(group_id=group_id)
    with Session(bind=engin) as session:
        group = session.query(VkGroup).get(group_id)
        group_data = await check_vk_group(group.domain)
        await state.update_data(domain=group.domain)
        await state.update_data(group=group_data)
        await callback.message.answer_photo(
            group.logo,
            f'{format_to_str_group_data(group_data)}',
            reply_markup=selective_mode_kb,
        )


@router.message(IsAdmin(), SelectiveModeState.SELECT_GROUP)
async def selective_mode_parse(message: Message, state: FSMContext):
    await state.set_state(SelectiveModeState.GET_COUNT_OF_POST)
    await message.answer(text.GET_COUNT_OF_POSTS_TEXT)


@router.message(IsAdmin(), SelectiveModeState.GET_COUNT_OF_POST)
async def selective_mode_parse(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(count_of_posts=message.text)
        await state.set_state(SelectiveModeState.READY_TO_PARSE)
        await message.answer(text.READY_TO_PARSE_TEXT)
        # ==
        data = await state.get_data()
        formatted_text = format_to_str_group_data(data['group']) + f"\ncount of posts:{data['count_of_posts']}"
        await message.answer_photo(
            data['group']['photo_200'],
            formatted_text,
            reply_markup=admin_fast_parse_inline_kb,
        )
        # ==
    else:
        await message.answer(text.INCORRECT_COUNT_OF_POSTS)


@router.channel_post(Command('get_current_chat_id'))
@router.message(IsAdmin(), Command('get_current_chat_id'))
async def handle_all_message(message: Message):
    print(message)
    await message.answer(str(message.chat.id))
