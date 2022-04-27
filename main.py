from os import environ
import discord
from discord.ext import commands, tasks 
from requests import get
import datetime as dt
from dotenv import load_dotenv

from constants import *
import functions


load_dotenv()

client = commands.Bot(command_prefix='$')


@client.event
async def on_ready():
	print(f'You have logged in as {client.user}')


# Every 60 minutes if there is bigger movement, +- 10%, 
# then it will be sent to that particular channel
@tasks.loop(minutes=60)
async def last_hour_movers():
	await client.wait_until_ready()

	channel = client.get_channel(PRICE_ALERTS_CHANNEL)

	try:
		data = get(COINGECKO_PRICE_CHANGE_LAST_HOUR).json()
	except:
		await functions.error(channel, 'URL problem', 'we have a problem with fetching the data from coingecko, try again later')
		return

	coin_symbols = []
	response_positive = ''
	response_negative = ''

	for crypto in data:
		coin_symbol = crypto['symbol'].upper()
		coin_symbols.append(coin_symbol)
		coin_1h_change_percentage = float(crypto['price_change_percentage_1h_in_currency'])
		if coin_1h_change_percentage > 10:
			response_positive += f'{coin_symbol} {coin_1h_change_percentage:,.2f}%\n'
		elif coin_1h_change_percentage < -10:
			response_negative += f'{coin_symbol} {coin_1h_change_percentage:,.2f}%\n'

	if response_positive or response_negative:
		date_now = dt.datetime.utcnow().strftime('%d-%b-%Y %H:%M UTC')

		my_embed = discord.Embed(
			colour = discord.Colour.blurple()
		)

		my_embed.set_author(name='Big market movers', icon_url=LAST_HOUR_MOVERS_IMAGE)
		if response_positive:
			my_embed.add_field(name='Positive movers', value=response_positive, inline=True)
		else:
			my_embed.add_field(name='Positive movers', value='‎', inline=True)
		if response_negative:
			my_embed.add_field(name='Negative movers', value=response_negative, inline=True)
		else:
			my_embed.add_field(name='Negative movers', value='‎', inline=True)
		my_embed.set_footer(text=f'Source: coingecko.com ☛ {date_now}')

		await channel.send(embed=my_embed)
	return


last_hour_movers.start()


# Every 30 minutes if there is new ATH then it will be sent to that particular channel
@tasks.loop(minutes=30)
async def new_ath():
	await client.wait_until_ready()

	channel = client.get_channel(PRICE_ALERTS_CHANNEL) 

	try:
		data = get(COINGECKO_COINS_PER_PAGE).json()	
	except:
		await functions.error(channel, 'URL problem', 'we have a problem with fetching the data from coingecko, try again later')
		return

	response = ''
	found = False
	date_now = dt.datetime.utcnow().replace(microsecond=0)

	for crypto in data:
		ath = crypto['ath']
		ath_date = crypto['ath_date']
		ath_year = int(ath_date[0:4])
		ath_month = int(ath_date[5:7])
		ath_day = int(ath_date[8:10])
		ath_hours = int(ath_date[11:13])
		ath_minutes = int(ath_date[14:16])
		ath_seconds = int(ath_date[17:19])
		ath_real_date = dt.datetime(ath_year, ath_month, ath_day, ath_hours, ath_minutes, ath_seconds)
		difference = date_now - ath_real_date
		minutes = divmod(difference.total_seconds(), 60)

		if minutes[0] <= 30:
			response += f'{crypto["symbol"].upper()} : {ath:,}\n'
			found = True
		
	if found:
		date_now = dt.datetime.utcnow().strftime('%d-%b-%Y %H:%M UTC')	

		my_embed = discord.Embed(
			colour = discord.Colour.blurple()
		)

		my_embed.set_author(name='New ATH', icon_url=NEW_ATH_IMAGE)
		my_embed.add_field(name='Currencies', value=response, inline=True)
		my_embed.set_footer(text=f'Source: coingecko.com ☛ {date_now}')

		await channel.send(embed=my_embed)
	
	return
		

new_ath.start()


# If there is more than 300$ movement on BTC in past 4 sec * 5 = 20 sec,
# then the bot will send BTC, ETH and DOT price at the moment,
# with possibility of the same movement on alt coins
btc_prices = []
eth_prices = []
dot_prices = []


