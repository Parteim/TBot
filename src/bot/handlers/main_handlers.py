from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.utils.media_group import MediaGroupBuilder

from src.bot.resources import text
from ..keyboards.main_keyboards import main_kb, parse_inline_kb
from ..states import ParseStates
from ..utils.vk_bot.utils.groups import check_vk_group
from ..utils.vk_bot.utils.wall import get_posts

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(text.START_TEXT, reply_markup=main_kb)


@router.callback_query(F.data == '_cancel_')
async def cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer('ok', reply_markup=main_kb)


@router.message(F.text == 'parsing')
async def parsing(message: Message, state: FSMContext):
    await message.answer(text.PARSING)
    await state.set_state(ParseStates.GET_GROUP_ID)
    await message.answer(text.GET_GROUP_ID_TEXT)


@router.message(ParseStates.GET_GROUP_ID)
async def get_group_id(message: Message, state: FSMContext):
    domain = message.text.split('/')[-1]
    group_data = await check_vk_group(domain)
    if group_data:
        if group_data['is_closed'] == 1:
            await message.answer(text.CLOSED_GROUP_TEXT)
        else:
            await state.update_data(domain=domain)
            await state.update_data(group=group_data)
            await state.set_state(ParseStates.GET_COUNT_OF_POSTS)
            await message.answer(text.GET_COUNT_OF_POSTS_TEXT)
    else:
        await message.answer(text.INCORRECT_GROUP_ID_TEXT)


@router.message(ParseStates.GET_COUNT_OF_POSTS)
async def get_count_of_posts(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(count_of_posts=message.text)
        await state.set_state(ParseStates.READY_TO_PARSE)
        await message.answer(text.READY_TO_PARSE_TEXT)
        # ==
        data = await state.get_data()
        formatted_text = f"id:{data['group']['id']}\n<b>{data['group']['name']}</b>\n" \
                         f"count of posts:{data['count_of_posts']}"
        await message.answer_photo(
            data['group']['photo_200'],
            formatted_text,
            reply_markup=parse_inline_kb,
        )
        # ==
    else:
        await message.answer(text.INCORRECT_COUNT_OF_POSTS)


@router.callback_query(F.data == '_parse_')
async def run_parsing(callback: CallbackQuery, state: FSMContext):
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
            continue
    await state.clear()
