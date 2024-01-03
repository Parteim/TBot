from aiogram import Bot
from aiogram.types import BotCommandScopeChat, BotCommand

from src.bot.config import Config


class Commands:
    ADMIN_PANEL = BotCommand(command='admin', description='Вызов панели администратора')
    SAVE_CHAT_IN_DB = BotCommand(command='save_chat', description='Добавить текущий чат в базу данных')
    LINK_CHANEL_WITH_GROUP = BotCommand(command='link', description='Связать текущий чат с группой ВК')
    SHOW_ACTIVE_TASKS = BotCommand(command='show_tasks', description='Выводит список текущих задач')

    @classmethod
    async def get_commands(cls):
        class_attributes = vars(cls)
        commands_list = [command for key, command in class_attributes.items() if
                         not key.startswith('_') and key.isupper()]
        return commands_list

    @classmethod
    async def set_commands(cls, bot: Bot):
        await bot.set_my_commands(await cls.get_commands(), BotCommandScopeChat(chat_id=Config.ADMIN_ID))
