import os
import sys
from discord import Webhook, RequestsWebhookAdapter
from discord.ext import commands
import discord
import requests
import datetime
import pytz
from threading import Thread
import time
import asyncio
import random
import traceback
import re
from typing import Optional
import base64
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
import logging
import keep_alive
from core import utils

Thread(target=keep_alive.run).start()

logging.basicConfig(level=logging.WARNING)

class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


'''image = b' '
#image = base64.b64decode(image)
with open('pato.jpeg', 'wb') as file:
    file.write(base64.decodebytes(image))'''

bot_token = os.environ['bot_token']


intents = discord.Intents.default()
intents.reactions = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or('>'),
    intents=intents,
    activity=discord.Activity(type=discord.ActivityType.listening, name='comandos com " > " | >help')
    )

current_channel = 693944449084162169
bot.uptime = None
mychannels = [693944449084162169, 830907484419784784, 850168576836108320]


async def send_message_to_channel(message, channel):
    channel = bot.get_channel(int(channel)) 
    msg = await channel.send(f'{message}')
    return msg


async def changeusername(username):
    await bot.user.edit(username=username)


async def changenickname(guild, name):
    await guild.get_member(bot.user.id).edit(nick=name)


async def send_hook(channel, message):
    channel = bot.get_channel(int(channel))
    hook = discord.utils.get(await channel.webhooks(), name='NQN-1')
    if not hook or hook.token is None:
        hook = discord.utils.get(await channel.webhooks(), name='NQN-2')
        if not hook or hook.token is None:
            hook = discord.utils.get(await channel.webhooks(), name='Unuseless')
            if not hook or hook.token is None:
                hook = await channel.create_webhook(name='Unuseless')
    member = await bot.get_guild(channel.guild.id).fetch_member(bot.appinfo.owner.id)
    message = await hook.send(content=message, username=member.display_name, avatar_url=member.avatar_url)


async def run_callback(cmd, ctx, *args):
    await cmd.callback(ctx, *args)


async def get_nickname(guild, member):
    return await bot.get_guild(int(guild)).fetch_member(int(member))


async def delete_message(message, delay=0):
    return await message.delete(delay=delay)


async def mainloop():
    global current_channel
    while True:
        userinput = input('')
        channel = bot.get_channel(current_channel)
        if userinput.startswith('>'):
            args = userinput.split()
            command = args[0][1:]
            params = args[1:]
            clean_params = ' '.join(params)
            try:
                if command == 'username':
                    if params:
                        asyncio.run_coroutine_threadsafe(changeusername(clean_params), bot.loop)
                        print(f'New username: {bot.user.name}')
                    else:
                        print(bot.user.name)
                elif command == 'nickname':
                    member = asyncio.run_coroutine_threadsafe(get_nickname(channel.guild.id, bot.user.id), bot.loop).result()
                    if params:
                        guild = await bot.get_guild(channel.guild.id)
                        asyncio.run_coroutine_threadsafe(changenickname(guild, clean_params), bot.loop)
                        print('New guild nickname:', {member.display_name})
                    else:
                        print(member.display_name)
                elif command == 'channel':
                    if params:
                        print(f'Older channel: #{channel.name} [{channel.id}]')
                        if clean_params == 'geral': clean_params = 693944449084162169
                        if clean_params == 'codigo': clean_params = 830907484419784784
                        current_channel = int(clean_params)
                        channel = bot.get_channel(current_channel)
                        print(f'Newer channel: #{channel.name} [{channel.id}]')
                    else:
                        print(f'Current channel: #{channel.name} [{channel.id}]')
                elif command == 'eval' and params:
                    print(eval(clean_params))
                else:
                    command = discord.utils.get(bot.commands, name=command)
                    if command:
                        asyncio.run_coroutine_threadsafe(send_hook(current_channel, ' '.join(args)), bot.loop)
                        message = asyncio.run_coroutine_threadsafe(send_message_to_channel(' '.join(args), current_channel), bot.loop).result()
                        ctx = await bot.get_context(message)
                        await asyncio.sleep(0.2)
                        asyncio.run_coroutine_threadsafe(run_callback(command, ctx, *params), bot.loop)
                        asyncio.run_coroutine_threadsafe(delete_message(ctx.message, 0.2), bot.loop)
                    else:
                        print('Comando não encontrado')
            except:
                traceback.print_exc()
        else:
            tmp = re.findall(':(\w+):', userinput)
            if tmp:
                for i in tmp:
                    if len(i) == 1:
                        emoji = f':regional_indicator_{i}:'
                        userinput = userinput.replace(f':{i}:', emoji)
                    else:
                        for guild in bot.guilds:
                            emoji = discord.utils.get(guild.emojis, name=i)
                            if emoji:
                                userinput = userinput.replace(f':{i}:', str(emoji))
                                break
            tmp2 = re.findall('_:([^:]+):', userinput)
            if tmp2:
                for i in tmp2:
                    emoji = []
                    for char in i:
                        if char == '?':
                            emoji.append(':grey_question:')
                            continue
                        elif char == '!':
                            emoji.append(':grey_exclamation:')
                            continue
                        if char == ' ':
                            emoji.append(' ')
                            continue
                        emoji.append(f':regional_indicator_{char.lower()}:')
                    emoji = ''.join(emoji)
                    userinput = userinput.replace(f'_:{i}:', emoji)
            
            asyncio.run_coroutine_threadsafe(send_hook(current_channel, userinput), bot.loop)
            #653491049771040781 # id da guild
            #data = {'content': userinput}
            #hook = requests.post(webhook_url, json=data)


