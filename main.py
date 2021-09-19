import sys, os

import discord, typing
from discord.ext import commands
from configparser import ConfigParser
from discord import Intents
intents = Intents.all()

config = ConfigParser()
config.read('config.ini')

bot = commands.Bot(intents=intents, command_prefix=config['general']['prefix'])


@bot.command(aliases=["test"])
async def echo(ctx, *arg):
    await ctx.send(' '.join(arg) or "echo")

@bot.command()
@commands.is_owner()
async def purge(ctx, amount: typing.Optional[int] = 100):
    await ctx.channel.purge(limit=amount)

bot.run(os.getenv('TOKEN'))

