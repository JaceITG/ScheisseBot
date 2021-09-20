from discord.ext import commands
from discord.ext.commands.errors import CheckFailure

def _is_channel(channel_id: int):
    def predicate(ctx):
        return ctx.channel.id == int(channel_id)
    return commands.check(predicate)