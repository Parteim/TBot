from typing import List
from sqlalchemy import ForeignKey, String, Integer, Boolean, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class User(Base):
    __tablename__ = 'users'

    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[str]

    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self):
        return f'User: {self.username}, tg id: {self.telegram_id}, db id: {self.id}'


class TgChannel(Base):
    __tablename__ = 'tg_channels'

    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    name: Mapped[str]

    vk_group: Mapped[List['VkGroup']] = relationship(back_populates='tg_channel')

    def __repr__(self):
        return f'TgChannel: {self.name}, tg id: {self.telegram_id}, db id: {self.id}'


class VkGroup(Base):
    __tablename__ = 'vk_groups'

    vk_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    domain: Mapped[str] = mapped_column(String, unique=True)
    name: Mapped[str]
    is_closed: Mapped[bool]
    logo: Mapped[str]

    tg_channel_id: Mapped[int] = mapped_column(ForeignKey('tg_channels.id'), nullable=True)
    tg_channel: Mapped['TgChannel'] = relationship(back_populates='vk_group')

    def __repr__(self):
        return f'VkGroup: {self.name}, domain: {self.domain}, db id: {self.id}'

    def response_message_repr(self):
        response_message = f'<b>{self.name}</b>\n' \
                           f'id: {self.vk_id}\n' \
                           f'domain: {self.domain}'
        return self.logo, response_message


class VkPost(Base):
    __tablename__ = 'vk_posts'

    vk_post_id: Mapped[int] = mapped_column(BigInteger, unique=True)

    def __repr__(self):
        return f'VkPost: {self.vk_post_id}, db id: {self.id}'
