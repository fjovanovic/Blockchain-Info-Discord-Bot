import os
from discord.ext import commands, tasks
import requests
from keep_alive import keep_alive
from replit import db
from constants import PRICE_ALERTS_CHANNEL, COINGECKO_COINS_MARKETS_URL

client = commands.Bot(command_prefix='!')


@client.event
async def on_ready():
    print(f'You have logged in as {client.user}')


# Checks the prices every hour to see the big market movers(+- 10%)
@tasks.loop(minutes=60)
async def update_database():
    await client.wait_until_ready()  # without this it won't work
    print('price-check-1h')

    data = requests.get(COINGECKO_COINS_MARKETS_URL).json()
    symbols = []

    text_positive = 'Next cryptocurrencies are up at least 10% in past hour:\n'
    positive = False

    text_negative = 'Next cryptocurrencies are down at least 10% in past hour:\n'
    negative = False

    channel = client.get_channel(PRICE_ALERTS_CHANNEL)

    for i in range(len(data)):
        current_price = data[i]['current_price']
        symbol = data[i]['symbol']

        if symbol not in db.keys():
            price_1h_ago = current_price
            percentage = 0
        else:
            price_1h_ago = db[symbol]
            percentage = ((float(current_price) / float(price_1h_ago)) - 1) * 100

        db[symbol] = current_price
        symbols.append(symbol)

        # print(symbol + ' ' + str(current_price) + ' ' + str(price_1h_ago) + ' ' + str(round(percentage, 2)))

        if percentage > 10:
            positive = True
            text_positive += symbol + ' +' + str(round(percentage, 2)) + '%\n'
        elif percentage < -10:
            negative = True
            text_negative += symbol + ' ' + str(round(percentage, 2)) + '%\n'

    if positive:
        print(text_positive)
        await channel.send(text_positive)
    elif negative:
        print(text_negative)
        await channel.send(text_negative)

    for key in db.keys():
        if key not in symbols:
            del db[key]


update_database.start()


# Check the price of symbol: !check symbol
@client.command()
async def price(ctx, symbol):
    data = requests.get(COINGECKO_COINS_MARKETS_URL).json()

    for crypto in data:
        if symbol.lower() == crypto['symbol']:
            await ctx.send('Current price of {} is {:,}'.format(symbol.upper(), crypto['current_price']))
            return

    await ctx.send('Either you sent wrong symbol or currency is not in top 100')
    return


# Check the percentage of (bought price - current price): !bought symbol bought_price
@client.command()
async def bought(ctx, symbol, bought_price):
    bought_price_real = bought_price.replace(',', '.')  # can't replace arguments, you need new variable
    print(f'You bought {symbol} at price of {bought_price_real}')

    if float(bought_price_real) < 0:
        await ctx.send('Price is not correct, please send us correct price')
        return

    data = requests.get(COINGECKO_COINS_MARKETS_URL).json()

    for crypto in data:
        if symbol.lower() == crypto['symbol']:
            percentage = ((float(crypto['current_price']) / float(bought_price_real)) - 1) * 100
            if percentage > 0:
                await ctx.send('You are currently {:.2f}% in profit'.format(percentage))
                return
            else:
                await ctx.send('You are currently {:.2f}% in loss'.format(percentage))
                return

    await ctx.send('Either you sent wrong symbol or currency is not in top 100')
    return


# 24h price change check: !daychange symbol
@client.command()
async def daychange(ctx, symbol):
    data = requests.get(COINGECKO_COINS_MARKETS_URL).json()

    for crypto in data:
        if symbol.lower() == crypto['symbol']:
            day_change = crypto['price_change_24h']
            day_change_percentage = crypto['price_change_percentage_24h']
            if day_change < 0:
                await ctx.send('24h change for {} is {}, which is {}%'.
                               format(symbol, day_change, day_change_percentage))
                return
            else:
                await ctx.send('24h change for {} is {}, which is +{}%'.
                               format(symbol, day_change, day_change_percentage))
                return

    await ctx.send('Either you sent wrong symbol or currency is not in top 100')
    return


# ATH check: !ath symbol
@client.command()
async def ath(ctx, symbol):
    data = requests.get(COINGECKO_COINS_MARKETS_URL).json()

    for crypto in data:
        if symbol.lower() == crypto['symbol']:
            ath = crypto['ath']
            ath_date = crypto['ath_date']
            day = ath_date[8] + ath_date[9]
            month = ath_date[5] + ath_date[6]
            year = ath_date[0] + ath_date[1] + ath_date[2] + ath_date[3]
            ath_percentage_down = crypto['ath_change_percentage']
            await ctx.send('ATH for {} is at {:,}, on {}.{}.{}, which is {:.2f}% down'.
                           format(symbol.upper(), ath, day, month, year, ath_percentage_down))
            return

    await ctx.send('Either you sent wrong symbol or currency is not in top 100')
    return


TOKEN = os.environ['TOKEN_SECRET']
keep_alive()
client.run(TOKEN)
