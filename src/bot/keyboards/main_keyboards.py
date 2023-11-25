from aiogram.types import ReplyKeyboardMarkup, \
    KeyboardButton, \
    InlineKeyboardMarkup, \
    InlineKeyboardButton

main_kb = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [KeyboardButton(text='parsing')],
        [KeyboardButton(text='POSOSAT')],
        [KeyboardButton(text='EXTRA_CONTENT')],
    ]
)