@tasks.loop(seconds=4)
async def binance_movers_check():
	if not client.is_ready():
		return

	channel = client.get_channel(BINANCE_PRICE_ALERTS_CHANNEL) 

	try:
		data = get(BINANCE_PRICE_ALL_COINS).json()	
	except:
		await functions.error(channel, 'URL problem', 'we have a problem with fetching the data from binance, try again later')
		return

	for coin in data:
		if 'USDT' in coin['symbol']:
			if coin['symbol'] == 'BTCUSDT':
				for price in btc_prices:
					if abs(float(coin['price']) - price) > 300:
						date_now = dt.datetime.utcnow().strftime('%d-%b-%Y %H:%M UTC')	

						my_embed = discord.Embed(
							colour = discord.Colour.blurple()
						)

						my_embed.set_author(name='BTC Movement Alert', icon_url=LAST_HOUR_MOVERS_IMAGE)
						my_embed.add_field(name='Potential buy / sell', value=f'‎\nBTC: {btc_prices[-1]}\n\nETH: {eth_prices[-1]}\n\nDOT: {dot_prices[-1]}', inline=True)
						my_embed.set_footer(text=f'Source: binance.com ☛ {date_now}')

						await channel.send(embed=my_embed)
						btc_prices.clear()
						eth_prices.clear()
						dot_prices.clear()
				if len(btc_prices) == 5:
					btc_prices.pop(0)
					btc_prices.append(float(coin['price']))
				else:
					btc_prices.append(float(coin['price']))
			elif coin['symbol'] == 'ETHUSDT':
				if len(eth_prices) == 5:
					eth_prices.pop(0)
					eth_prices.append(float(coin['price']))
				else:
					eth_prices.append(float(coin['price']))
			elif coin['symbol'] == 'DOTUSDT':
				if len(dot_prices) == 5:
					dot_prices.pop(0)
					dot_prices.append(float(coin['price']))
				else:
					dot_prices.append(float(coin['price']))

	return


binance_movers_check.start()


# Some info about the provided coin, ath, price, etc.
@client.command()
async def info(ctx, *args):
	if len(args) != 1:
		await functions.wrong_call(ctx, 'info symbol')
		return
	
	coin_symbol = args[0].lower()
	coin_id = functions.find_id(coin_symbol)
	if not coin_id:
		await functions.error(ctx, 'Wrong coin', 'make sure to provide us with the correct coin')
		return

	try:
		data = get(COINGECKO_COIN_DATA_URL.replace('COIN_ID_REPLACE', coin_id)).json()
	except:
		await functions.error(ctx, 'URL problem', 'we have a problem with fetching the data from coingecko, try again later')
		return

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
	coin_ath_real_date = dt.datetime(int(coin_ath_date[:4]), int(coin_ath_date[5:7]), int(coin_ath_date[8:10]), int(coin_ath_date[11:13]), int(coin_ath_date[14:16])).strftime('%d-%b-%Y %H:%M')

	date_now = dt.datetime.utcnow().strftime('%d-%b-%Y %H:%M UTC')	

	my_embed = discord.Embed(
		title = 'More info',
		url = 'https://www.coingecko.com/en/coins/' + coin_id,
		colour = discord.Colour.blurple() 
	)

	my_embed.set_author(name=f'{coin_name}({coin_symbol.upper()})', icon_url=coin_image)
	my_embed.add_field(name='Price', value=f'{coin_price:,}$', inline=True)
	my_embed.add_field(name='Market cap', value=f'#{coin_market_cap_rank}\n{coin_market_cap:,}', inline=True)
	my_embed.add_field(name='ATH', value=f'{coin_ath:,}\n{coin_ath_real_date}', inline=True)
	my_embed.add_field(name='Change(24h $)', value=f'{coin_price_change_24h}$', inline=True)
	my_embed.add_field(name='Change(24h %)', value=f'{coin_price_change_percentage_24h}%', inline=True)
	my_embed.set_footer(text=f'Source: coingecko.com ☛ {date_now}')

	await ctx.send(embed=my_embed)
	return


# Price for the provided coin
@client.command()
async def price(ctx, *args):
	if len(args) != 1:
		await functions.wrong_call(ctx, 'price symbol')
		return

	coin_symbol = args[0].lower()
	coin_id = functions.find_id(coin_symbol)
	if not coin_id:
		await functions.error(ctx, 'Wrong coin', 'make sure to provide us correct coin')
		return

	try:
		data = get(COINGECKO_COIN_DATA_URL.replace('COIN_ID_REPLACE', coin_id)).json()
	except:
		await functions.error(ctx, 'URL problem', 'we have a problem with fetching the data from coingecko, try again later')
		return

	coin_name = data['name']
	coin_image = data['image']['small']
	coin_price = data['market_data']['current_price']['usd']

	date_now = dt.datetime.utcnow().strftime('%d-%b-%Y %H:%M UTC')	
	
	my_embed = discord.Embed(
		title = 'More info',
		url = 'https://www.coingecko.com/en/coins/' + coin_id,
		colour = discord.Colour.blurple() 
	)

	my_embed.set_author(name=f'{coin_name}({coin_symbol.upper()})', icon_url=coin_image)
	my_embed.add_field(name='Price', value=f'{coin_price:,}$', inline=True)
	my_embed.set_footer(text=f'Source: coingecko.com ☛ {date_now}')

	await ctx.send(embed=my_embed)
	return


