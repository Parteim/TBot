from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton

from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message


class ReplyKeyboardPaginator:
    def __init__(self, data_list: list, page_size: int = 9, line_size: int = 3, delete_preview_message: bool = False):
        self._data_list = data_list
        self._page_size = page_size
        self._line_size = line_size
        self._current_page = 0

        self._delete_preview_message = delete_preview_message

    def get_page_size(self):
        return self._page_size

    def set_page_size(self, page_size: int):
        if not isinstance(page_size, int):
            raise ValueError('page_size must be int!')
        self._page_size = page_size

    def _list_btn_serializer(self):
        button_list = []
        for i in range(0, len(self._data_list), self._page_size):
            page_value = self._data_list[i:i + self._page_size]
            page = []
            for j in range(0, len(page_value), self._line_size):
                line = [
                    KeyboardButton(text=str(btn_text)) for btn_text in page_value[j:j + self._line_size]
                ]
                page.append(line)
            button_list.append(page)
        return button_list

    def get_page(self):
        builder = ReplyKeyboardBuilder()
        for line in self._list_btn_serializer()[self._current_page]:
            builder.row(*line)

        builder.row(
            KeyboardButton(text='⬅'),
            KeyboardButton(text='➡'),
        )

        return builder.as_markup(resize_keyboard=True)

    def get_keyboard(self):
        self._current_page = 0
        return self.get_page()

    def get_pagination_handler(self):
        router = Router()

        @router.message(F.text.in_(['⬅', '➡']))
        async def pagination_handler(message: Message, bot: Bot, state: FSMContext):
            await message.delete()
            if message.text == '⬅':
                self._current_page = (self._current_page - 1) if self._current_page - 1 > 0 else 0
            elif message.text == '➡':
                self._current_page = (self._current_page + 1) if len(
                    self._data_list) / self._page_size - 1 > self._current_page else self._current_page
            last_message = await message.answer('showed', reply_markup=self.get_page())
            if self._delete_preview_message:
                data = await state.get_data()
                await state.update_data(message_id=last_message.message_id)
                await bot.delete_message(chat_id=message.chat.id, message_id=int(data.get('message_id')))

        return router
