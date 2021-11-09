import os
import discord
from discord.ext import commands, tasks 
import requests
from keep_alive import keep_alive
from replit import db
from datetime import datetime
from datetime import date
from constants import PRICE_ALERTS_CHANNEL, COINGECKO_COINS_URL

client = commands.Bot(command_prefix='!')

@client.event
async def on_ready():
	print(f'You have logged in as {client.user}')


# Checks the prices every hour to see the big market movers(+- 10%)
@tasks.loop(minutes=60)
async def last_hour_movers():
	await client.wait_until_ready() # without this it won't work

	data = requests.get(COINGECKO_COINS_URL).json()
	symbols = []
	response_positive = ''
	positive = False
	response_negative = ''
	negative = False
	channel = client.get_channel(PRICE_ALERTS_CHANNEL)
	image = 'https://img.favpng.com/6/10/11/stock-market-bull-priceu2013earnings-ratio-wish-png-favpng-gXsPEtZiBZEULjz07u2j4k5v7.jpg'

	for i in range(len(data)):
		current_price = data[i]['current_price']
		symbol = data[i]['symbol'].upper()

		if symbol not in db.keys():
			price_1h_ago = current_price
			percentage = 0
		else:
			price_1h_ago = db[symbol]
			percentage = ((float(current_price) / float(price_1h_ago))  - 1) * 100

		db[symbol] = current_price
		symbols.append(symbol)

		if percentage > 10:
			positive = True
			response_positive += symbol + ' +{:.2f}'.format(percentage) + '%\n'
		elif percentage < -10:
			negative = True
			response_negative += symbol + ' {:.2f}'.format(percentage) + '%\n'

	if positive or negative:
		today = date.today()
		d2 = today.strftime("%B/%d/%Y")
		now = datetime.now()
		time_now = now.strftime("%H:%M:%S")
		date_now = d2 + ' at ' + time_now	

		my_embed = discord.Embed(
			colour = discord.Colour.purple()
		)
		my_embed.set_author(name='Big market movers(+- 10%)', icon_url=image)
		my_embed.add_field(name='Positive movers', value=response_positive, inline=True)
		my_embed.add_field(name='Negative movers', value=response_negative, inline=True)
		my_embed.set_footer(text='Source: coingecko.com ☛ ' + date_now)

		await channel.send(embed=my_embed)
		
	for key in db.keys():
		if key not in symbols:
			del db[key]


last_hour_movers.start()


# Checks for new ATH currencies every 30min
@tasks.loop(minutes=30)
async def new_ath():
	await client.wait_until_ready() # without this it won't work

	data = requests.get(COINGECKO_COINS_URL).json()	
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
			colour = discord.Colour.purple()
		)
		my_embed.set_author(name='New ATH', icon_url=image)
		my_embed.add_field(name='Currencies', value=response, inline=True)
		my_embed.set_footer(text='Source: coingecko.com ☛ ' + date_now)

		await channel.send(embed=my_embed)
		

new_ath.start()


