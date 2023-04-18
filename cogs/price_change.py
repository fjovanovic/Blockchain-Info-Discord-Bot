from aiohttp import ClientSession
from typing import List
import datetime as dt

from discord import app_commands
from discord import Interaction, Embed, Colour
from discord.ext.commands import Cog, Bot

from constants import *
from utils import utils
from utils import errors
    

class PriceChange(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
	

    @app_commands.command(name='price_change', description='Price change over the period of time')
    @app_commands.describe(
        coin_symbol='Coin symbol'
    )
    async def price_change(self, interaction: Interaction, coin_symbol: str):
        await interaction.response.defer()

        coin_id = utils.find_id_local(coin_symbol)

        if coin_id is None:
            async with ClientSession() as session:
                data = await utils.fetch_url(session, COINGECKO_ALL_COINS_URL)
                for coin in data:
                    if coin['symbol'] == coin_symbol.lower() and 'peg' not in coin['id'].lower():
                        coin_id = coin['id']
        
            if coin_id is None:
                await errors.coin_not_found(interaction)
                return
        
        async with ClientSession() as session:
            data = await utils.fetch_url(
                session, 
                COINGECKO_COIN_DATA_URL.replace('COIN_ID_REPLACE', coin_id)
            )
        
        if data is None:
            await errors.coin_not_found(interaction)
            return

        coin_name = data['name']
        coin_image = data['image']['small']
        coin_day_change = data['market_data']['price_change_24h']
        coin_day_change_percentage = data['market_data']['price_change_percentage_24h']
        coin_7d_change_percentage = data['market_data']['price_change_percentage_7d']
        coin_14d_change_percentage = data['market_data']['price_change_percentage_14d']
        coin_30d_change_percentage = data['market_data']['price_change_percentage_30d']
        if coin_day_change > 0:
            response_price = f'`+{coin_day_change:,}$`'
            response_percentage = f'`+{coin_day_change_percentage:,.2f}%`'
        else:
            response_price = f'`{coin_day_change:,}$`'
            response_percentage = f'`{coin_day_change_percentage:,.2f}%`'
        
        if coin_7d_change_percentage > 0:
            response_7d_percentage = f'`+{coin_7d_change_percentage:,.2f}%`'
        else:
            response_7d_percentage = f'`{coin_7d_change_percentage:,.2f}%`'
        
        if coin_14d_change_percentage > 0:
            response_14d_percentage = f'`+{coin_14d_change_percentage:,.2f}%`'
        else:
            response_14d_percentage = f'`{coin_14d_change_percentage:,.2f}%`'
        
        if coin_30d_change_percentage > 0:
            response_30d_percentage = f'`+{coin_30d_change_percentage:,.2f}%`'
        else:
            response_30d_percentage = f'`{coin_30d_change_percentage:,.2f}%`'

        my_embed = Embed(
            title='More info',
            url=f'https://www.coingecko.com/en/coins/{coin_id}',
            colour=Colour.red() if coin_day_change < 0 else Colour.green(),
            timestamp=dt.datetime.now()
        )

        my_embed.set_author(name=f'{coin_name}({coin_symbol.upper()})', icon_url=coin_image)
        my_embed.add_field(name='Change(24h $)', value=response_price, inline=True)
        my_embed.add_field(name='Change(24h %)', value=response_percentage, inline=True)
        my_embed.add_field(name='‎', value='‎', inline=True)
        my_embed.add_field(name='Change(7d %)', value=response_7d_percentage, inline=True)
        my_embed.add_field(name='Change(14d %)', value=response_14d_percentage, inline=True)
        my_embed.add_field(name='Change(30d %)', value=response_30d_percentage, inline=True)
        my_embed.set_footer(text=f'Source: coingecko.com')

        await interaction.followup.send(embed=my_embed)
    

    @price_change.autocomplete('coin_symbol')
    async def price_change_coin_symbol(self, interaction: Interaction, current: str) -> List[app_commands.Choice]:
        return [
            app_commands.Choice(name=coin, value=coin)
            for coin in COIN_EXAMPLES
            if coin.lower().startswith(current.lower())
        ]
    

    async def cog_load(self) -> None:
        print(f'Cog loaded: {self.__class__.__name__}')


async def setup(bot: Bot) -> None:
    await bot.add_cog(PriceChange(bot=bot))