def Alarme(): return True

def ShowTime():
    tz = pytz.timezone('Brazil/East')
    timeanddate = datetime.datetime.now(tz)
    daynumber = timeanddate.weekday()
    dayname = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
    searchall = re.search('(\d+)-(\d+)-(\d+)\s+(\d+):(\d+):(\d+)\.\d+', str(timeanddate))
    if searchall:
        year = searchall.group(1)
        month = searchall.group(2)
        day = searchall.group(3)
        hour = searchall.group(4)
        minute = searchall.group(5)
        second = searchall.group(6)
        dayofweek = dayname[daynumber]
        if not daynumber == 5 and not daynumber == 6:
            dayofweek = '{}-Feira'.format(dayofweek)
        stringtime = 'Data: {}/{}/{}, {}\nHora: {}:{}:{}'.format(day, month, year, dayofweek, hour, minute, second)
        if int(hour) > 5 and int(hour) < 8 and Alarme:
            print(colors.WARNING + 'VAI DORMIR\nVAI DORMIR\nVAI DORMIR\t\tVAI DORMIR\nVAI DORMIR\t\tVAI DORMIR\nVAI DORMIR\t\tVAI DORMIR')
        return stringtime


@bot.event
async def on_connect():
    if not hasattr(bot, 'appinfo'):
        bot.appinfo = await bot.application_info()
    bot.uptime = time.time()


@bot.event
async def on_disconnect():
    end = time.time()
    hours, rem = divmod(end-bot.uptime, 3600)
    minutes, seconds = divmod(rem, 60)
    elapsed = '{:0>2}:{:0>2}:{:05.2f}'.format(int(hours), int(minutes), seconds)
    await bot.appinfo.owner.send(f'Estou offline! Eu estive online por {elapsed}')
    print(f'Estou offline! Eu estive online por {elapsed}')


@bot.event
async def on_ready():
    print(colors.HEADER)
    print('-------------------------------------------------------------')
    print('Conexão bem-sucedida com o Discord')
    print(f'Nome do bot: {bot.user} ID: {bot.user.id}')
    print(f'Rodando Discord.py {discord.__version__}')
    print(ShowTime())
    print('-------------------------------------------------------------')
    print(colors.ENDC)
    for root, dirs, files in os.walk('core/commands/cogs'):
        dirs[:] = [dir for dir in dirs if not dir == '__pycache__']
        for file in files:
            if file.endswith('.py'):
                try:
                    bot.load_extension(f'{root.replace("/", ".")}.{file[:-3]}')
                except (discord.ClientException, ModuleNotFoundError):
                    print(f'Failed to load extension {file}')
                    traceback.print_exc()
    #bot.load_extension('core.commands.cogs.bot.customhelp')
    #bot.load_extension('core.commands.cogs.owner.owner')
    '''with open('pato.jpeg', 'rb') as file:
        image = file.read()
        await bot.user.edit(avatar=image)'''
    #await bot.user.edit(avatar_url=bot.appinfo.owner.avatar_url)
    #sys.excepthook = await asyncio.run(traceback_handling())
    #bot.remove_command('help')
    #await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='comandos com " > " | >help'))
    Thread(target=asyncio.run, args=(mainloop(), )).start()


