import os
import discord
from discord.ext import commands, tasks 
import requests
from datetime import datetime
from datetime import date
from constants import PRICE_ALERTS_CHANNEL, COINGECKO_ALLCOINS_URL, COINGECKO_COIN_DATA_URL, COINGECKO_COINS_PER_PAGE, COINGECKO_PRICE_CHANGE_LAST_HOUR
from constants import MONTH_NAMES
from errors import wrong_call_len, wrong_call


client = commands.Bot(command_prefix='!')


# Find coin_id('bitcoin') out of coin_symbol('btc')
def find_id(url, coin_symbol):
	data = requests.get(url).json()
	for coin in data:
		if coin['symbol'] == coin_symbol.lower() and 'binance-peg' not in coin['id']:
			return coin['id']


@client.event
async def on_ready():
	print(f'You have logged in as {client.user}')


# Checks the prices every hour to see the big market movers(+- 10%)
@tasks.loop(minutes=60)
async def last_hour_movers():
	await client.wait_until_ready() # without this it won't work

	data = requests.get(COINGECKO_PRICE_CHANGE_LAST_HOUR).json()
	coin_symbols = []
	response_positive = ''
	positive = False
	response_negative = ''
	negative = False
	channel = client.get_channel(PRICE_ALERTS_CHANNEL)
	image = 'https://img.favpng.com/6/10/11/stock-market-bull-priceu2013earnings-ratio-wish-png-favpng-gXsPEtZiBZEULjz07u2j4k5v7.jpg'

	for crypto in data:
		coin_symbol = crypto['symbol'].upper()
		coin_symbols.append(coin_symbol)
		coin_1h_change_percentage = crypto['price_change_percentage_1h_in_currency']
		if coin_1h_change_percentage > 10:
			positive = True
			response_positive += coin_symbol + ' +{:.2f}'.format(coin_1h_change_percentage) + '%\n'
		elif coin_1h_change_percentage < -10:
			negative = True
			response_negative += coin_symbol + ' {:.2f}'.format(coin_1h_change_percentage) + '%\n'

	if positive or negative:
		today = date.today()
		d2 = today.strftime("%B/%d/%Y")
		now = datetime.now()
		time_now = now.strftime("%H:%M:%S")
		date_now = d2 + ' at ' + time_now	

		my_embed = discord.Embed(
			colour = discord.Colour.blurple()
		)
		my_embed.set_author(name='Big market movers', icon_url=image)
		if positive:
			my_embed.add_field(name='Positive movers', value=response_positive, inline=True)
		else:
			my_embed.add_field(name='Positive movers', value='None', inline=True)
		if negative:
			my_embed.add_field(name='Negative movers', value=response_negative, inline=True)
		else:
			my_embed.add_field(name='Negative movers', value='None', inline=True)
		my_embed.set_footer(text='Source: coingecko.com ☛ ' + date_now)

		await channel.send(embed=my_embed)
		
	return


last_hour_movers.start()


# Checks for new ATH currencies every 30min
@tasks.loop(minutes=30)
async def new_ath():
	await client.wait_until_ready() # without this it won't work

	data = requests.get(COINGECKO_COINS_PER_PAGE).json()	
	response = ''
	found = False
	channel = client.get_channel(PRICE_ALERTS_CHANNEL) 
	date_now = datetime.now()
	image = 'https://cdn.iconscout.com/icon/premium/png-256-thumb/upward-arrow-2206687-1853775.png'

	for crypto in data:
		ath = crypto['ath']
		ath_date = crypto['ath_date']
		ath_year = int(ath_date[0:4])
		ath_month = int(ath_date[5:7])
		ath_day = int(ath_date[8:10])
		ath_hours = int(ath_date[11:13])
		ath_minutes = int(ath_date[14:16])
		ath_seconds = int(ath_date[17:19])
		ath_real_date = datetime(ath_year, ath_month, ath_day, ath_hours, ath_minutes, ath_seconds)
		difference = date_now - ath_real_date
		minutes = divmod(difference.total_seconds(), 60)

		if minutes[0] <= 30:
			response += crypto['symbol'].upper() + ' : ' + '{:,}'.format(ath) + '\n'
			found = True
		
	if found:
		today = date.today()
		d2 = today.strftime("%B/%d/%Y")
		now = datetime.now()
		time_now = now.strftime("%H:%M:%S")
		date_now = d2 + ' at ' + time_now	

		my_embed = discord.Embed(
			colour = discord.Colour.blurple()
		)
		my_embed.set_author(name='New ATH', icon_url=image)
		my_embed.add_field(name='Currencies', value=response, inline=True)
		my_embed.set_footer(text='Source: coingecko.com ☛ ' + date_now)

		await channel.send(embed=my_embed)
	
	return
		

new_ath.start()


