from typing import List
from sqlalchemy import ForeignKey, String, Integer, Boolean, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id = mapped_column(BigInteger, unique=True)
    username: Mapped[str]

    is_admin: Mapped[bool]

    def __repr__(self):
        return f'User {self.username}, id: {self.telegram_id}, is admin: {self.is_admin}'


class VkGroup(Base):
    __tablename__ = 'vk_groups'

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id = mapped_column(BigInteger, unique=True)
    domain: Mapped[str] = mapped_column(unique=True)
    group_name: Mapped[str]
    is_closed: Mapped[bool]

    logo: Mapped[str]

    is_active: Mapped[bool] = mapped_column(default=True)

    tg_channel: Mapped[List['TgChannel']] = relationship(
        back_populates='vk_group', cascade='all, delete-orphan'
    )

    vk_posts: Mapped[List['VkPost']] = relationship(back_populates='vk_group', cascade='all, delete-orphan')

    def __repr__(self):
        return f'Group {self.group_name}, group_id: {self.group_id}'

    def response_message_repr(self):
        response_message = f'<b>{self.group_name}</b>\n' \
                           f'id: {self.group_id}\n' \
                           f'domain: {self.domain}'
        return self.logo, response_message


class VkPost(Base):
    __tablename__ = 'vk_posts'
    id: Mapped[int] = mapped_column(primary_key=True)

    post_id: Mapped[int]

    vk_group_id: Mapped[int] = mapped_column(ForeignKey('vk_groups.id'), nullable=True)
    vk_group: Mapped['VkGroup'] = relationship(back_populates='vk_posts')


class TgChannel(Base):
    __tablename__ = 'tg_channel'

    id: Mapped[int] = mapped_column(primary_key=True)
    channel_id = mapped_column(BigInteger, unique=True)
    title: Mapped[str] = mapped_column(String(50))

    vk_group_id: Mapped[int] = mapped_column(ForeignKey('vk_groups.id'), nullable=True)
    vk_group: Mapped['VkGroup'] = relationship(back_populates='tg_channel')

    def __repr__(self):
        return f'Telegram channel {self.title}, channel_id: {self.channel_id}'
