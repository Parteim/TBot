from typing import Any

from aiogram.types import (ReplyKeyboardMarkup,
                           KeyboardButton,
                           InlineKeyboardMarkup,
                           InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder


class ReplyKeyboardButton(KeyboardButton):
    def __init__(self, *, text: str, **__pydantic_kwargs: Any):
        super().__init__(text=text, **__pydantic_kwargs)

    def __str__(self):
        return self.text


class AdminPanelKeyboard:
    def __init__(self):
        self.BOT_CONFIG_BTN = ReplyKeyboardButton(text='Bot config')
        self.VK_CONSOLE_BTN = ReplyKeyboardButton(text='VK')
        self.TG_CONSOLE_BTN = ReplyKeyboardButton(text='TG')

    def get_keyboard(self):
        keyboard = ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=[
                [self.BOT_CONFIG_BTN, self.VK_CONSOLE_BTN],
                [self.TG_CONSOLE_BTN],
            ]
        )
        return keyboard


class AdminVkConsoleKeyboard:
    def __init__(self):
        self.GROUP_LIST_BTN = ReplyKeyboardButton(text='group list')
        self.ADD_GROUP_BTN = ReplyKeyboardButton(text='add group')
        self.SELECTIVE_MODE_BTN = ReplyKeyboardButton(text='selective mode')
        self.FAST_PARSE_BTN = ReplyKeyboardButton(text='fast parse')
        self.BACK_BTN = ReplyKeyboardButton(text='cancel')

    def get_keyboard(self):
        keyboard = ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=[
                [self.GROUP_LIST_BTN, self.ADD_GROUP_BTN],
                [self.SELECTIVE_MODE_BTN],
                [self.FAST_PARSE_BTN],
                [self.BACK_BTN]
            ]
        )
        return keyboard


class AdminParseInlineKeyboard:
    def __init__(self):
        self.PARSE_BTN = InlineKeyboardButton(text='PARS', callback_data='_parse_')
        self.PARS_TO_CHANNEL_BTN = InlineKeyboardButton(text='PARS TO CHANNEL', callback_data='_parse_to_channel_')
        self.CANCEL_BTN = InlineKeyboardButton(text='CANCEL', callback_data='_cancel_')

    def get_keyboard(self):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [self.PARSE_BTN],
                [self.PARS_TO_CHANNEL_BTN],
                [self.CANCEL_BTN],
            ])
        return keyboard


class AdminAddGroupInlineKeyBoard:
    def __init__(self):
        self.ADD_BTN = InlineKeyboardButton(text='ADD', callback_data='_add_')
        self.CANCEL_BTN = InlineKeyboardButton(text='CANCEL', callback_data='_cancel_')

    def get_keyboard(self):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [self.ADD_BTN],
                [self.CANCEL_BTN],
            ])
        return keyboard


class SelectiveModeInlineKeyboard:
    def __init__(self):
        self.SELECT_BTN = InlineKeyboardButton(text='SELECT', callback_data='_select_')
        self.CANCEL_BTN = InlineKeyboardButton(text='CANCEL', callback_data='_cancel_')

        self.PARSE_BTN = InlineKeyboardButton(text='PARSE', callback_data='_selective_mode_parse_')
        self.DELETE_BTN = InlineKeyboardButton(text='DELETE', callback_data='_delete_')
        self.SET_TASK_BTN = InlineKeyboardButton(text='SET TASK', callback_data='_set_task_')

        self.PARSE_TO_CHANEL_BTN = InlineKeyboardButton(text='PARSE TO CHANEL', callback_data='_parse_to_channel_')
        self.PARSE_TO_THIS_CHAT_BTN = InlineKeyboardButton(text='PARSE TO THIS CHAT',
                                                           callback_data='_parse_to_this_chat_')

    @staticmethod
    def get_selection_keyboard(group):
        builder = InlineKeyboardBuilder()
        builder.button(text='SELECT', callback_data=f'_select_{group.group_id}')
        return builder.as_markup()

    def get_action_keyboard(self):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [self.PARSE_BTN],
                [self.DELETE_BTN],
                [self.SET_TASK_BTN],
                [self.CANCEL_BTN],
            ]
        )
        return keyboard

    def get_parse_keyboard(self):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [self.PARSE_TO_CHANEL_BTN],
                [self.PARSE_TO_THIS_CHAT_BTN],
                [self.CANCEL_BTN],
            ]
        )
        return keyboard
