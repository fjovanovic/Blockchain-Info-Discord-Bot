from aiohttp import ClientSession
from typing import List
import datetime as dt

from discord import app_commands
from discord import Interaction, Embed, Colour
from discord.ext.commands import Cog, Bot

from constants import *
from utils import utils
from utils import errors
    

class Top(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
	

    @app_commands.command(name='top', description='Top n coins by the market cap')
    @app_commands.describe(
        n='Number of coins [1, 30]'
    )
    async def top(self, interaction: Interaction, n: int):
        await interaction.response.defer()

        if n < 1 or n > 30:
            await errors.wrong_topn_number(interaction)
            return

        respond_symbols = ''
        respond_prices = ''
        respond_market_cap = ''

        async with ClientSession() as session:
            data = await utils.fetch_url(session, COINGECKO_COINS_PER_PAGE)
        
        if data is None:
            await errors.api_problem(interaction)
            return

        i = 0
        for coin in data:
            if i == n:
                break
            respond_symbols += f'`{coin["symbol"].upper()}`\n'
            respond_prices += f'`{coin["current_price"]:,}$`\n'
            respond_market_cap += f'`{coin["market_cap"]:,}$`\n'
            i += 1

        my_embed = Embed(
            title='More info',
            url='https://www.coingecko.com/en',
            colour=Colour.blue(),
            timestamp=dt.datetime.now()
        )

        my_embed.set_author(name=f'Top{n} coins', url='https://coingecko.com', icon_url=TOP_N_COINS_IMAGE)
        my_embed.add_field(name='Symbol', value=respond_symbols, inline=True)
        my_embed.add_field(name='Price', value=respond_prices, inline=True)
        my_embed.add_field(name='Market cap', value=respond_market_cap, inline=True)
        my_embed.set_footer(text=f'Source: coingecko.com')

        await interaction.followup.send(embed=my_embed)
    

    async def cog_load(self) -> None:
        print(f'Cog loaded: {self.__class__.__name__}')


async def setup(bot: Bot) -> None:
    await bot.add_cog(Top(bot=bot))