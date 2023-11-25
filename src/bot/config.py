import os
from dotenv import load_dotenv, find_dotenv
from dataclasses import dataclass

load_dotenv(find_dotenv())


# 1065749495

@dataclass
class Config:
    BOT_TOKEN: str = os.getenv('BEST_BOT_TOKEN')
    ADMIN_ID: int = int(os.getenv('ADMIN_ID'))

    VK_ACCESS_TOKEN = os.getenv('VK_SERVICES_ACCESS_KEY')

    DB_URL = 'sqlite:///bot_db.db'
