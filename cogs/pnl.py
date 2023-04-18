from aiohttp import ClientSession
from typing import List
import datetime as dt

from discord import app_commands
from discord import Interaction, Embed, Colour
from discord.ext.commands import Cog, Bot

from constants import *
from utils import utils
from utils import errors
    

class PNL(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
	

    @app_commands.command(name='pnl', description='Price of the coin')
    @app_commands.describe(
        position_type='Type of the opened position',
        coin_symbol='Coin symbol',
        price='Price of the opened position'
    )
    async def pnl(self, interaction: Interaction, position_type: str, coin_symbol: str, price: float):
        await interaction.response.defer()

        position_type = position_type.lower()

        if position_type != 'buy' and position_type != 'sell':
            await errors.wrong_position_type(interaction)
            return
        
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

        coin_name = data['name']
        coin_image = data['image']['small']
        coin_current_price = float(data['market_data']['current_price']['usd'])
        coin_percentage = (coin_current_price - price) / price * 100
        if coin_percentage > 0 and position_type == 'buy':
            response = f'+{coin_percentage:,.2f}%'
        elif coin_percentage < 0 and position_type == 'sell':
            coin_percentage = abs(coin_percentage)
            response = f'+{coin_percentage:,.2f}%'
        elif coin_percentage > 0 and position_type == 'sell':
            coin_percentage = -coin_percentage
            response = f'{coin_percentage:,.2f}%'
        else:
            response = f'{coin_percentage:,.2f}%'

        current_position = 'Current profit' if coin_percentage >= 0 else 'Current loss'
        timestamp_now = dt.datetime.now()
        
        my_embed = Embed(
            title = 'More info',
            url = f'https://www.coingecko.com/en/coins/{coin_id}',
            colour = Colour.red() if coin_percentage < 0 else Colour.green(),
            timestamp=timestamp_now
        )

        my_embed.set_author(name=f'{coin_name}({coin_symbol.upper()})', icon_url=coin_image)
        my_embed.add_field(name=current_position, value=response, inline=True)
        my_embed.set_footer(text=f'Source: coingecko.com')

        await interaction.followup.send(embed=my_embed)
    

    @pnl.autocomplete('position_type')
    async def pnl_position_type(self, interaction: Interaction, current: str) -> List[app_commands.Choice]:
        return [
            app_commands.Choice(name=position_type, value=position_type)
            for position_type in ['BUY', 'SELL']
            if position_type.lower().startswith(current.lower())
        ]
    

    @pnl.autocomplete('coin_symbol')
    async def pnl_coin_symbol(self, interaction: Interaction, current: str) -> List[app_commands.Choice]:
        return [
            app_commands.Choice(name=coin, value=coin)
            for coin in COIN_EXAMPLES
            if coin.lower().startswith(current.lower())
        ]
        

    async def cog_load(self) -> None:
        print(f'Cog loaded: {self.__class__.__name__}')


async def setup(bot: Bot) -> None:
    await bot.add_cog(PNL(bot=bot))