# Info about currency such as ath, price, price change.. :!info symbol
@client.command(pass_context=True)
async def info(ctx, *args):
	if len(args) != 1:
		my_embed = wrong_call_len(ctx, 'info symbol')
		await ctx.send(embed=my_embed)
		return
	
	coin_symbol = args[0].lower()
	coin_id = find_id(COINGECKO_ALLCOINS_URL, coin_symbol)
	if coin_id == None:
		my_embed = wrong_call(ctx, 'make sure to provide us correct coin symbol.')
		await ctx.send(embed=my_embed)
		return

	data = requests.get(COINGECKO_COIN_DATA_URL.replace('COIN_ID_REPLACE', coin_id)).json()

	coin_name = data['name']
	coin_image = data['image']['small']
	coin_price = data['market_data']['current_price']['usd']
	coin_market_cap = data['market_data']['market_cap']['usd']
	coin_market_cap_rank = data['market_data']['market_cap_rank']
	coin_price_change_24h = data['market_data']['price_change_24h']
	coin_price_change_percentage_24h = data['market_data']['price_change_percentage_24h']
	if float(coin_price_change_24h) >= 0:
		coin_price_change_24h = '+{:,}'.format(coin_price_change_24h)
		coin_price_change_percentage_24h = '+{:,}'.format(coin_price_change_percentage_24h)
	else:
		coin_price_change_24h = '{:,}'.format(coin_price_change_24h)
		coin_price_change_percentage_24h = '{:,}'.format(coin_price_change_percentage_24h)
	coin_ath = data['market_data']['ath']['usd']
	coin_ath_date = data['market_data']['ath_date']['aed']
	coin_ath_year = coin_ath_date[0:4]
	coin_ath_month = MONTH_NAMES[int(coin_ath_date[5:7]) - 1]
	coin_ath_day = coin_ath_date[8:10]
	coin_ath_real_date = coin_ath_month + '/' + coin_ath_day + '/' + coin_ath_year

	today = date.today()
	d2 = today.strftime("%B/%d/%Y")
	now = datetime.now()
	time_now = now.strftime("%H:%M:%S")
	date_now = d2 + ' at ' + time_now	
	
	my_embed = discord.Embed(
		title = 'More info',
		url = 'https://www.coingecko.com/en/coins/' + coin_id,
		colour = discord.Colour.blurple() 
	)
	my_embed.set_author(name=coin_name + '(' + coin_symbol.upper() + ')', icon_url=coin_image)
	my_embed.add_field(name='Price', value='{:,}$'.format(coin_price), inline=True)
	my_embed.add_field(name='Market cap', value='#' + str(coin_market_cap_rank) + '\n{:,}'.format(coin_market_cap), inline=True)
	my_embed.add_field(name='ATH', value='{:,}'.format(coin_ath) + '\n' + coin_ath_real_date + '\n' + str(coin_ath_date[11:16]), inline=True)
	my_embed.add_field(name='Change(24h)', value=coin_price_change_24h + '$', inline=True)
	my_embed.add_field(name='Change(24h)', value=coin_price_change_percentage_24h + '%', inline=True)
	my_embed.set_footer(text='Source: coingecko.com ☛ ' + date_now)

	await ctx.send(embed=my_embed)
	return


# Check the price of symbol: !check symbol
@client.command()
async def price(ctx, *args):
	if len(args) != 1:
		my_embed = wrong_call_len(ctx, 'price symbol')
		await ctx.send(embed=my_embed)
		return

	coin_symbol = args[0].lower()
	coin_id = find_id(COINGECKO_ALLCOINS_URL, coin_symbol)
	if coin_id == None:
		my_embed = wrong_call(ctx, 'make sure to provide us correct coin symbol.')
		await ctx.send(embed=my_embed)
		return

	data = requests.get(COINGECKO_COIN_DATA_URL.replace('COIN_ID_REPLACE', coin_id)).json()
	
	coin_name = data['name']
	coin_image = data['image']['small']
	coin_price = data['market_data']['current_price']['usd']

	today = date.today()
	d2 = today.strftime("%B/%d/%Y")
	now = datetime.now()
	time_now = now.strftime("%H:%M:%S")
	date_now = d2 + ' at ' + time_now	
	
	my_embed = discord.Embed(
		colour = discord.Colour.blurple()
	)
	my_embed.set_author(name=coin_name + '(' + coin_symbol.upper() + ')', icon_url=coin_image)
	my_embed.add_field(name='Price', value='{:,}$'.format(coin_price), inline=True)
	my_embed.set_footer(text='Source: coingecko.com ☛ ' + date_now)

	await ctx.send(embed=my_embed)


