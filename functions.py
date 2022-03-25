import discord


def wrong_call_len(ctx, error_message):
    user_id = ctx.author.id
    user_mention = f'<@{user_id}>'
    my_embed = discord.Embed(
        colour = discord.Colour.red()
    )

    my_embed.add_field(name='⛔Wrong call', value=user_mention + ', make sure to use the right call. (**!' + error_message + '**)')
    return my_embed   


def wrong_call(ctx, error_message):
    user_id = ctx.author.id
    user_mention = f'<@{user_id}>'
    my_embed = discord.Embed(
        colour = discord.Colour.red()
    )

    my_embed.add_field(name='⛔Wrong call', value=user_mention + ', ' + error_message)
    return my_embed   