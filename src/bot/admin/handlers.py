from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.media_group import MediaGroupBuilder

from .keyboards import admin_panel_kb, admin_vk_kb, admin_fast_parse_inline_kb
from . import text
from ..states import FastParseStates
from .filters import IsAdmin

# from ..config import Config
# from ..utils.vk_bot.Base import Bot as VKBot
# from ..utils.vk_bot.Base import Wall, Groups
from ..utils.vk_bot.utils.groups import check_vk_group
from ..utils.vk_bot.utils.wall import get_posts

router = Router()


@router.message(IsAdmin(), Command('admin'))
async def show_admin_panel(message: Message):
    await message.answer(text.GET_ADMIN_PANEL_TEXT, reply_markup=admin_panel_kb)


@router.message(IsAdmin(), F.text == 'CANCEL')
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('ok', reply_markup=admin_panel_kb)


@router.callback_query(F.data == '_cancel_')
@router.callback_query(IsAdmin(), F.data == '_cancel_')
async def fp_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer('ok', reply_markup=admin_panel_kb)


@router.message(IsAdmin(), F.text == 'VK')
async def vk_console(message: Message):
    await message.answer(text.VK_CONSOLE, reply_markup=admin_vk_kb)


@router.message(F.text == 'parsing')
@router.message(IsAdmin(), F.text == 'fast parse')
async def fast_parse(message: Message, state: FSMContext):
    await message.answer(text.FAST_PARSE)
    await state.set_state(FastParseStates.GET_GROUP_ID)
    await message.answer(text.GET_GROUP_ID_TEXT)


@router.message(FastParseStates.GET_GROUP_ID)
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


@router.message(FastParseStates.GET_COUNT_OF_POSTS)
@router.message(IsAdmin(), FastParseStates.GET_COUNT_OF_POSTS)
async def fp_get_count_of_posts(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(count_of_posts=message.text)
        await state.set_state(FastParseStates.READY_TO_PARSE)
        await message.answer(text.READY_TO_PARSE_TEXT)
        # ==
        data = await state.get_data()
        formatted_text = f"id:{data['group']['id']}\n<b>{data['group']['name']}</b>\n" \
                         f"count of posts:{data['count_of_posts']}"
        await message.answer_photo(
            data['group']['photo_200'],
            formatted_text,
            reply_markup=admin_fast_parse_inline_kb,
        )
        # ==
    else:
        await message.answer(text.INCORRECT_COUNT_OF_POSTS)


@router.callback_query(F.data == '_parse_')
@router.callback_query(IsAdmin(), F.data == '_parse_')
async def fp_run_(callback: CallbackQuery, state: FSMContext):
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
    await state.clear()
