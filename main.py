import sys, os
from colour import Color

import util.checks

import music

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
mainserver = None


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

    global mainserver
    mainserver = await bot.fetch_guild(int(config['mainserver']))

    music.setup(bot)

######## REACTION HANDLING ########

@bot.event
async def on_reaction_add(reaction, user):
    #ignore self
    if user.bot:
        return
    
    message = reaction.message
    embeds = message.embeds

    if embeds:
        emb = embeds[0]

        #role request confirmation
        if message.channel.id == int(config['confirmchan']) and emb.title.startswith("Role request"):
            if reaction.emoji == '✅':
                #accept
                color = emb.color
                member = message.guild.get_member(int(emb.footer.text))
                
                if not member:
                    #member not found in server; probably left
                    return

                rolename = emb.description[emb.description.find("Name: ")+7:-1]

                print(f"Adding {rolename} ({color}) to {member.display_name}")
                

                #check if user already has custom role
                if len(member.roles)>1:
                    #edit current role
                    await member.roles[1].edit(name=rolename, color=color)
                else:
                    new_role = await mainserver.create_role(name=rolename, color=color)
                    await member.add_roles(new_role)
                await message.delete()

            elif reaction.emoji == '❌':
                #decline
                await message.delete()
                
######## ADMIN ########

@bot.command()
@commands.is_owner()
async def purge(ctx, amount: typing.Optional[int] = 100):
    if amount:
        amount += 1 #account for new message from command call

    deleted = await ctx.channel.purge(limit=amount)
    print('Purged {0} messages'.format(len(deleted)))

@bot.command()
async def show_mem(ctx):
    await _send(ctx, ctx.guild.members)

######## SERVER/META ########
@bot.command(aliases=['rolerequest','request','rr'])
@util.checks._is_channel(config['rolechan'])
async def role(ctx, *args):

    if len(args)<2:
        raise commands.errors.BadArgument
    
    argstr = ' '.join(args)

    try:
        color = await _parse_to_hex(argstr[0:argstr.find(',')])
    except ValueError:
        raise commands.errors.BadColorArgument

    rolename = argstr[argstr.find(',')+2:]

    if len(rolename)<1:
        raise commands.errors.BadArgument
    
    if config.getboolean('requireconfirm'):
        #await ctx.send(f"Color: {color} Role Name: {argstr[argstr.find(',')+2:]}")
        reqdesc = 'Color: `{0}`\nName: `{1}`'.format(hex(color),rolename)
        reqemb = discord.Embed(title=f"Role request from {ctx.author.display_name}", description=reqdesc, color=color)
        reqemb.set_footer(text=ctx.author.id)
        reqemb.set_thumbnail(url=ctx.author.avatar_url)
        
        sentemb = await _send(ctx.guild.get_channel(int(config['confirmchan'])), embed=reqemb)
        await sentemb.add_reaction('❌')
        await sentemb.add_reaction('✅')
    else:
        #check if user already has custom role
        member = ctx.author
        if len(member.roles)>1:
            #edit current role
            await member.roles[1].edit(name=rolename, color=color)
            await ctx.send(None, embed=discord.Embed(description=f"Role edited to {rolename} successfully ✅"))
        else:
            new_role = await ctx.guild.create_role(name=rolename, color=color)
            await member.add_roles(new_role)
            await ctx.send(None, embed=discord.Embed(description=f"Role {rolename} created successfully ✅"))



@role.error
async def role_error(ctx, error):
    if isinstance(error, commands.errors.BadArgument):
        await _send(ctx, embed=await _err_embed('Usage: {0}role [color], [name]'.format(PREFIX), '{0}role #ff1493, Cool Guy'.format(PREFIX)))
    elif isinstance(error, commands.errors.BadColorArgument):
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
    return int(c.hex_l[1:], 16)

bot.run(os.getenv('TOKEN'))

