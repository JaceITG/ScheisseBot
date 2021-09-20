import sys, os

import discord, typing
from discord.ext import commands
from configparser import ConfigParser
from discord import Intents
intents = Intents.all()

config = ConfigParser()
config.read('config.ini')

bot = commands.Bot(intents=intents, command_prefix=config['general']['prefix'])

######## ADMIN ########

@bot.command()
@commands.is_owner()
async def purge(ctx, amount: typing.Optional[int] = 100):
    await ctx.channel.purge(limit=amount)

######## SERVER/META ########
@bot.command(aliases=['rolerequest','request','rr'])
async def role(ctx, *args):
    if len(args)<2:
        await ctx.send()

######## MISC ########

@bot.command(aliases=["test"])
async def echo(ctx, *arg):
    await ctx.send(' '.join(arg) or "echo")

######## HELPER FUNCS ########

async def _err_embed(msg):
    emb = discord.Embed(description=msg, color=discord.Color.dark_red)
    return emb


bot.run(os.getenv('TOKEN'))

