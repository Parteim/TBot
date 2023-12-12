import json

from aiogram.utils.media_group import MediaGroupBuilder
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot
from redis import Redis
from apscheduler_di import ContextSchedulerDecorator

from src.bot.db.models import Base, VkGroup
from src.bot.utils.vk_api.base import Bot as VkBot
from src.bot.config import Config
from src.bot.utils.vk_api.utils.wall import get_posts

posts_storage = Redis(
    host=Config.REDIS_CONFIG.HOST,
    port=Config.REDIS_CONFIG.PORT,
    db=1,
    decode_responses=Config.REDIS_CONFIG.DECODE_RESPONSE,
)


async def load_posts():
    posts = await get_posts(
        bot=VkBot(Config.VK_ACCESS_TOKEN),
        domain='land_of_art',
        count_of_posts=50
    )

    data = json.dumps(
        {'posts': posts}
    )
    posts_storage.set('land_of_art', data)


job_storage = {
    'default': RedisJobStore(
        jobs_key='tasks',
        run_times_key='tasks_running',
        host=Config.REDIS_CONFIG.HOST,
        port=Config.REDIS_CONFIG.PORT,
        db=2,
    )
}

scheduler = ContextSchedulerDecorator(AsyncIOScheduler(timezone='Europe/Moscow', jobstores=job_storage))


class GroupTask:
    def __init__(self, group: VkGroup, trigger: str = 'interval', ):
        self.domain = group.domain
        self.group_id = group.group_id

    async def load_posts(self):
        posts = await get_posts(
            bot=VkBot(Config.VK_ACCESS_TOKEN),
            domain=self.domain,
            count_of_posts=50,
        )
        data = json.dumps(
            {'posts': posts}
        )

        posts_storage.set(self.group_id, data)

    @staticmethod
    async def task(group, bot: Bot):
        posts = json.loads(posts_storage.get(group.group_id))['posts']
        post = posts.pop()

        posts_storage.set(
            group.group_id,
            json.dumps({'posts': posts})
        )

        group_post_images = MediaGroupBuilder()
        if len(post['attachments']) > 0:
            for image in post['attachments']:
                group_post_images.add_photo(media=image)
            await bot.send_message(-1002141893327, text=post['text']) if post['text'] else None
            await bot.send_media_group(-1002141893327, media=group_post_images.build())
        else:
            await bot.send_message(-1002141893327, text="--")

    def create_send_post_task(self):
        scheduler.add_job(GroupTask.task, 'interval', seconds=30, name=self.domain, kwargs={'group': self})
