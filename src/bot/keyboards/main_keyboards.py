from aiogram.types import (ReplyKeyboardMarkup,
                           KeyboardButton,
                           InlineKeyboardMarkup,
                           InlineKeyboardButton)

from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from aiogram.filters.callback_data import CallbackData


class Pagination(CallbackData, prefix='pag'):
    action: str
    page: int


# def paginator(page: int = 0):
#     builder = InlineKeyboardBuilder()
#     builder.row(
#         InlineKeyboardButton(text='⬅', callback_data=Pagination(action='prev', page=page).pack()),
#         InlineKeyboardButton(text='➡', callback_data=Pagination(action='next', page=page).pack()),
#         width=2
#     )
#     return builder.as_markup()

PAGE_SIZE = 9


def get_btn_list(v_list, page_size=PAGE_SIZE):
    btn_list = []
    for i in range(0, len(v_list), page_size):
        page = []
        for value in v_list[i:i + page_size]:
            page.append(
                # KeyboardButton(text=str(value))
                value
            )
        btn_list.append(page)
    return btn_list


def get_pagination_kb(v_list, page):
    btn_list = get_btn_list(v_list)[page]
    builder = ReplyKeyboardBuilder()
    for i in range(0, len(btn_list), 3):
        line = []
        for btn in btn_list[i:i + 3]:
            line.append(
                KeyboardButton(text=str(btn))
            )
        builder.row(*line)

    builder.row(
        KeyboardButton(text='⬅'),
        KeyboardButton(text='➡'),
    )
    return builder.as_markup(resize_keyboard=True)

# for value in value_list:
#     page = []
#     for i in range(page_size):
#         page.append(
#             # KeyboardButton(text=str(value))
#             value
#         )
#     btn_list.append(page)
#     print(page)
# return btn_list


# smiles = [
#     KeyboardButton(text='😊'),
#     KeyboardButton(text='😘'),
#     KeyboardButton(text='😂'),
#     KeyboardButton(text='😎'),
# ]
#
# page_size = 3
# pages = [smiles[i:i + page_size] for i in range(0, len(smiles), page_size)]
#
# current_page = 0
#
# smile_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
# smile_keyboard.add(*pages[current_page])
