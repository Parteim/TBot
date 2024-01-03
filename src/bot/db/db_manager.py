import asyncio

from .models import TgChannel, User, VkGroup, VkPost, Base
from sqlalchemy import select, ScalarResult
import sqlalchemy
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from src.bot.config import Config

engin = create_async_engine(Config.DB_URL, echo=True)

async_session = async_sessionmaker(engin)


class BaseManager:
    model = None

    def __init__(self):  # class model
        self._engin = create_async_engine(Config.DB_URL, echo=True)
        self._async_session = async_sessionmaker(self._engin)

    async def get(self, pk):
        async with self._async_session() as session:
            obj = await session.scalar(select(self.model).where(self.model.id == pk))
            return obj

    async def get_all(self):
        async with self._async_session() as session:
            result = await session.scalars(select(self.model))
            return result

    async def create(self, obj):
        async with self._async_session() as session:
            session.add(obj)
            await session.commit()

    async def update(self, obj):
        async with self._async_session() as session:
            session.add(obj)
            await session.commit()


class VkGroupManager(BaseManager):
    model = VkGroup

    async def get_by_id(self, group_id):
        async with self._async_session() as session:
            group: ScalarResult = await session.scalar(select(self.model).where(self.model.vk_id == group_id))
            return group


class TGChannelManager(BaseManager):
    model = TgChannel

    async def get_by_id(self, channel_id):
        async with self._async_session() as session:
            channel: ScalarResult = await session.scalar(select(self.model).where(self.model.telegram_id == channel_id))
            return channel


async def main():
    group = VkGroupManager()
    group = await group.get(1)
    print(group)


if __name__ == '__main__':
    asyncio.run(main())

# async def add_post(post_id, group_id):
#     async with async_session() as session:
#         post = VkPost(
#             post_id=post_id,
#             vk_group_id=group_id,
#         )
#         session.add_all([post])
#         await session.commit()
#
#
# async def get_vk_groups():
#     async with async_session() as session:
#         result = await session.scalars(select(VkGroup))
#         return result
#
#
# async def get_vk_group_by_id(group_id):
#     async with async_session() as session:
#         result = await session.scalars(select(VkGroup).where(VkGroup.group_id == group_id))
#         return result.first()
#
#
# async def add_vk_group(group_data):
#     async with async_session() as session:
#         new_group = VkGroup(
#             group_id=group_data["id"],
#             domain=group_data['screen_name'],
#             group_name=group_data['name'],
#             is_closed=group_data['is_closed'],
#             logo=group_data['photo_200'],
#         )
#         session.add_all([new_group])
#         await session.commit()
#
#
# async def update_vk_group(group: VkGroup):
#     async with async_session() as session:
#         session.add_all([group])
#         await session.commit()
#         return group
#
#
# async def save_tg_channel(channel_data):
#     async with async_session() as session:
#         new_group = TgChannel(
#             channel_id=channel_data.id,
#             title=channel_data.title,
#         )
#         session.add_all([new_group])
#         await session.commit()
#         return new_group
#
#
# async def get_tg_channel_by_id(channel_id):
#     async with async_session() as session:
#         try:
#             result = await session.scalars(select(TgChannel).where(TgChannel.channel_id == channel_id))
#             return result.first()
#         except OperationalError:
#             return None
#
#
# async def get_tg_channel_list():
#     async with async_session() as session:
#         try:
#             result = await session.scalars(select(TgChannel))
#             return result
#         except OperationalError:
#             return None
#
#
# async def update_tg_channel(chanel: TgChannel):
#     async with async_session() as session:
#         session.add_all([chanel])
#         await session.commit()
#         return chanel