# How many % you are positive or negative for the provided coin
@client.command()
async def bought(ctx, *args):
	if len(args) != 2:
		await functions.wrong_call(ctx, 'bought symbol price')
		return

	coin_symbol = args[0].lower()
	try:
		bought_price = float(args[1].replace(',','.'))
		if bought_price <= 0:
			await functions.error(ctx,'Wrong price', 'make sure to provide us with correct price.')
			return
	except:
		await functions.wrong_call(ctx, 'bought symbol price')
		return

	coin_id = functions.find_id(coin_symbol)
	if not coin_id:
		await functions.error(ctx, 'Wrong coin', 'make sure to provide us with the correct coin')
		return

	try:
		data = get(COINGECKO_COIN_DATA_URL.replace('COIN_ID_REPLACE', coin_id)).json()
	except:
		await functions.error(ctx, 'URL problem', 'we have a problem with fetching the data from coingecko, try again later')
		return

	coin_name = data['name']
	coin_image = data['image']['small']
	coin_current_price = data['market_data']['current_price']['usd']
	coin_percentage = ((float(coin_current_price) / float(bought_price))  - 1) * 100
	if coin_percentage > 0:
		response = f'+{coin_percentage:,.2f}%'
	else:
		response = f'{coin_percentage:,.2f}%'

	date_now = dt.datetime.utcnow().strftime('%d-%b-%Y %H:%M UTC')		
	
	my_embed = discord.Embed(
		colour = discord.Colour.red() if coin_percentage < 0 else discord.Colour.green()
	)

	my_embed.set_author(name=f'{coin_name}({coin_symbol.upper()})', icon_url=coin_image)
	if coin_percentage > 0:
		my_embed.add_field(name='Current profit', value=response, inline=True)
	else:
		my_embed.add_field(name='Current loss', value=response, inline=True)
	my_embed.set_footer(text=f'Source: coingecko.com ☛ {date_now}')

	await ctx.send(embed=my_embed)	
	return


# Daychange in $ and % for the provided coin
@client.command()
async def daychange(ctx, *args):
	if len(args) != 1:
		await functions.wrong_call(ctx, 'daychange symbol')
		return

	coin_symbol = args[0].lower()
	coin_id = functions.find_id(coin_symbol)
	if not coin_id:
		await functions.error(ctx, 'Wrong coin', 'make sure to provide us correct coin')
		return

	try:
		data = get(COINGECKO_COIN_DATA_URL.replace('COIN_ID_REPLACE', coin_id)).json()
	except:
		await functions.error(ctx, 'URL problem', 'we have a problem with fetching the data from coingecko, try again later')
		return


	coin_name = data['name']
	coin_image = data['image']['small']
	coin_day_change = data['market_data']['price_change_24h']
	coin_day_change_percentage = data['market_data']['price_change_percentage_24h']
	if coin_day_change > 0:
		response_price = f'+{coin_day_change:,}$'
		response_percentage = f'+{coin_day_change_percentage:,.2f}%'
	else:
		response_price = f'{coin_day_change:,}$'
		response_percentage = f'{coin_day_change_percentage:,.2f}%'

	date_now = dt.datetime.utcnow().strftime('%d-%b-%Y %H:%M UTC')		
	
	my_embed = discord.Embed(
		colour = discord.Colour.red() if coin_day_change < 0 else discord.Colour.green()
	)

	my_embed.set_author(name=f'{coin_name}({coin_symbol.upper()})', icon_url=coin_image)
	if coin_day_change > 0:
		my_embed.add_field(name='Change(24h $)', value=response_price, inline=True)
		my_embed.add_field(name='Change(24h %)', value=response_percentage, inline=True)
	else:
		my_embed.add_field(name='Change(24h $)', value=response_price, inline=True)
		my_embed.add_field(name='Change(24h %)', value=response_percentage, inline=True)
	my_embed.set_footer(text=f'Source: coingecko.com ☛ {date_now}')

	await ctx.send(embed=my_embed)
	return