@bot.event
async def on_error(event, *args, **kwargs):
    embed = discord.Embed(title=':x: Event Error', colour=0xe74c3c) #Red
    embed.add_field(name='Event', value=event)
    embed.description = '```py\n%s\n```' % traceback.format_exc()
    embed.timestamp = datetime.datetime.utcnow()
    await bot.appinfo.owner.send(embed=embed)
    print('%s' % traceback.format_exc())


@bot.event
async def on_message(message):
    owner_display_name = bot.appinfo.owner.name
    if not isinstance(message.channel, discord.DMChannel):
        owner_display_name = await bot.get_guild(message.channel.guild.id).fetch_member(bot.appinfo.owner.id)
        owner_display_name = owner_display_name.display_name
    '''if message.author == bot.user:
        return'''
    if message.author.discriminator == '0000':
        if not message.author.name == owner_display_name:
            return

    if f'<@!{bot.appinfo.owner.id}>' in message.content or f'<@{bot.appinfo.owner.id}>' in message.content:
        if not message.channel.id == current_channel and not message.channel.id in mychannels:
            msg = await utils.funcs.replace_emoji_id_by_name(message.content)
            msg = await utils.funcs.replace_user_id_by_name(bot, msg)
            print( f'{colors.FAIL}Ping de {message.author.name} em {message.guild.name}\n[#{message.channel.name}] {message.author}: {msg}{colors.ENDC}')

    if message.channel.id == current_channel or message.channel.id in mychannels:
        #msg = await utils.funcs.replace_emoji_id_by_name(message.content)
        msg = await utils.funcs.replace_user_id_by_name(bot, message.content)

        if message.reference:
            try:
                msg_reply = await bot.get_channel(message.channel.id).fetch_message(message.reference.message_id)
                msg_author = msg_reply.author.name
                msg_reply = await utils.funcs.replace_emoji_id_by_name(msg_reply.content)
                msg_reply = await utils.funcs.replace_user_id_by_name(bot, msg_reply)
            except discord.errors.NotFound as exc: # 404 Not Found (error code 10008): Unknown Message ((Message deleted))
                msg_reply = 'A mensagem original foi excluída.'
                msg_author = '✖️ '
            print(f'{colors.HEADER}┌ Reply: {msg_author}: {msg_reply}{colors.ENDC}')

        if message.channel.id in mychannels and not message.channel.id == current_channel:
            print(f'[#{colors.BOLD}{message.channel.name}{colors.ENDC}] {colors.BOLD}{message.author.name}{colors.ENDC}: {msg}')
        elif message.author.name == owner_display_name and message.author.discriminator == '0000':
            print(f'\033[F{colors.BOLD}{bot.appinfo.owner.name}{colors.ENDC}: {msg}')
        else:
            print(f'{colors.BOLD}{message.author.name}{colors.ENDC}: {msg}')
            
        if message.attachments:
            attachments = ''
            for i in message.attachments:
                attachments += i.filename + ' │ '
            print(f'{colors.HEADER}└ Attachment{"s" if len(message.attachments) > 1 else ""}: {attachments}{colors.ENDC}')
                

    #data = {'content': message.content, 'username': message.author.display_name}
    #hook = requests.post(None, json=data)
    #hook = Webhook.from_url(webhook_url, adapter=RequestsWebhookAdapter)
    #await hook.send(content=message.content, username=message.author.display_name, avatar_url=message.author.avatar_url)
    
    if message.content.startswith('gostosa ') or ' gostosa' in message.content or message.content == 'gostosa' or message.attachments and message.attachments[0].filename.startswith('SPOILER_'):
        await message.add_reaction('<:gostosa:840014461590437969>')

    if message.content.startswith('oi ') or ' oi' in message.content or message.content == 'oi':
        await message.add_reaction('<:oi:791124512644136991>')#'<a:peepohi:724060904194441257>')

    await bot.process_commands(message)


@bot.event
async def on_reaction_add(reaction, user):
    '''args = reaction.message.split()
    command = args[0][1:] if args[0].startswith(bot.command_prefix) else None
    params = args[1:] if command else None
    if command:
        cmd = discord.utils.get(bot.commands, name=command)
        if not cmd:
            async for user_react in reaction.users():
                if user_react == bot.user:
                    reaction.remove(user)
                    helpcmd = discord.utils.get(bot.commands, name='ajuda')
                    if helpcmd:
                        await helpcmd.callback(ctx)'''


