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


class AdminAddGroupInlineKeyboard:
    def __init__(self):
        self.LINK_BTN = InlineKeyboardButton(text='LINK', callback_data='_link_')
        self.SAVE_BTN = InlineKeyboardButton(text='SAVE', callback_data='_save_')
        self.CANCEL_BTN = InlineKeyboardButton(text='CANCEL', callback_data='_cancel_')

    def get_keyboard(self):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [self.SAVE_BTN],
                [self.CANCEL_BTN],
            ])
        return keyboard


class AdminSelectiveModeInlineKeyboard:
    def __init__(self):
        self.PARS_BTN = InlineKeyboardButton(text='PARS', callback_data='_selective_mode_parse_')
        self.LINK_BTN = InlineKeyboardButton(text='LINK WITH CHANNEL', callback_data='_link_')
        self.DELETE_BTN = InlineKeyboardButton(text='DELETE', callback_data='_delete_')

    def get_keyboard(self, group_id: int):
        self.PARS_BTN.callback_data += str(group_id)
        self.LINK_BTN.callback_data += str(group_id)
        self.DELETE_BTN.callback_data += str(group_id)

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [self.PARS_BTN],
                [self.LINK_BTN],
                [self.DELETE_BTN],
            ])
        return keyboard


class AdminLinkGroupWithChannelKeyboard:
    def __init__(self):
        self.PARS_BTN = InlineKeyboardButton(text='PARS', callback_data='_selective_mode_parse_')
        self.LINK_BTN = InlineKeyboardButton(text='LINK WITH CHANNEL', callback_data='_link_')
        self.DELETE_BTN = InlineKeyboardButton(text='DELETE', callback_data='_delete_')

    def get_keyboard(self, group_id: int):
        self.PARS_BTN.callback_data += str(group_id)
        self.LINK_BTN.callback_data += str(group_id)
        self.DELETE_BTN.callback_data += str(group_id)

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [self.PARS_BTN],
                [self.LINK_BTN],
                [self.DELETE_BTN],
            ])
        return keyboard


def get_admin_link_group_with_channel_keyboard(tg_channel_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='SELECT', callback_data=f'_select_{tg_channel_id}')]
        ]
    )
