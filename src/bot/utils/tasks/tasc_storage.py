from redis import Redis

from src.bot.config import Config

r = Redis(
    host=Config.REDIS_CONFIG.HOST,
    port=Config.REDIS_CONFIG.PORT,
    db=1,
    decode_responses=Config.REDIS_CONFIG.DECODE_RESPONSE,
)

# r.set('test:1', 'SOME TEXT')

# print(r.get('test1'))
