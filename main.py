import os
import discord
from dotenv import load_dotenv
from argparse import ArgumentParser
import asyncio

from constants import *
from components import MyBot, MyCommandTree
from utils import utils


async def main():
    load_dotenv()
    
    bot = MyBot(command_prefix='$', activity_name='Blockchain', tree_cls=MyCommandTree)

    parser = ArgumentParser(
        usage='python3 main.py [-t | --test]',
        description='Discord bot for providing information about the cryptocurrencies',
        allow_abbrev=False
    )

    parser.add_argument('-t', '--test', action='store_true', help='Providing console log instead of file log')
    args = parser.parse_args()    
    if args.test:
        discord.utils.setup_logging()
    else:
        utils.setup_file_logging()
    
    TOKEN = os.getenv('TOKEN')
    await bot.start(TOKEN)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())