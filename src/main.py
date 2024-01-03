import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from Bot.config import Config


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    bot = Bot(Config.BOT_TOKEN, parse_mode=ParseMode.MARKDOWN_V2)
    dp = Dispatcher()

    # dp.include_routers()

    await bot.delete_webhook(drop_pending_updates=True)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
