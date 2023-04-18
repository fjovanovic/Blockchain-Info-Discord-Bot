import logging
from aiohttp import client_exceptions

from discord import Interaction
from discord.app_commands import CommandTree, AppCommandError, CommandInvokeError

from utils import errors


class MyCommandTree(CommandTree):
    async def on_error(self, interaction: Interaction, error: AppCommandError) -> None:
        logging.exception(error)

        if isinstance(error, CommandInvokeError):
            error = error.original
        
        if isinstance(error, client_exceptions.InvalidURL):
            await errors.coin_not_found(interaction)
        else:
            await errors.unexpected_error(interaction)