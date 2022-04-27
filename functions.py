from discord import Embed, Colour
from json import load


async def wrong_call(ctx, error_message):
    user_id = ctx.author.id
    user_mention = f'<@{user_id}>'
    
    my_embed = Embed(
        colour = Colour.red()
    )

    my_embed.add_field(name='⛔Wrong call', value=f'{user_mention}, make sure to use the right call. (**${error_message}**)')

    await ctx.send(embed=my_embed)
    return  


async def error(ctx, error_name, error_message):
    user_id = ctx.author.id
    user_mention = f'<@{user_id}>'
    
    my_embed = Embed(
        colour = Colour.red()
    )

    my_embed.add_field(name=f'⛔{error_name}', value=f'{user_mention}, {error_message}')

    await ctx.send(embed=my_embed)
    return  


def find_id(coin_symbol):
    with open('coingecko\\all_coins.json', 'r') as f:
        data = load(f)
        for coin in data:
            if coin['symbol'] == coin_symbol.lower() and 'binance-peg' not in coin['id']:
                return coin['id']
    return None