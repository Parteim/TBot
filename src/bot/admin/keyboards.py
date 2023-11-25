from aiogram.types import ReplyKeyboardMarkup, \
    KeyboardButton, \
    InlineKeyboardMarkup, \
    InlineKeyboardButton

admin_panel_kb = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [KeyboardButton(text='bot config'), KeyboardButton(text='VK')],
        [KeyboardButton(text='TG')],
    ]
)

admin_vk_kb = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [KeyboardButton(text='group list'), KeyboardButton(text='add group')],
        [KeyboardButton(text='selective mode'), KeyboardButton(text='select group')],
        [KeyboardButton(text='fast parse')],
        [KeyboardButton(text='back')]
    ]
)

admin_fast_parse_inline_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='PARSE', callback_data='_parse_')],
        [InlineKeyboardButton(text='CANCEL', callback_data='_cancel_')],
    ]
)
