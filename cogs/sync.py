from typing import Optional, Literal

import discord
from discord.ext.commands import Context, Greedy
from discord.ext import commands
from discord.ext.commands import Cog, Bot


class Sync(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
    
    
    @commands.command(name='sync')
    @commands.guild_only()
    @commands.is_owner()
    async def sync(self, ctx: Context, guilds: Greedy[discord.Object], spec: Optional[Literal['~', '*', '^']] = None):
        if not guilds:
            if spec == '~':
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == '*':
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == '^':
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await ctx.bot.tree.sync()

            await ctx.send(f'Synced {len(synced)} commands {"globally" if spec is None else "to the current guild."}')
            return

        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1

        await ctx.send(f'Synced the tree to {ret}/{len(guilds)}.')
        
        
    async def cog_load(self) -> None:
        print(f'Cog loaded: {self.__class__.__name__}')


async def setup(bot: Bot) -> None:
    await bot.add_cog(Sync(bot=bot))