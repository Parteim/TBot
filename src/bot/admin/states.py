from aiogram.fsm.state import StatesGroup, State


class GetWeatehr(StatesGroup):
    GET_CITY = State()
    CHOOCE_WEATHER = State()


class ParsingStates(StatesGroup):
    GET_GROUP = State()
    GET_COUNT_OF_POSTS = State()
    READY_TO_PARSE = State()
    PARSING_PROCESS = State()


class AddVkGroupStates(StatesGroup):
    GET_GROUP = State()
    READY_TO_ADD = State()


class SelectiveModeStates(StatesGroup):
    GROUP_SELECTED = State()

    # parsing
    GET_COUNT_OF_POSTS = State()

    READY_TO_PARSE = State()

    PARSE_TO_THIS_CHAT = State()
    PARSE_TO_CHANEL = State()

    PARSING_PROCESS = State()


class LinkingStates(StatesGroup):
    GET_TG_CHANNEL_ID = State()
    GET_VK_GROUP_ID = State()
