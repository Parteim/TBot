from aiogram.fsm.context import FSMContext
from aiogram import Bot
from aiogram.utils.media_group import MediaGroupBuilder

from src.Bot.resource import text
from src.Bot.states import ParsingStates
from src.Bot.vk_api.base import Wall, Groups, Bot as Vkbot


async def check_vk_group(vk_bot_token: str, domain: str):
    vk_bot = Vkbot(vk_bot_token)
    try:
        response = await Groups(vk_bot).get_by_id(domain)
        return False if 'error' in response else response['response'][0]
    finally:
        await vk_bot.close_session()


def get_current_size_photo(images: list):
    current_img = ''
    img_size = 0
    for img in images:
        if img_size < img['height'] + img['width']:
            img_size = img['height'] + img['width']
            current_img = img['url']
    return current_img


async def get_posts(vk_bot_token: str, domain: str, count_of_posts: int):
    vk_bot = Vkbot(vk_bot_token)
    try:
        posts = []
        response = await Wall(vk_bot).get_posts(domain, count_of_posts)
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
                    img = get_current_size_photo(attachment['photo']['sizes'])
                    post_data['attachments'].append(img) if img != '' else None
            posts.append(post_data)
        return posts
    finally:
        await vk_bot.close_session()


async def parse(chat_id: int, state: FSMContext, domain: str, count_of_posts: int, vk_bot_token: str, tg_bot: Bot):
    posts = await get_posts(vk_bot_token=vk_bot_token, domain=domain, count_of_posts=count_of_posts)

    for post in posts:
        if state == ParsingStates.PARSING_PROCESS:
            group_post_images = MediaGroupBuilder()
            if len(post['attachments']) > 0:
                for image in post['attachments']:
                    group_post_images.add_photo(media=image)
                await tg_bot.send_message(chat_id=chat_id, text=post['text']) if post['text'] else None
                await tg_bot.send_media_group(media=group_post_images.build())
            else:
                await tg_bot.send_message(chat_id=chat_id, text='--')
        else:
            break
    await tg_bot.send_message(chat_id=chat_id, text=text.PARSING_COMPLETE)
    await state.clear()
