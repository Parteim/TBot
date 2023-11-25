from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext

from ..text import START_TEXT
from ..keyboards.main_keyboards import main_kb
from ..states import FastParseStates

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    await message.answer(START_TEXT, reply_markup=main_kb)


# @router.message(F.text == 'parsing')
# async def start_parsing(message: Message, states: FSMContext):
#     # await states.set_state(FastParseStates.GET_GROUP_ID)
#     await message.answer('POKA NE RABOTAET')


@router.message(F.text == 'POSOSAT')
async def give_suck(message: Message):
    img_url = 'https://fotosbor.com/files/2019/05/IMGJPEG1558160461PpRzqj/15581604614xw7gt.jpeg'
    await message.answer_photo(img_url)


@router.message(F.text == 'EXTRA_CONTENT')
async def give_extra_content(message: Message):
    await message.answer_sticker('CAACAgIAAxkBAAIEPWVh8qLtdJ4yjSbN4UI1M6LYEFswAAJpHQACXLGZSL-zuoFOc2x6MwQ')


@router.message()
async def handel_all_message(message: Message):
    await message.answer('.!.')
    print(message)
