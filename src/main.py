import asyncio
import logging
import json

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.context import FSMContext

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler_di import ContextSchedulerDecorator

from bot.utils.commands import Commands
from bot.admin.utils.commands import Commands as AdminCommands
from bot.config import Config
from bot.handlers.main_handlers import router, kb
from bot.admin.handlers import router as admin_router
from src.bot.db.db_manager import main as m
from src.bot.utils.tasks.manager import scheduler, load_posts


async def start_bot(bot: Bot):
    await Commands.set_commands(bot)
    await AdminCommands.set_commands(bot)
    await bot.send_message(Config.ADMIN_ID, text='Bot is running')
    await m()
    await load_posts()


async def stop_bot(bot: Bot):
    await bot.send_message(Config.ADMIN_ID, text='Bot is stopped')
    await reset_jobs()


async def reset_jobs():
    # Останавливаем планировщик
    scheduler.shutdown(wait=True)

    # Удаляем все текущие задачи
    scheduler.remove_all_jobs()

    # Перезапускаем планировщик
    scheduler.start()


async def main() -> None:
    logging.basicConfig(level=logging.INFO)

    storage = RedisStorage.from_url(Config.REDIS_CONFIG.get_url())

    bot = Bot(token=Config.BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=storage)
    scheduler.ctx.add_instance(bot, declared_class=Bot)

    scheduler.start()

    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    dp.include_routers(admin_router, router)
    # dp.include_routers(admin_router, router, kb.get_pagination_handler())

    await bot.delete_webhook(drop_pending_updates=True)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
