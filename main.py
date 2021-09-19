import sys, os

import discord
from discord.ext import commands
from configparser import ConfigParser
from discord import Intents
intents = Intents.all()

config = ConfigParser
config.read("config.ini")

bot = commands.Bot(intents=intents, command_prefix=config.options("prefix"))

@bot.command(aliases=["test"])
async def echo(ctx):
    await ctx.send(ctx.message.content)

bot.run()