# Check the percentage of (bought price - current price): !bought symbol bought_price
@client.command()
async def bought(ctx, *args):
	if len(args) != 2:
		my_embed = wrong_call_len(ctx, 'bought symbol price')
		await ctx.send(embed=my_embed)
		return

	coin_symbol = args[0].lower()
	try:
		bought_price = float(args[1].replace(',','.'))
		if bought_price <= 0:
			my_embed = wrong_call(ctx, 'make sure to provide us correct price.')
			await ctx.send(embed=my_embed)
			return
	except:
		my_embed = wrong_call(ctx, 'make sure to use the right call. (**!bought symbol price**)')
		await ctx.send(embed=my_embed)
		return

	coin_id = find_id(COINGECKO_ALLCOINS_URL, coin_symbol)
	if coin_id == None:
		my_embed = wrong_call(ctx, 'make sure to provide us correct symbol.')
		await ctx.send(embed=my_embed)
		return

	data = requests.get(COINGECKO_COIN_DATA_URL.replace('COIN_ID_REPLACE', coin_id)).json()

	coin_name = data['name']
	coin_image = data['image']['small']
	coin_current_price = data['market_data']['current_price']['usd']
	coin_percentage = ((float(coin_current_price) / float(bought_price))  - 1) * 100
	if coin_percentage > 0:
		response = '+{:,.2f}%'.format(coin_percentage)
	else:
		response = '{:,.2f}%'.format(coin_percentage)

	today = date.today()
	d2 = today.strftime("%B/%d/%Y")
	now = datetime.now()
	time_now = now.strftime("%H:%M:%S")
	date_now = d2 + ' at ' + time_now	
	
	my_embed = discord.Embed(
		colour = discord.Colour.blurple() 
	)
	my_embed.set_author(name=coin_name + '(' + coin_symbol.upper() + ')', icon_url=coin_image)
	if coin_percentage > 0:
		my_embed.add_field(name='Current profit', value=response, inline=True)
		my_embed.colour = discord.Colour.green()
	else:
		my_embed.add_field(name='Current loss', value=response, inline=True)
		my_embed.colour = discord.Colour.red()
	my_embed.set_footer(text='Source: coingecko.com ☛ ' + date_now)

	await ctx.send(embed=my_embed)	
	return


# 24h price change check: !daychange symbol
@client.command()
async def daychange(ctx, *args):
	if len(args) != 1:
		my_embed = wrong_call_len(ctx, 'daychange symbol')
		await ctx.send(embed=my_embed)
		return

	coin_symbol = args[0].lower()
	coin_id = find_id(COINGECKO_ALLCOINS_URL, coin_symbol)
	if coin_id == None:
		my_embed = wrong_call(ctx, 'make sure to provide us correct symbol.')
		await ctx.send(embed=my_embed)
		return

	data = requests.get(COINGECKO_COIN_DATA_URL.replace('COIN_ID_REPLACE', coin_id)).json()

	coin_name = data['name']
	coin_image = data['image']['small']
	coin_day_change = data['market_data']['price_change_24h']
	coin_day_change_percentage = data['market_data']['price_change_percentage_24h']
	if coin_day_change > 0:
		response_price = '+{:,.2f}$'.format(coin_day_change)
		response_percentage = '+{:,.2f}%'.format(coin_day_change_percentage)
	else:
		response_price = '{:,.2f}$'.format(coin_day_change)
		response_percentage = '{:,.2f}%'.format(coin_day_change_percentage)

	today = date.today()
	d2 = today.strftime("%B/%d/%Y")
	now = datetime.now()
	time_now = now.strftime("%H:%M:%S")
	date_now = d2 + ' at ' + time_now	
	
	my_embed = discord.Embed(
		colour = discord.Colour.blurple() 
	)
	my_embed.set_author(name=coin_name + '(' + coin_symbol.upper() + ')', icon_url=coin_image)
	if coin_day_change > 0:
		my_embed.add_field(name='Change(24h)', value=response_price, inline=True)
		my_embed.add_field(name='Change(24h)', value=response_percentage, inline=True)
		my_embed.colour = discord.Colour.green()
	else:
		my_embed.add_field(name='Change(24h)', value=response_price, inline=True)
		my_embed.add_field(name='Change(24h)', value=response_percentage, inline=True)
		my_embed.colour = discord.Colour.red()
	my_embed.set_footer(text='Source: coingecko.com ☛ ' + date_now)

	await ctx.send(embed=my_embed)
	return


