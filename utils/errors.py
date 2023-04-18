from discord import Interaction, Embed, Colour


async def api_problem(interaction: Interaction) -> None:
    my_embed = Embed(
        colour = Colour.red()
    )

    my_embed.add_field(name='⛔Problem with API', value=f'We have a problem with API, please inform admin team')
    
    await interaction.followup.send(embed=my_embed)


async def coin_not_found(interaction: Interaction) -> None:
    my_embed = Embed(
        colour = Colour.red()
    )

    my_embed.add_field(name='⛔Coin not found', value=f'Make sure to provide a correct coin symbol')
    
    await interaction.followup.send(embed=my_embed)


async def unexpected_error(interaction: Interaction) -> None:
    my_embed = Embed(
        colour = Colour.red()
    )

    my_embed.add_field(name='⛔Unexpected error', value='An unexpected error has occured. Please contact the admin')

    await interaction.followup.send(embed=my_embed)


async def wrong_position_type(interaction: Interaction) -> None:
    my_embed = Embed(
        colour = Colour.red()
    )

    my_embed.add_field(name='⛔Wrong position type', value='Position type can be either buy or sell')

    await interaction.followup.send(embed=my_embed)


async def wrong_topn_number(interaction: Interaction) -> None:
    my_embed = Embed(
        colour = Colour.red()
    )

    my_embed.add_field(name='⛔Wrong number', value='Number of coins must be between 1 and 30')

    await interaction.followup.send(embed=my_embed)