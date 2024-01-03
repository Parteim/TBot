from src.Bot.vk_api.base import Groups, Bot as Vkbot


async def check_vk_group(vk_bot_token: str, domain: str):
    vk_bot = Vkbot(vk_bot_token)
    try:
        response = await Groups(vk_bot).get_by_id(domain)
        return False if 'error' in response else response['response'][0]
    finally:
        await vk_bot.close_session()