def make_sequence(seq):
    from collections.abc import Sequence
    if seq is None:
        return ()
    if isinstance(seq, Sequence) and not isinstance(seq, str):
        return seq
    else:
        return (seq,)


def reaction_check(message=None, emoji=None, author=None, ignore_bot=True): # Thanks to Patrick Haugh on StackOverflow for sharing this function
    '''Function to check arguments made mainly to use with the Client.wait_for "check" argument
    
    Usage example:
    check = reaction_check("React with '❔' here", '❔', ctx.message.author)
    reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)'''
    message = make_sequence(message)
    message = tuple(m.id for m in message)
    emoji = make_sequence(emoji)
    author = make_sequence(author)
    def check(reaction, user):
        if ignore_bot and user.bot:
            return False
        if message and reaction.message.id not in message:
            return False
        if emoji and reaction.emoji not in emoji:
            return False
        if author and user not in author:
            return False
        return True
    return check


@bot.event
async def on_command_error(ctx, error):
    if hasattr(ctx.command, 'on_error'): # Ignore commands with local error handlers
        return

    cog = ctx.cog
    if cog:
        if not cog._get_overridden_method(cog.cog_command_error) == None:
            return
        
    error = getattr(error, 'original', error)

    if isinstance(error, commands.CommandOnCooldown):
        if ctx.author.id == bot.appinfo.owner.id:
            ctx.command.reset_cooldown(ctx)
            return await ctx.command.reinvoke(ctx)
        return await ctx.reply(f'O comando tá em cooldown!\nPera {error.retry_after:.0f} segundos aí blz')

    elif isinstance(error, commands.MaxConcurrencyReached):
        return await ctx.reply('Já tão usando esse comando!')

    elif isinstance(error, commands.BotMissingPermissions):
        permissions = '\n'.join([f'{permission}' for permission in error.missing_perms])
        return await ctx.reply(f'Eu não consegui fazer o que foi pedido pois não tenho permissão para:\n{permissions}')
    
    elif isinstance(error, commands.TooManyArguments):
        return await ctx.reply('Argumentos inválidos')

    elif isinstance(error, commands.BadArgument):
        return await ctx.reply('Argumentos inválidos')

    elif isinstance(error, commands.DisabledCommand):
        return await ctx.reply('Esse comando está desativado')

    elif isinstance(error, commands.NoPrivateMessage):
        return await ctx.reply('Esse comando não pode ser usado em DMs')

    elif isinstance(error, commands.CommandNotFound):
        await ctx.message.add_reaction('❔')
        check = reaction_check(ctx.message, '❔', ctx.message.author)
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=5.0, check=check)
            await reaction.remove(bot.user)
            helpcmd = discord.utils.get(bot.commands, name='ajuda')
            if helpcmd:
                await helpcmd.callback(ctx)
            print(reaction, user)
        except asyncio.TimeoutError:
            await ctx.message.remove_reaction('❔', bot.user)
        return

    else:
        print(f'Erro na execução do comando: {ctx.command}')
        traceback.print_exception(type(error), error, error.__traceback__)


'''@bot.command()
async def ajuda(ctx, cmd=None):
    if not cmd:
        embed = discord.Embed(title='Ajuda', description='Comandos do bot', timestamp=datetime.datetime.utcnow())
        cmd_help = []
        for command in bot.walk_commands():
            params = ''
            for index, param in enumerate(command.params):
                if index == 0:
                    continue
                params +=f'{param} '
            #cmd_help.append(f'{command:<20} {params:>20}')
            if not params:
                params = 'Nenhum'
            embed.add_field(name=command, value=params)
                
            if command.parents:
                if command.parents[0] == command:
                    print(command.parents[0], 'PAAAAAAAARENT')
                
            #print(dir(command))
        await ctx.reply(embed=embed)
    elif cmd in (cmds:={command.name: command for command in bot.commands}):
        embed = discord.Embed(title=f'Comando: {cmd}', description=cmds[cmd].help, timestamp=datetime.datetime.utcnow())
        await ctx.reply(embed=embed)
        #await ctx.reply('cmd: ' + cmds[cmd].help)
    else:
        await ctx.reply('Comando não encontrado')'''


bot.run(bot_token)