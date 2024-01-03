import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from Bot.config import Config
from Bot.handlers import main_router
from Bot.filters import BotCommands


async def bot_start(bot: Bot) -> None:
    await BotCommands.set_commands(bot)

    await bot.send_message(Config.ADMIN_ID, text='Bot is running')


async def bot_stop(bot: Bot) -> None:
    await bot.send_message(Config.ADMIN_ID, text='Bot is stopped')


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    bot = Bot(Config.BOT_TOKEN, parse_mode=ParseMode.MARKDOWN_V2)
    dp = Dispatcher()

    dp.startup.register(bot_start)
    dp.shutdown.register(bot_stop)

    dp.include_routers(main_router)

    await bot.delete_webhook(drop_pending_updates=True)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
