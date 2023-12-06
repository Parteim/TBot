import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode

from bot.utils.commands import Commands
from bot.admin.utils.commands import Commands as AdminCommands
from bot.config import Config
from bot.handlers.main_handlers import router, kb
from bot.admin.handlers import router as admin_router
from src.bot.db.db_manager import async_main


async def start_bot(bot: Bot):
    await Commands.set_commands(bot)
    await AdminCommands.set_commands(bot)
    await bot.send_message(Config.ADMIN_ID, text='Bot is running')


async def stop_bot(bot: Bot):
    await bot.send_message(Config.ADMIN_ID, text='Bot is stopped')


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    await async_main()

    bot = Bot(token=Config.BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    dp.include_routers(admin_router, router, kb.get_pagination_handler())

    await bot.delete_webhook(drop_pending_updates=True)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