# ATH check: !ath symbol
@client.command()
async def ath(ctx, *args):
	if len(args) != 1:
		my_embed = wrong_call_len(ctx, 'ath symbol')
		await ctx.send(embed=my_embed)
		return

	coin_symbol = args[0].lower()
	coin_id = find_id(COINGECKO_ALLCOINS_URL, coin_symbol)
	if coin_id == None:	
		my_embed = wrong_call(ctx, 'make sure to provide us correct symbol.')
		await ctx.send(embed=my_embed)
		return

	data = requests.get(COINGECKO_COIN_DATA_URL.replace('COIN_ID_REPLACE', coin_id)).json()

	coin_name = data['name']
	coin_image = data['image']['small']
	coin_ath = data['market_data']['ath']['usd']
	coin_ath_date = data['market_data']['ath_date']['aed']
	day = coin_ath_date[8:10]
	month = MONTH_NAMES[int(coin_ath_date[5:7]) - 1]
	year = coin_ath_date[0:4]
	coin_ath_percentage_down = data['market_data']['ath_change_percentage']['usd']

	today = date.today()
	d2 = today.strftime("%B/%d/%Y")
	now = datetime.now()
	time_now = now.strftime("%H:%M:%S")
	date_now = d2 + ' at ' + time_now	
	
	my_embed = discord.Embed(
		colour = discord.Colour.blurple() 
	)
	my_embed.set_author(name=coin_name + '(' + coin_symbol.upper() + ')', icon_url=coin_image)
	my_embed.add_field(name='ATH', value='{:,.2f}'.format(coin_ath) + '$', inline=True)
	my_embed.add_field(name='Date', value=month + '/' + day + '/' + year, inline=True)
	my_embed.add_field(name='Down(%)', value='{:,.2f}'.format(coin_ath_percentage_down) + '%', inline=True)
	my_embed.set_footer(text='Source: coingecko.com ☛ ' + date_now)

	await ctx.send(embed=my_embed)
	return


# Shows top n coins by market cap n ∈ [0,50]
@client.command()
async def top(ctx, *args):
	if len(args) != 1:
		my_embed = wrong_call_len(ctx, 'top n')
		await ctx.send(embed=my_embed)
		return
	try:
		n = int(args[0])
		if n < 1 or n > 50:
			my_embed = wrong_call(ctx, 'make sure to provide us correct number (0-50).')
			await ctx.send(embed=my_embed)
			return 
	except:
		my_embed = wrong_call(ctx, 'top n')
		await ctx.send(embed=my_embed)
		return

	respond_symbols = ''
	respond_prices = ''
	respond_market_cap = ''

	data = requests.get(COINGECKO_COINS_PER_PAGE).json() 

	i = 0
	for crypto in data:
		if i == n:
			break
		respond_symbols += str(crypto['symbol']).upper() + '\n'
		respond_prices += '{:,}'.format(crypto['current_price']) + '\n'
		respond_market_cap += '{:,}'.format(crypto['market_cap']) + '\n'
		i += 1

	today = date.today()
	d2 = today.strftime("%B/%d/%Y")
	now = datetime.now()
	time_now = now.strftime("%H:%M:%S")
	date_now = d2 + ' at ' + time_now

	my_embed = discord.Embed(
		title = 'More info',
		url = 'https://www.coingecko.com/en',
		colour = discord.Colour.blurple()
	)
	my_embed.set_author(name='Top' + str(n) + ' coins', url='', icon_url='https://png.pngtree.com/png-clipart/20210310/original/pngtree-3d-trophy-with-first-second-third-winner-png-image_5931060.jpg')
	my_embed.add_field(name='Symbol', value=respond_symbols, inline=True)
	my_embed.add_field(name='Price', value=respond_prices, inline=True)
	my_embed.add_field(name='Market cap', value=respond_market_cap, inline=True)
	my_embed.set_footer(text='Source: coingecko.com ☛ ' + date_now)

	await ctx.send(embed=my_embed)
	return


# Help command for commands and tasks
@client.command()
async def botinfo(ctx, *args):
	if len(args) != 0:
		my_embed = wrong_call_len(ctx, 'botinfo')
		await ctx.send('botinfo')
		return

	commands = '!price symbol\n!bought symbol price\n!daychange symbol\n!ath symbol\n!info symbol\n!top n'
	examples = '!price btc\n!bought btc 21000\n!daychange btc\n!ath btc\n!info btc\n!top 10'
	
	today = date.today()
	d2 = today.strftime("%B/%d/%Y")
	now = datetime.now()
	time_now = now.strftime("%H:%M:%S")
	date_now = d2 + ' at ' + time_now

	my_embed = discord.Embed(
		colour = discord.Colour.blurple()
	)	
	my_embed.set_author(name='Commands', icon_url='https://e7.pngegg.com/pngimages/305/948/png-clipart-computer-icons-exclamation-mark-others-miscellaneous-angle-thumbnail.png')
	my_embed.add_field(name='Command', value=commands, inline=True)
	my_embed.add_field(name='Example', value=examples, inline=True)
	my_embed.set_footer(text='Source: coingecko.com ☛ ' + date_now)

	await ctx.send(embed=my_embed)
	return


TOKEN = os.environ['TOKEN_SECRET']
client.run(TOKEN)