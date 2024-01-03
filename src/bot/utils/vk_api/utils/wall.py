from aiogram.utils.media_group import MediaGroupBuilder

from bot.admin.utils.resource import text
from src.bot.config import Config
from aiogram import Router, F, Bot
from aiogram.fsm.state import State
from ..base import Wall, Bot as VkBot


class WallParser:
    def __init__(self, bot: Bot, vk_bot_token):
        self._tg_bot = bot
        self._vk_bot = VkBot(vk_bot_token)

    @staticmethod
    def get_current_size_photo(images: list):
        current_img = ''
        img_size = 0
        for img in images:
            if img_size < img['height'] + img['width']:
                img_size = img['height'] + img['width']
                current_img = img['url']
        return current_img

    async def get_posts(self, domain: str, count_of_posts: int):
        try:
            posts = []
            response = await Wall(self._vk_bot).get_posts(domain, count_of_posts)
            for post in response:
                if post['marked_as_ads'] == 1:
                    continue
                post_data = {
                    'text': post['text'],
                    'id': post['id'],
                    'likes': post['likes']['count'],
                    'attachments': []
                }
                for attachment in post['attachments']:
                    if attachment['type'] == 'photo':
                        img = self.get_current_size_photo(attachment['photo']['sizes'])
                        post_data['attachments'].append(img) if img != '' else None
                posts.append(post_data)
            return posts
        finally:
            await self._vk_bot.close_session()

    async def parse(self, chat_id: int, state: State, domain: str, count_of_posts: int):
        posts = await self.get_posts(domain=domain, count_of_posts=count_of_posts)

        for post in posts:
            if state:
                group_post_images = MediaGroupBuilder()
                group_post_images = MediaGroupBuilder()
                if len(post['attachments']) > 0:
                    for image in post['attachments']:
                        group_post_images.add_photo(media=image)
                    await self._tg_bot.send_message(chat_id=chat_id, text=post['text']) if post['text'] else None
                    await self._tg_bot.send_media_group(media=group_post_images.build())
                else:
                    await self._tg_bot.send_message(chat_id=chat_id, text='--')
            else:
                break
        await self._tg_bot.send_message(chat_id=chat_id, text=text.PARSING_COMPLETE)
        await state.clear()