@client.command(pass_context=True)
async def info(ctx, *args):
	if len(args) != 1:
		await ctx.send('Command !info is not used properly. (!info symbol)')
		return
	symbol = args[0]
	data = requests.get(COINGECKO_COINS_URL).json()
	not_found = True

	for crypto in data:
		if crypto['symbol'].lower() == symbol.lower():
			id = crypto['id']
			name = crypto['name']
			image = crypto['image']
			price = crypto['current_price']
			market_cap = crypto['market_cap']
			market_cap_rank = crypto['market_cap_rank']
			price_change_24h = crypto['price_change_24h']
			price_change_percentage = crypto['price_change_percentage_24h']
			if float(price_change_24h) >= 0:
				price_change_24h = '+{:,}'.format(price_change_24h)
				price_change_percentage = '+{:,}'.format(price_change_percentage)
			else:
				price_change_24h = '{:,}'.format(price_change_24h)
				price_change_percentage = '{:,}'.format(price_change_percentage)
			ath = crypto['ath']
			ath_date = crypto['ath_date']
			ath_year = ath_date[0:4]
			ath_month = ath_date[5:7]
			ath_day = ath_date[8:10]
			ath_real_date = ath_month + '/' + ath_day + '/' + ath_year
			not_found = False
			break

	if not_found:
		await ctx.send('Make sure that you entered correct symbol')
		return

	today = date.today()
	d2 = today.strftime("%B/%d/%Y")
	now = datetime.now()
	time_now = now.strftime("%H:%M:%S")
	date_now = d2 + ' at ' + time_now	
	
	my_embed = discord.Embed(
		title = 'More info',
		url = 'https://www.coingecko.com/en/coins/' + id,
		colour = discord.Colour.purple() 
	)
	my_embed.set_author(name=name + '(' + symbol.upper() + ')', icon_url=image)
	my_embed.add_field(name='Price', value='{:,}$'.format(price), inline=True)
	my_embed.add_field(name='Market cap', value='#' + str(market_cap_rank) + '\n{:,}'.format(market_cap), inline=True)
	my_embed.add_field(name='ATH', value='{:,}'.format(ath) + '\n' + ath_real_date + '\n' + str(ath_date[11:16]), inline=True)
	my_embed.add_field(name='Change(24h)', value=price_change_24h + '$', inline=True)
	my_embed.add_field(name='Change(24h)', value=price_change_percentage + '%', inline=True)
	my_embed.set_image(url='https://cdn.wallpapersafari.com/71/88/InUZKu.png')
	my_embed.set_footer(text='Source: coingecko.com ☛ ' + date_now)

	await ctx.send(embed=my_embed)


# Check the price of symbol: !check symbol
@client.command()
async def price(ctx, *args):
	if len(args) != 1:
		await ctx.send('Command !price is not used properly. (!price symbol)')
		return
	symbol = args[0]
	data = requests.get(COINGECKO_COINS_URL).json()
	not_found = True

	for crypto in data:
		if crypto['symbol'].lower() == symbol.lower():
			name = crypto['name']
			image = crypto['image']
			price = crypto['current_price']
			not_found = False
			break
	if not_found:
		await ctx.send('Either you sent wrong symbol or currency is not in top 100')
		return

	today = date.today()
	d2 = today.strftime("%B/%d/%Y")
	now = datetime.now()
	time_now = now.strftime("%H:%M:%S")
	date_now = d2 + ' at ' + time_now	
	
	my_embed = discord.Embed(
		colour = discord.Colour.purple() 
	)
	my_embed.set_author(name=name + '(' + symbol.upper() + ')', icon_url=image)
	my_embed.add_field(name='Price', value='{:,}$'.format(price), inline=True)
	my_embed.set_footer(text='Source: coingecko.com ☛ ' + date_now)

	await ctx.send(embed=my_embed)


# Check the percentage of (bought price - current price): !bought symbol bought_price
@client.command()
async def bought(ctx, *args):
	if len(args) != 2:
		await ctx.send('Command !bought is not used properly. (!bought symbol bought_price)')
		return
	symbol = args[0]
	bought_price = args[1].replace(',','.')

	if float(bought_price) < 0:
		await ctx.send('Price is not correct, please send us correct price')
		return

	data = requests.get(COINGECKO_COINS_URL).json()
	not_found = True

	for crypto in data:
		if crypto['symbol'].lower() == symbol.lower():
			name = crypto['name']
			image = crypto['image']
			current_price = crypto['current_price']
			percentage = ((float(current_price) / float(bought_price))  - 1) * 100
			if percentage > 0:
				response = '+{:,.2f}%'.format(percentage)
			else:
				response = '{:,.2f}%'.format(percentage)
			not_found = False
			break
	if not_found:
		await ctx.send('Either you sent wrong symbol or currency is not in top 100')
		return

	today = date.today()
	d2 = today.strftime("%B/%d/%Y")
	now = datetime.now()
	time_now = now.strftime("%H:%M:%S")
	date_now = d2 + ' at ' + time_now	
	
	my_embed = discord.Embed(
		colour = discord.Colour.purple() 
	)
	my_embed.set_author(name=name + '(' + symbol.upper() + ')', icon_url=image)
	if percentage > 0:
		my_embed.add_field(name='Current profit', value=response, inline=True)
		my_embed.colour = discord.Colour.green()
	else:
		my_embed.add_field(name='Current loss', value=response, inline=True)
		my_embed.colour = discord.Colour.red()
	my_embed.set_footer(text='Source: coingecko.com ☛ ' + date_now)

	await ctx.send(embed=my_embed)	


