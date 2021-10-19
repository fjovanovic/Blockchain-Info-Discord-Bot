import os
from discord.ext import commands 
import requests

client = commands.Bot(command_prefix='!')

@client.event
async def on_ready():
	print(f'You have logged in as {client.user}')

# Works everything fine !check symbol
@client.command()
async def price(ctx, symbol):
	url = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd'
	data = requests.get(url).json()
	not_found = True

	for crypto in data:
		if symbol.lower() == crypto['symbol']:
			not_found = False
			current_price = crypto['current_price']
			print('Current price of {} is {:,}'.format(symbol.upper(), current_price))
			await ctx.send('Current price of {} is {:,}'.format(symbol.upper(), current_price))
	if not_found:
		await ctx.send('Either you sent wrong symbol or currency is not in top 100')

# Works everything fine !bought symbol bought_price
@client.command()
async def bought(ctx, symbol, bought_price):
	bought_price_real = bought_price.replace(',','.') # can't replace arguments, you 														need new variable
	print(f'You bought {symbol} at price of {bought_price_real}')

	if float(bought_price_real) < 0:
		await ctx.send('Price is not correct, please send us correct price')
		return

	url = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd'
	data = requests.get(url).json()
	not_found = True
	
	for crypto in data:
		if symbol.lower() == crypto['symbol']:
			not_found = False
			current_price = crypto['current_price']
			percentage = ((float(current_price) / float(bought_price_real))  - 1) * 100
			if percentage > 0:
				print('You are currently {:.2f}% in profit'.format(percentage))
				await ctx.send('You are currently {:.2f}% in profit'.format(percentage))
			else:
				print('You are currently {:.2f}% in loss'.format(percentage))
				await ctx.send('You are currently {:.2f}% in loss'.format(percentage))
	if not_found:
		await ctx.send('Either you sent wrong symbol or currency is not in top 100')

# Works everything fine, !daychange symbol
@client.command()
async def daychange(ctx, symbol):
	url = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd'
	data = requests.get(url).json()
	not_found = True

	for crypto in data:
		if symbol.lower() == crypto['symbol']:
			not_found = False
			day_change = crypto['price_change_24h']
			day_change_percentage = crypto['price_change_percentage_24h']
			print('24h change for {} is {}, which is {}%'.format(symbol, day_change, day_change_percentage))
			await ctx.send('24h change for {} is {}, which is {}%'.format(symbol, day_change, day_change_percentage))
	if not_found:
		await ctx.send('Either you sent wrong symbol or currency is not in top 100')

# Work everything fine, !ath symbol
@client.command()
async def ath(ctx, symbol):
	url = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd'
	data = requests.get(url).json()
	not_found = True
	
	for crypto in data:
		if symbol.lower() == crypto['symbol']:
			not_found = False
			ath = crypto['ath']
			ath_date = crypto['ath_date']
			day = ath_date[8] + ath_date[9]
			month = ath_date[5] + ath_date[6]
			year = ath_date[0] + ath_date[1] + ath_date[2] + ath_date[3]
			ath_percentage_down = crypto['ath_change_percentage']
			print('ATH for {} is at {:,}, on {}.{}.{}, which is {:.2f}% down'.format(symbol.upper(), ath, day, month, year, ath_percentage_down))
			await ctx.send('ATH for {} is at {:,}, on {}.{}.{}, which is {:.2f}% down'.format(symbol.upper(), ath, day, month, year, ath_percentage_down))
	if not_found:
		await ctx.send('Either you sent wrong symbol or currency is not in top 100')	


TOKEN = os.environ['TOKEN_SECRET']
client.run(TOKEN)