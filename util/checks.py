from discord.ext import commands
from discord.ext.commands.errors import CheckFailure

def _is_channel(channel_id: int):
    async def predicate(ctx):
        return ctx.guild and ctx.channel.id == channel_id
    return commands.check(predicate)