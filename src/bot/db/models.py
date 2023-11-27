from typing import List
import sqlalchemy
from sqlalchemy import ForeignKey, String, Integer, Boolean, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase

from src.bot.config import Config


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer(), unique=True)
    username: Mapped[str] = mapped_column(String(50))

    is_admin: Mapped[bool] = mapped_column(Boolean())

    def __repr__(self):
        return f'User {self.username}, id: {self.user_id}, is admin: {self.is_admin}'


class VkGroup(Base):
    __tablename__ = 'vk_groups'

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(BigInteger(), unique=True)
    domain: Mapped[str] = mapped_column(String(100), unique=True)
    group_name: Mapped[str] = mapped_column(String(100))
    is_closed: Mapped[bool] = mapped_column(Boolean())

    logo: Mapped[str] = mapped_column(String(255))

    tg_channel: Mapped[List['TgChannel']] = relationship(
        back_populates='vk_group', cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'Group {self.group_name}, group_id: {self.group_id}'


class TgChannel(Base):
    __tablename__ = 'tg_channel'

    id: Mapped[int] = mapped_column(primary_key=True)
    channel_id: Mapped[int] = mapped_column(BigInteger(), unique=True)
    channel_name: Mapped[str] = mapped_column(String(50))

    logo: Mapped[str] = mapped_column((String(255)))

    vk_group_id: Mapped[int] = mapped_column(ForeignKey('vk_groups.id'))
    vk_group: Mapped['VkGroup'] = relationship(back_populates='tg_channel')

    def __repr__(self):
        return f'Telegram channel {self.channel_name}, channel_id: {self.channel_id}'


engin = sqlalchemy.create_engine(Config.DB_URL, echo=True)

Base.metadata.create_all(engin)
