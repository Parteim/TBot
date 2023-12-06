from .models import TgChannel, User, VkGroup
from sqlalchemy import select
import sqlalchemy
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from .models import User, Base
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from src.bot.config import Config

engin = create_async_engine(Config.DB_URL, echo=True)

async_session = async_sessionmaker(engin)


async def async_main():
    async with engin.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_vk_groups():
    async with async_session() as session:
        result = await session.scalars(select(VkGroup))
        return result


async def get_vk_group_by_id(group_id):
    async with async_session() as session:
        result = await session.scalars(select(VkGroup).where(VkGroup.group_id == group_id))
        return result.first()


async def add_vk_group(group_data):
    async with async_session() as session:
        new_group = VkGroup(
            group_id=group_data["id"],
            domain=group_data['screen_name'],
            group_name=group_data['name'],
            is_closed=group_data['is_closed'],
            logo=group_data['photo_200'],
        )
        session.add_all([new_group])
        await session.commit()


async def add_tg_channel(channel_data):
    async with async_session() as session:
        new_group = TgChannel(
            channel_id=channel_data.id,
            title=channel_data.title,
        )
        session.add_all([new_group])
        await session.commit()


async def get_tg_channel_by_id(channel_id):
    async with async_session() as session:
        try:
            result = await session.scalars(select(TgChannel).where(TgChannel.channel_id == channel_id))
            return result.first()
        except OperationalError:
            return False
