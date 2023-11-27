from aiogram.fsm.state import StatesGroup, State


class ParseStates(StatesGroup):
    GET_GROUP_ID = State()
    GET_COUNT_OF_POSTS = State()
    READY_TO_PARSE = State()
