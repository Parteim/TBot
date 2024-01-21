import json

from aiogram.utils.media_group import MediaGroupBuilder
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram import Bot
from redis import Redis
from apscheduler_di import ContextSchedulerDecorator

from Bot.config import Config
from Bot.db import VkGroup
from Bot.db.managers import VkGroupManager
from Bot.utils import get_posts

posts_storage = Redis(
    host=Config.REDIS_CONFIG.HOST,
    port=Config.REDIS_CONFIG.PORT,
    db=1,
    decode_responses=Config.REDIS_CONFIG.DECODE_RESPONSE,
)

job_storage = {
    'default': RedisJobStore(
        jobs_key='tasks',
        run_times_key='tasks_running',
        host=Config.REDIS_CONFIG.HOST,
        port=Config.REDIS_CONFIG.PORT,
        db=2,
    )
}
scheduler = ContextSchedulerDecorator(
    AsyncIOScheduler(
        timezone='Europe/Moscow',
        jobstores=job_storage
    )
)


# class BaseTaskManager:
#     def __init__(self):
#         self._job_storage = {
#             'default': RedisJobStore(
#                 jobs_key='tasks',
#                 run_times_key='tasks_running',
#                 host=Config.REDIS_CONFIG.HOST,
#                 port=Config.REDIS_CONFIG.PORT,
#                 db=2,
#             )
#         }
#         self.scheduler = ContextSchedulerDecorator(
#             AsyncIOScheduler(
#                 timezone='Europe/Moscow',
#                 jobstores=self._job_storage
#             )
#         )
#
#     def __call__(self, *args, **kwargs):
#         return self.scheduler


class VkGroupTaskManager:
    db_manager = VkGroupManager

    def __init__(self, group: VkGroup, trigger: str = 'interval'):
        super().__init__()
        self.domain = group.domain
        self.vk_group_id = group.vk_id
        self.db_group_id = group.id
        self._group = group
        self.trigger = trigger
        self.linked_channels_ids = []

    async def _get_linked_channels_ids(self):
        channels = await self.db_manager().get_tg_channels(self.db_group_id)
        return [channel.tg_id for channel in channels]

    async def update_linked_channels_ids(self):
        self.linked_channels_ids = await self._get_linked_channels_ids()

    @staticmethod
    async def _get_post_from_storage(domain: str):
        try:
            posts = json.loads(posts_storage.get(domain))['posts']
        except TypeError:
            await LoadVkGroupPosts().load_posts_for_current_group(domain)
            posts = json.loads(posts_storage.get(domain))['posts']

        post = posts.pop()

        while len(post['attachments']) < 1:
            post = posts.pop()

        posts_storage.set(
            str(domain),
            json.dumps({'posts': posts}),
        )

        return post

    @staticmethod
    async def task(domain: str, channel_id: int, bot: Bot):
        post = await VkGroupTaskManager._get_post_from_storage(domain)
        group_post_images = MediaGroupBuilder()
        for img in post['attachments']:
            group_post_images.add_photo(media=img)
        await bot.send_media_group(channel_id, media=group_post_images.build())

    async def create_post_task(self, seconds: int = 20):
        await self.update_linked_channels_ids()
        scheduler.add_job(
            self.task,
            self.trigger,
            seconds=seconds,
            name=self.domain,
            kwargs={
                'domain': self.domain,
                'channels_ids': self.linked_channels_ids,
            }
        )

    async def create_post_tasks_for_all_channels(self, seconds: int = 20):
        print(scheduler)
        await self.update_linked_channels_ids()
        for channel_id in self.linked_channels_ids:
            scheduler.add_job(
                self.task,
                self.trigger,
                seconds=seconds,
                name=self.domain,
                kwargs={
                    'domain': self.domain,
                    'channel_id': channel_id,
                }
            )


class LoadVkGroupPosts:
    db_manager = VkGroupManager

    def __init__(self, count_of_posts: int = 100):
        self.count_of_posts = count_of_posts
        self.vk_api_token = Config.VK_ACCESS_TOKEN

    async def load_posts_for_all_groups(self):
        groups = await self.db_manager().get_all()
        for group in groups:
            posts = await get_posts(
                vk_bot_token=self.vk_api_token,
                domain=group.domain,
                count_of_posts=self.count_of_posts
            )
            posts_storage.set(
                str(group.domain),
                json.dumps({'posts': posts}),
            )

    async def load_posts_for_current_group(self, current_group: VkGroup | str):
        domain = current_group.domain if isinstance(current_group, VkGroup) else current_group
        posts = await get_posts(
            vk_bot_token=self.vk_api_token,
            domain=domain,
            count_of_posts=self.count_of_posts
        )
        print(posts)
        print(posts)
        posts_storage.set(
            str(domain),
            json.dumps({'posts': posts}),
        )
