from src.bot.config import Config
from ..base import Bot, Wall


def get_current_size_photo(images: list):
    current_img = ''
    img_size = 0
    for img in images:
        if img_size < img['height'] + img['width']:
            img_size = img['height'] + img['width']
            current_img = img['url']
    return current_img


async def get_posts(bot: Bot, domain: str, count_of_posts: int):
    vk_bot = bot
    try:
        posts = []
        response = await Wall(vk_bot).get_posts(domain, count_of_posts)
        for post in response:
            post_data = {
                'text': post['text'],
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
