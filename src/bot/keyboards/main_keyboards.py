from aiogram.types import ReplyKeyboardMarkup, \
    KeyboardButton, \
    InlineKeyboardMarkup, \
    InlineKeyboardButton

main_kb = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [KeyboardButton(text='parsing')],
    ]
)
parse_inline_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='PARSE', callback_data='_parse_')],
        [InlineKeyboardButton(text='CANCEL', callback_data='_cancel_')],
    ]
)
