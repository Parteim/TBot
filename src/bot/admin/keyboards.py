from aiogram.types import ReplyKeyboardMarkup, \
    KeyboardButton, \
    InlineKeyboardMarkup, \
    InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

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

admin_cancel_kb = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [KeyboardButton(text='CANCEL')]
    ]
)

admin_fast_parse_inline_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='PARSE', callback_data='_parse_')],
        [InlineKeyboardButton(text='PARSE TO CHANNEL', callback_data='_parse_to_channel_')],
        [InlineKeyboardButton(text='CANCEL', callback_data='_cancel_')],
    ]
)

admin_add_group_inline_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='ADD', callback_data='_add_group_')],
        [InlineKeyboardButton(text='CANCEL', callback_data='_cancel_')],
    ]
)

selective_mode_instance_group_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='LINK WITH CHANNEL', callback_data='_link_with_channel_')],
        [InlineKeyboardButton(text='REMOVE', callback_data='_remove_')],
    ]
)

selective_mode_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='link with channel'), KeyboardButton(text='parse')],
        [KeyboardButton(text='remove')],
        [KeyboardButton(text='back')]
    ]
)


def sm_get_instance_group_kb(group):
    builder = InlineKeyboardBuilder()
    builder.button(text='SELECT', callback_data=f'_select_{group.id}')
    return builder.as_markup()


def sm_channel_list_kb(channels):
    builder = ReplyKeyboardBuilder()
    for channel in channels:
        builder.button(text=f'{channel.channel_name} id: {channel.channel_id}')
    return builder.as_markup(resize_keyboard=True)
