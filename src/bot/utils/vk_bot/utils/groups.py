from ..Base import Bot, Groups

from src.bot.config import Config


async def check_vk_group(domain: str):
    vk_bot = Bot(Config.VK_ACCESS_TOKEN)
    try:
        response = await Groups(vk_bot).get_by_id(domain)
        return False if 'error' in response else response['response'][0]
    finally:
        await vk_bot.close_session()
