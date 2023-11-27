from aiogram.fsm.state import StatesGroup, State


class FastParseStates(StatesGroup):
    GET_GROUP_ID = State()
    GET_COUNT_OF_POSTS = State()
    READY_TO_PARSE = State()


class AddVkGroupStates(StatesGroup):
    GET_GROUP_LINK = State()
    READY_TO_ADD = State()


class SelectiveModeState(StatesGroup):
    SELECT_GROUP = State()
    GET_COUNT_OF_POST = State()
    READY_TO_PARSE = State()
