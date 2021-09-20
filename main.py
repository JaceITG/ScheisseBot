import sys, os
from colour import Color

import util.checks, util.errors

import discord, typing
from discord.ext import commands
from configparser import ConfigParser
from discord import Intents
from discord.ext.commands.errors import ArgumentParsingError
intents = Intents.all()

config = ConfigParser()
config.read('config.ini')
config = config['general']
PREFIX = config['prefix']

bot = commands.Bot(intents=intents, command_prefix=PREFIX)
scheisse = bot.get_user(int(config['adminid']))

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

######## ADMIN ########

@bot.command()
@commands.is_owner()
async def purge(ctx, amount: typing.Optional[int] = 100):
    deleted = await ctx.channel.purge(limit=amount)
    print('Purged {0} messages'.format(len(deleted)))

######## SERVER/META ########
@bot.command(aliases=['rolerequest','request','rr'])
@util.checks._is_channel(config['rolechan'])
async def role(ctx, *args):

    if len(args)<2:
        raise util.errors.UsageError        
    
    argstr = ' '.join(args)

    try:
        color = await _parse_to_hex(argstr[0:argstr.find(',')])
    except ValueError:
        raise util.errors.BadColor

    role_name = argstr[argstr.find(',')+2:]

    if len(role_name)<1:
        raise util.errors.UsageError
    
    #await ctx.send(f"Color: {color} Role Name: {argstr[argstr.find(',')+2:]}")
    reqdesc = 'Color: `{0}`\nName: `{0}'.format(color,role_name)
    reqemb = discord.Embed(title=f"Role request from {ctx.author.display_name}", description=reqdesc)
    reqemb.set_thumbnail(url=ctx.author.avatar_url)
    
    sentemb = _send(scheisse, embed=reqemb)
    



@role.error
async def role_error(ctx, error):
    if isinstance(error, util.errors.UsageError):
        await _send(ctx, embed=await _err_embed('Usage: {0}role [color], [name]'.format(PREFIX), '{0}role #ff1493, Cool Guy'.format(PREFIX)))
    elif isinstance(error, util.errors.BadColor):
        await _send(ctx, embed=await _err_embed('Invalid color. Must be interpreted color name, RGB value, or hex string starting with #'.format(PREFIX), '{0}role #ff1493, Cool Guy'.format(PREFIX)))
    else:
        print(error)

######## MISC ########

@bot.command(aliases=["test"])
async def echo(ctx, *arg):
    await ctx.send(' '.join(arg) or "echo")

######## HELPER FUNCS ########

async def _send(ctx, msg=None, embed=None, file=None):
    try:
        return await ctx.send(content=msg, embed=embed, file=file)
    except Exception as e:
        print('Error while sending message in {0.channel}: {0}'.format(ctx,e))

async def _err_embed(msg, example=None):
    emb = discord.Embed(description=msg, color=discord.Color.dark_red())

    if example:
        emb.add_field(name='Example:', value=example)

    return emb

async def _parse_to_hex(colorstr):
    try:
        c = Color(colorstr)
    except ValueError as e:
        raise commands.ArgumentParsingError
    return c.hex_l

bot.run(os.getenv('TOKEN'))

