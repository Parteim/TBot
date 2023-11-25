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


@router.message()
async def handel_all_message(message: Message):
    await message.answer('.!.')
    print(message)
