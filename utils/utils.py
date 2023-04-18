import logging
import logging.handlers
from typing import Dict, Union
from aiohttp import ClientSession
import json

from constants import *


def find_id_local(coin_symbol: str) -> Union[Dict, None]:
    coin_symbol = coin_symbol.lower()
    
    with open('coingecko/all_coins.json', 'r') as f:
        data = json.load(f)
        for coin in data:
            if coin['symbol'] == coin_symbol and 'peg' not in coin['id']:
                return coin['id']
    
    return None


def setup_logging() -> None:
    logger = logging.getLogger('')
    logger.setLevel(logging.INFO)

    handler = logging.handlers.RotatingFileHandler(
        filename='discord.log',
        encoding='utf-8',
        maxBytes=32 * 1024 * 1024,
        backupCount=5,
    )

    dt_fmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


async def fetch_url(session: ClientSession, url: str) -> Union[Dict, None]:
    async with session.get(url) as response:
        if response.status == 404:
            return None
        
        return await response.json()