# 24h price change check: !daychange symbol
@client.command()
async def daychange(ctx, *args):
	if len(args) != 1:
		await ctx.send('Command !daychange is not used properly. (!daychange symbol)')
		return
	symbol = args[0]
	data = requests.get(COINGECKO_COINS_URL).json()
	not_found = True

	for crypto in data:
		if crypto['symbol'].lower() == symbol.lower():
			name = crypto['name']
			image = crypto['image']
			day_change = crypto['price_change_24h']
			day_change_percentage = crypto['price_change_percentage_24h']
			if day_change > 0:
				response_price = '+{:,.2f}$'.format(day_change)
				response_percentage = '+{:,.2f}%'.format(day_change_percentage)
			else:
				response_price = '{:,.2f}$'.format(day_change)
				response_percentage = '{:,.2f}%'.format(day_change_percentage)
			not_found = False
			break
	if not_found:
		await ctx.send('Either you sent wrong symbol or currency is not in top 100')
		return

	today = date.today()
	d2 = today.strftime("%B/%d/%Y")
	now = datetime.now()
	time_now = now.strftime("%H:%M:%S")
	date_now = d2 + ' at ' + time_now	
	
	my_embed = discord.Embed(
		colour = discord.Colour.purple() 
	)
	my_embed.set_author(name=name + '(' + symbol.upper() + ')', icon_url=image)
	if day_change > 0:
		my_embed.add_field(name='Change(24h)', value=response_price, inline=True)
		my_embed.add_field(name='Change(24h)', value=response_percentage, inline=True)
		my_embed.colour = discord.Colour.green()
	else:
		my_embed.add_field(name='Change(24h)', value=response_price, inline=True)
		my_embed.add_field(name='Change(24h)', value=response_percentage, inline=True)
		my_embed.colour = discord.Colour.red()
	my_embed.set_footer(text='Source: coingecko.com ☛ ' + date_now)

	await ctx.send(embed=my_embed)


# ATH check: !ath symbol
@client.command()
async def ath(ctx, *args):
	if len(args) != 1:
		await ctx.send('Command !ath is not used properly. (!ath symbol)')
		return
	symbol = args[0]
	data = requests.get(COINGECKO_COINS_URL).json()
	not_found = True
	
	for crypto in data:
		if crypto['symbol'].lower() == symbol.lower():
			name = crypto['name']
			image = crypto['image']
			ath = crypto['ath']
			ath_date = crypto['ath_date']
			day = ath_date[8:10]
			month = ath_date[5:7]
			year = ath_date[0:4]
			ath_percentage_down = crypto['ath_change_percentage']
			not_found = False
			break
	if not_found:
		await ctx.send('Either you sent wrong symbol or currency is not in top 100')
		return

	today = date.today()
	d2 = today.strftime("%B/%d/%Y")
	now = datetime.now()
	time_now = now.strftime("%H:%M:%S")
	date_now = d2 + ' at ' + time_now	
	
	my_embed = discord.Embed(
		colour = discord.Colour.purple() 
	)
	my_embed.set_author(name=name + '(' + symbol.upper() + ')', icon_url=image)
	my_embed.add_field(name='ATH', value='{:,.2f}'.format(ath) + '$', inline=True)
	my_embed.add_field(name='Date', value=month + '/' + day + '/' + year, inline=True)
	my_embed.add_field(name='Down(%)', value='{:,.2f}'.format(ath_percentage_down), inline=True)
	my_embed.set_footer(text='Source: coingecko.com ☛ ' + date_now)

	await ctx.send(embed=my_embed)


TOKEN = os.environ['TOKEN_SECRET']
keep_alive()
client.run(TOKEN)