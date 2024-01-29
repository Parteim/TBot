import zipfile
from typing import BinaryIO

from aiohttp import ClientSession, ClientConnectorError
import aiohttp
import shutil
import os
import requests
from io import BytesIO
from PIL import Image
import uuid

from Bot.config import BASE_DIR


async def download_images(img_urls: [str], dir_path: str) -> None:
    async with ClientSession() as session:
        for img_url in img_urls:
            try:
                async with session.get(img_url) as response:
                    if response.status == 200:
                        img = Image.open(BytesIO(await response.read()))
                        try:
                            img.save(
                                os.path.join(
                                    dir_path,
                                    f'{str(uuid.uuid4())}.jpg'
                                )
                            )
                        except Exception as e:
                            print(e)
            except ClientConnectorError:
                pass


def create_dir() -> str:
    dir_path = os.path.join(
        BASE_DIR,
        str(uuid.uuid4())
    )
    os.mkdir(dir_path)
    return dir_path


async def get_zip(img_urls: list) -> str:
    dir_path = create_dir()
    await download_images(img_urls, dir_path)
    shutil.make_archive(
        dir_path,
        'zip',
        dir_path
    )
    return dir_path + '.zip'


async def remove_zip(path: str):
    # this function should be called immediately after the archive sending method is executed!
    shutil.rmtree(path.replace('.zip', ''))
    os.remove(path)


if __name__ == '__main__':
    get_zip(
        [
            'https://pichold.ru/wp-content/uploads/2018/10/interesnie_fakti_o_ejah.jpg',
            'https://uprostim.com/wp-content/uploads/2021/02/image004-49.jpg',
            'https://masyamba.ru/%D0%B5%D0%B6%D0%B8%D0%BA-%D0%BA%D0%B0%D1%80%D1%82%D0%B8%D0%BD%D0%BA%D0%B8/94-%D0%BA%D0%B0%D1%80%D1%82%D0%B8%D0%BD%D0%BA%D0%B8-%D0%BF%D1%80%D0%BE-%D0%B5%D0%B6%D0%B8%D0%BA%D0%BE%D0%B2.jpg'
        ]
    )
