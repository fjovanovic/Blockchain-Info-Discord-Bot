from aiohttp import ClientSession
from typing import List
import datetime as dt
from io import BytesIO
from plotly.graph_objects import Figure, Candlestick

from discord import app_commands
from discord import Interaction, Embed, Colour, File
from discord.ext.commands import Cog, Bot

from constants import *
from utils import utils
from utils import errors
    

class Info(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
    
    
    @app_commands.command(name='info', description='Basic information about the coin')
    @app_commands.describe(
        coin_symbol='Coin symbol'
    )
    async def info(self, interaction: Interaction, coin_symbol: str):
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
        
        async with ClientSession() as session:
            ohlc_data = await utils.fetch_url(
                session, 
                COINGECKO_OHLC_DATA_URL.replace('COIN_ID_REPLACE', coin_id)
            )
        
        dates = [dt.datetime.fromtimestamp(tick[0]/1000) for tick in ohlc_data]
        open = [tick[1] for tick in ohlc_data]
        high = [tick[2] for tick in ohlc_data]
        low = [tick[3] for tick in ohlc_data]
        close = [tick[4] for tick in ohlc_data]

        coin_name = data['name']
        coin_image = data['image']['small']
        coin_price = data['market_data']['current_price']['usd']
        coin_market_cap = data['market_data']['market_cap']['usd']
        coin_market_cap_rank = data['market_data']['market_cap_rank']
        coin_price_change_24h = float(data['market_data']['price_change_24h'])
        coin_price_change_percentage_24h = float(data['market_data']['price_change_percentage_24h'])
        if coin_price_change_24h >= 0:
            coin_price_change_24h = f'+{coin_price_change_24h:,.5f}'
            coin_price_change_percentage_24h = f'+{coin_price_change_percentage_24h:,.2f}'
        else:
            coin_price_change_24h = f'{coin_price_change_24h:,.5f}'
            coin_price_change_percentage_24h = f'{coin_price_change_percentage_24h:,.2f}'
        coin_ath = data['market_data']['ath']['usd']
        coin_ath_date = data['market_data']['ath_date']['aed']
        coin_ath_real_date = dt.datetime(
            int(coin_ath_date[:4]), 
            int(coin_ath_date[5:7]), 
            int(coin_ath_date[8:10]), 
            int(coin_ath_date[11:13]), 
            int(coin_ath_date[14:16])
        ).strftime('%d-%b-%Y %H:%M')

        my_embed = Embed(
            title='More info',
            url=f'https://www.coingecko.com/en/coins/{coin_symbol}',
            colour=Colour.blue(),
            timestamp=dt.datetime.now()
        )

        my_embed.set_author(name=f'{coin_name}({coin_symbol.upper()})', icon_url=coin_image)
        my_embed.add_field(name='Price', value=f'`{coin_price:,}$`', inline=True)
        my_embed.add_field(name='Market cap', value=f'`#{coin_market_cap_rank}\n{coin_market_cap:,}$`', inline=True)
        my_embed.add_field(name='ATH', value=f'`{coin_ath:,}\n{coin_ath_real_date}`', inline=True)
        my_embed.add_field(name='Change(24h $)', value=f'`{coin_price_change_24h}$`', inline=True)
        my_embed.add_field(name='Change(24h %)', value=f'`{coin_price_change_percentage_24h}%`', inline=True)
        my_embed.set_footer(text=f'Source: coingecko.com')

        fig = Figure(data=[Candlestick(
            x=dates,
            open=open,
            high=high,
            low=low,
            close=close
        )])

        fig.update_layout(xaxis_rangeslider_visible=False, template='plotly_dark')

        with BytesIO() as image_binary:
            fig.write_image(image_binary, 'PNG')
            image_binary.seek(0)
            my_file = File(fp=image_binary, filename='image.png')
            my_embed.set_image(url='attachment://image.png')

            await interaction.followup.send(embed=my_embed, file=my_file)


    @info.autocomplete('coin_symbol')
    async def info_coin_symbol(self, interaction: Interaction, current: str) -> List[app_commands.Choice]:
        return [
            app_commands.Choice(name=coin, value=coin)
            for coin in COIN_EXAMPLES
            if coin.lower().startswith(current.lower())
        ]
    

    async def cog_load(self) -> None:
        print(f'Cog loaded: {self.__class__.__name__}')


async def setup(bot: Bot) -> None:
    await bot.add_cog(Info(bot=bot))