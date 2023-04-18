from aiohttp import ClientSession
from typing import List
import datetime as dt

from discord import app_commands
from discord import Interaction, Embed, Colour
from discord.ext.commands import Cog, Bot

from constants import *
from utils import utils
from utils import errors
    

class ATH(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
	

    @app_commands.command(name='ath', description='All time high info')
    @app_commands.describe(
        coin_symbol='Coin symbol'
    )
    async def ath(self, interaction: Interaction, coin_symbol: str):
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
        coin_ath = data['market_data']['ath']['usd']
        coin_ath_date = data['market_data']['ath_date']['aed']
        coin_ath_real_date = dt.datetime(
            int(coin_ath_date[:4]), 
            int(coin_ath_date[5:7]), 
            int(coin_ath_date[8:10]), 
            int(coin_ath_date[11:13]), 
            int(coin_ath_date[14:16])
        ).strftime('`%d-%b-%Y %H:%M`')
        coin_ath_percentage_down = data['market_data']['ath_change_percentage']['usd']

        my_embed = Embed(
            title='More info',
            url=f'https://www.coingecko.com/en/coins/{coin_id}',
            colour=Colour.blue(),
            timestamp=dt.datetime.now()
        )

        my_embed.set_author(name=f'{coin_name}({coin_symbol.upper()})', icon_url=coin_image)
        my_embed.add_field(name='ATH', value=f'`{coin_ath:,}$`', inline=True)
        my_embed.add_field(name='Date', value=coin_ath_real_date, inline=True)
        my_embed.add_field(name='Down(%)', value=f'`{coin_ath_percentage_down:,.2f}%`', inline=True)
        my_embed.set_footer(text=f'Source: coingecko.com')

        await interaction.followup.send(embed=my_embed)
    

    @ath.autocomplete('coin_symbol')
    async def ath_coin_symbol(self, interaction: Interaction, current: str) -> List[app_commands.Choice]:
        return [
            app_commands.Choice(name=coin, value=coin)
            for coin in COIN_EXAMPLES
            if coin.lower().startswith(current.lower())
        ]
    

    async def cog_load(self) -> None:
        print(f'Cog loaded: {self.__class__.__name__}')


async def setup(bot: Bot) -> None:
    await bot.add_cog(ATH(bot=bot))