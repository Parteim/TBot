from aiogram.types import (ReplyKeyboardMarkup,
                           KeyboardButton,
                           InlineKeyboardMarkup,
                           InlineKeyboardButton)


class AdminPanelKeyboard:
    def __init__(self):
        self.BOT_CONFIG_BTN = KeyboardButton(text='Bot config')
        self.VK_CONSOLE_BTN = KeyboardButton(text='VK')
        self.TG_CONSOLE_BTN = KeyboardButton(text='TG')

    def get_keyboard(self):
        return ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=[
                [self.BOT_CONFIG_BTN, self.VK_CONSOLE_BTN],
                [self.TG_CONSOLE_BTN],
            ]
        )


class AdminVkConsoleKeyboard:
    def __init__(self):
        self.GROUP_LIST_BTN = KeyboardButton(text='group list')
        self.ADD_GROUP_BTN = KeyboardButton(text='add group')
        self.SELECTIVE_MODE_BTN = KeyboardButton(text='selective mode')
        self.FAST_PARSE_BTN = KeyboardButton(text='fast parse')
        self.BACK_BTN = KeyboardButton(text='cancel')

    def get_keyboard(self):
        return ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=[
                [self.GROUP_LIST_BTN, self.ADD_GROUP_BTN],
                [self.SELECTIVE_MODE_BTN],
                [self.FAST_PARSE_BTN],
                [self.BACK_BTN]
            ]
        )