# ATH for the provided coin
@client.command()
async def ath(ctx, *args):
	if len(args) != 1:
		await functions.wrong_call(ctx, 'ath symbol')
		return

	coin_symbol = args[0].lower()
	coin_id = functions.find_id(coin_symbol)
	if not coin_id:
		await functions.error(ctx, 'Wrong coin', 'make sure to provide us correct coin')
		return

	try:
		data = get(COINGECKO_COIN_DATA_URL.replace('COIN_ID_REPLACE', coin_id)).json()
	except:
		await functions.error(ctx, 'URL problem', 'we have a problem with fetching the data from coingecko, try again later')
		return

	coin_name = data['name']
	coin_image = data['image']['small']
	coin_ath = data['market_data']['ath']['usd']
	coin_ath_date = data['market_data']['ath_date']['aed']
	coin_ath_real_date = dt.datetime(int(coin_ath_date[:4]), int(coin_ath_date[5:7]), int(coin_ath_date[8:10]), int(coin_ath_date[11:13]), int(coin_ath_date[14:16])).strftime('%d-%b-%Y %H:%M')
	coin_ath_percentage_down = data['market_data']['ath_change_percentage']['usd']

	date_now = dt.datetime.utcnow().strftime('%d-%b-%Y %H:%M UTC')
	
	my_embed = discord.Embed(
		colour = discord.Colour.blurple() 
	)
	my_embed.set_author(name=f'{coin_name}({coin_symbol.upper()})', icon_url=coin_image)
	my_embed.add_field(name='ATH', value=f'{coin_ath:,}$', inline=True)
	my_embed.add_field(name='Date', value=coin_ath_real_date, inline=True)
	my_embed.add_field(name='Down(%)', value=f'{coin_ath_percentage_down:,.2f}%', inline=True)
	my_embed.set_footer(text=f'Source: coingecko.com ☛ {date_now}')

	await ctx.send(embed=my_embed)
	return


# Top n coins by market cap, n ∈ [0, 50]
@client.command()
async def top(ctx, *args):
	if len(args) != 1:
		await functions.wrong_call(ctx, 'top n')
		return

	try:
		n = int(args[0])
		if n < 1 or n > 50:
			await functions.error(ctx, 'Wrong input', 'make sure to provide us with correct input (number of coins must be between 1 and 50)')
			return
	except:
		await functions.wrong_call(ctx, 'top n')
		return

	respond_symbols = ''
	respond_prices = ''
	respond_market_cap = ''

	try:
		data = get(COINGECKO_COINS_PER_PAGE).json() 
	except:
		await functions.error(ctx, 'URL problem', 'we have a problem with fetching the data from coingecko, try again later')
		return

	i = 0
	for crypto in data:
		if i == n:
			break
		respond_symbols += f'{crypto["symbol"].upper()}\n'
		respond_prices += f'{crypto["current_price"]:,}\n'
		respond_market_cap += f'{crypto["market_cap"]:,}\n'
		i += 1

	date_now = dt.datetime.utcnow().strftime('%d-%b-%Y %H:%M UTC')	

	my_embed = discord.Embed(
		title = 'More info',
		url = 'https://www.coingecko.com/en',
		colour = discord.Colour.blurple()
	)
	my_embed.set_author(name=f'Top{n} coins', url='https://coingecko.com', icon_url='https://png.pngtree.com/png-clipart/20210310/original/pngtree-3d-trophy-with-first-second-third-winner-png-image_5931060.jpg')
	my_embed.add_field(name='Symbol', value=respond_symbols, inline=True)
	my_embed.add_field(name='Price', value=respond_prices, inline=True)
	my_embed.add_field(name='Market cap', value=respond_market_cap, inline=True)
	my_embed.set_footer(text=f'Source: coingecko.com ☛ {date_now}')

	await ctx.send(embed=my_embed)
	return


# All commands that bot can use
@client.command()
async def botinfo(ctx, *args):
	if len(args) != 0:
		await functions.wrong_call(ctx, 'botinfo')
		return

	commands = '$info symbol\n$price symbol\n$bought symbol price\n$daychange symbol\n$ath symbol\n$top n'
	examples = '$info btc\n$price btc\n$bought btc 21000\n$daychange btc\n$ath btc\n$top 10'
	
	date_now = dt.datetime.utcnow().strftime('%d-%b-%Y %H:%M UTC')	

	my_embed = discord.Embed(
		colour = discord.Colour.blurple()
	)	
	my_embed.set_author(name='Commands', icon_url='https://e7.pngegg.com/pngimages/305/948/png-clipart-computer-icons-exclamation-mark-others-miscellaneous-angle-thumbnail.png')
	my_embed.add_field(name='Command', value=commands, inline=True)
	my_embed.add_field(name='Example', value=examples, inline=True)
	my_embed.set_footer(text=f'Source: coingecko.com ☛ {date_now}')

	await ctx.send(embed=my_embed)
	return


TOKEN = environ.get('TOKEN')
client.run(TOKEN)