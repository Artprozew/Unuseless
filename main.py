import os
import sys
import keep_alive
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

logging.basicConfig(level=logging.WARNING)

'''image = b' '
#image = base64.b64decode(image)
with open('pato.jpeg', 'wb') as file:
    file.write(base64.decodebytes(image))'''


bot_token = os.environ['bot_token']
#webhook_url = os.environ['webhook_url']

#botprefix = '='
#client = discord.Client()
intents = discord.Intents.default()
intents.reactions = True

bot = commands.Bot(command_prefix='>', intents=intents)

current_channel = 830907484419784784
bot.uptime = None
mychannels = [693944449084162169, 830907484419784784]

#bot.commands
#sum_command = commands.Bot.get_command(bot, 'sum')
#sum_aliases = sum_command.aliases

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


async def send_message_to_channel(message, channel):
    channel = bot.get_channel(int(channel)) 
    msg = await channel.send(f'{message}')
    return msg


async def changeusername(username):
    await bot.user.edit(username=username)


async def changenickname(guild, name):
    await guild.get_member(bot.user.id).edit(nick=name)


async def eval_message(channel, args):
    try:
        await channel.send(f'(CLI) Eval result: {eval(args)}')
    except Exception as exc:
        print(exc)


async def send_hook(channel, message):
    try:
        channel = bot.get_channel(int(channel))
        hook = discord.utils.get(await channel.webhooks(), name='NQN-1')
        if not hook:
            hook = discord.utils.get(await channel.webhooks(), name='Unuseless')
            if not hook:
                hook = await channel.create_webhook(name='Unuseless')
        member = await bot.get_guild(channel.guild.id).fetch_member(bot.appinfo.owner.id)
        message = await hook.send(content=message, username=member.display_name, avatar_url=member.avatar_url)
    except Exception as exc:
        traceback.print_exc()


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
        if userinput.startswith(bot.command_prefix):
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
                    '''elif command == '>evalmessage':
                    userinput2 = input('Eval with message to current channel>>> ')
                    asyncio.run_coroutine_threadsafe(eval_message(channel, userinput2), bot.loop)'''
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
                        emoji.append(f':regional_indicator_{char}:')
                    emoji = ''.join(emoji)
                    userinput = userinput.replace(f'_:{i}:', emoji)
            
            asyncio.run_coroutine_threadsafe(send_hook(current_channel, userinput), bot.loop)
            #653491049771040781 # id da guild
            #data = {'content': userinput}
            #hook = requests.post(webhook_url, json=data)


async def replace_emoji_id_by_name(message):
    tmp = re.findall('(<\w*(:\w+:)\d+>)', message)
    if tmp:
        for i in tmp:
            message = message.replace(i[0], i[1])
    return message


async def replace_username_id_by_name(message):
    tmp = re.findall('(<@!?(\d+)>)', message)
    if tmp:
        for i in tmp:
            member = await bot.fetch_user(i[1])
            if member:
                if member.id == bot.appinfo.owner.id:
                    message = f'{colors.FAIL}{message}{colors.ENDC}'
                    message = message.replace(i[0], f'{colors.OKBLUE}@{member}{colors.FAIL}')
                else:
                    message = message.replace(i[0], f'{colors.OKBLUE}@{member}{colors.ENDC}')
    return message


def remove_formattation(formatted_string):
    try:
        formatted_string = re.sub('^(```[a-zA-Z]*)', '', formatted_string)
        formatted_string = re.sub('(```)$', '', formatted_string)
        formatted_string = re.sub('^(`)', '', formatted_string)
        formatted_string = re.sub('(`)$', '', formatted_string)
    except Exception as e:
        print(e)
    return formatted_string


'''class ErrorCog(commands.cog, name='Error'):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        error = getattr(error, 'original', error)

        if isinstance(error, commands.CommandNotFound):
            print(error)
            return await ctx.reply('Não conheço esse comando')
        
        elif isinstance(error, commands.CommandOnCooldown):
            if ctx.author.id == self.bot.appinfo.owner.id:
                ctx.command.reset_cooldown(ctx)
                return await ctx.command.reinvoke(ctx)
            return await ctx.reply('O comando está em cooldown')
        
        elif isinstance(error, commands.BotMissingPermissions):
            permissions = '\n'.join([f'{permission}' for permission in error.missing_perms])
            ctx.reply(f'Eu não consegui fazer o que foi pedido pois não tenho permissão para: {permissions}')'''


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
async def on_ready():
    print(colors.HEADER)
    print('-------------------------------------------------------------')
    print('Conexão bem-sucedida com o Discord')
    print(f'Nome do bot: {bot.user} ID: {bot.user.id}')
    print(ShowTime())
    print('-------------------------------------------------------------')
    print(colors.ENDC)
    #bot.add_cog(ErrorCog(bot))
    '''with open('pato.jpeg', 'rb') as file:
        image = file.read()
        await bot.user.edit(avatar=image)'''
    #await bot.user.edit(avatar_url=bot.appinfo.owner.avatar_url)
    #sys.excepthook = await asyncio.run(traceback_handling())
    bot.remove_command('help')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name='comandos com " > " | >help'))
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
            msg = await replace_emoji_id_by_name(message.content)
            msg = await replace_username_id_by_name(msg)
            print( f'{colors.FAIL}Ping de {message.author.name} em {message.guild.name}\n[#{message.channel.name}] {message.author}: {msg}{colors.ENDC}')

    if message.channel.id == current_channel or message.channel.id in mychannels:
        msg = await replace_emoji_id_by_name(message.content)
        msg = await replace_username_id_by_name(msg)

        if message.reference:
            try:
                msg_reply = await bot.get_channel(message.channel.id).fetch_message(message.reference.message_id)
                msg_author = msg_reply.author.name
                msg_reply = await replace_emoji_id_by_name(msg_reply.content)
                msg_reply = await replace_username_id_by_name(msg_reply)
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


#@commands.command_name.error()
@bot.event
async def on_command_error(ctx, error):
    #await ctx.message.delete()
    if isinstance(error, commands.CommandOnCooldown):
        if ctx.author.id == bot.appinfo.owner.id:
            ctx.command.reset_cooldown(ctx)
            return await ctx.command.reinvoke(ctx)
        return await ctx.reply(f'O comando tá em cooldown!\nPera {error.retry_after:.0f} segundos aí blz')

    elif isinstance(error, commands.MaxConcurrencyReached):
        return await ctx.reply('Já tão usano esse comando!')

    elif isinstance(error, commands.BotMissingPermissions):
        permissions = '\n'.join([f'{permission}' for permission in error.missing_perms])
        return await ctx.reply(f'Eu não consegui fazer o que foi pedido pois não tenho permissão para: {permissions}')
    
    elif isinstance(error, commands.TooManyArguments):
        return await ctx.reply('Argumentos inválidos')

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
        return# await ctx.reply('Eu não conheço esse comando')
    else:
        print(error)
        print('Erro desconhecido')
        traceback.print_exc()


@bot.command()
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
                
            '''if command.parents:
                if command.parents[0] == command:
                    print(command.parents[0], 'PAAAAAAAARENT')'''
                
            #print(dir(command))
        await ctx.reply(embed=embed)
    elif cmd in (cmds:={command.name: command for command in bot.commands}):
        embed = discord.Embed(title=f'Comando: {cmd}', description=cmds[cmd].help, timestamp=datetime.datetime.utcnow())
        await ctx.reply(embed=embed)
        #await ctx.reply('cmd: ' + cmds[cmd].help)
    else:
        await ctx.reply('Comando não encontrado')


@bot.command()
async def corrida(ctx, *racers):
    if racers:
        users = list(racers)
        users = ' '.join(users)
        users = users.split(', ')
        if len(users) <= 1:
            await ctx.reply(f'{users[0]} não pode correr sozinho')
            return
    race = True
    participants = []
    await ctx.channel.send('INICIANDO A CORRIDA!!!! 🚦')
    await asyncio.sleep(3)
    await ctx.channel.send('3')
    await asyncio.sleep(1)
    await ctx.channel.send('2')
    await asyncio.sleep(1)
    await ctx.channel.send('1')
    await asyncio.sleep(1)
    await ctx.channel.send('VAAAAAI!!!!')
    if users:
        await asyncio.sleep(5)
        await ctx.channel.send('Corrida finalizada! 🏁')
        winners2 = []
        for user in users:
            winners2.append(user)
        random.shuffle(winners2)
        winners = ''
        for index, value in enumerate(winners2):
            index += 1
            if index == 1:
                winners += f'Primeiro 🥇: {winners2[0]}\n'
            elif index == 2:
                winners += f'Segundo 🥈: {winners2[1]}\n'
            elif index == 3:
                winners += f'Terceiro 🥉: {winners2[2]}\n'
            else:
                winners += f'{index}º: {value}\n'
        await ctx.channel.send(f'Ganhadores:\n{winners}')
    else:
        def check(message):
            return ':run:' in message.content and message.channel == ctx.channel #a:run:847637360979083324
        try:
            timer = time.time() - 19
            while race:
                timer2 = time.time()
                if timer2 == timer:
                    race = False
                    break
                message = await bot.wait_for('message', check=check, timeout=10.0)
                if not message.author.mention in participants and not message.author.discriminator == '0000':
                    participants.append(message.author.mention)
            if participants:
                winners = random.shuffle(participants)
                winners2 = ''
                for index, value in enumerate(participants):
                    index += 1
                    if index == 1:
                        winners2 += f'Primeiro 🥇: {value}\n'
                    elif index == 2:
                        winners2 += f'Segundo 🥈: {value}\n'
                    elif index == 3:
                        winners2 += f'Terceiro 🥉: {value}\n'
                    else:
                        winners2 += f'{index}º: {value}\n'
                await ctx.channel.send(f'Ganhadores:\n{winners2}')
        except asyncio.TimeoutError:
            if not participants:
                await ctx.channel.send('Ninguém participou da corrida')
            if participants:
                winners = random.shuffle(participants)
                winners2 = ''
                for index, value in enumerate(participants):
                    index += 1
                    if index == 1:
                        winners2 += f'Primeiro 🥇: {value}\n'
                    elif index == 2:
                        winners2 += f'Segundo 🥈: {value}\n'
                    elif index == 3:
                        winners2 += f'Terceiro 🥉: {value}\n'
                    else:
                        winners2 += f'{index}º: {value}\n'
                await ctx.channel.send(f'Ganhadores:\n{winners2}')


@bot.command()
@commands.is_owner()
async def evaluate(ctx, *args, awaitfirst=False):
    print('started')
    try:
        execargs = ''
        for arg in args:
            if arg == '--awaitfirst=true' or arg == '--awaitfirst=True' or arg.startswith('await'):
                awaitfirst = True
                continue
            execargs = execargs + ' ' + arg
        while execargs.startswith(' '):
            execargs = execargs[1:]
        print(execargs)
        execargs = remove_formattation(execargs)
    except Exception as e:
        print(e)
    try:
        if awaitfirst:
            print('here')
            await ctx.reply(await eval(execargs))
            print('here')
        else:
            print('doing')
            await ctx.reply(eval(f'{execargs}'))
            print('doing')
    except Exception as exc:
        exc_type, exc_value, exc_tb = sys.exc_info()
        #exc = traceback.format_exc(chain=False)
        if exc_type.__name__ == 'HTTPException':
            await ctx.reply(f'Returned an empty string (`{exc_value}`)')
        else:
            exc = traceback.format_exception_only(exc_type, exc_value)
            exc = ' '.join(exc)
            if '```' in exc:
                exc = exc.replace('```', '')
            await ctx.reply(f'Exception: ```py\n{exc}```')#```py' + exc_formatted + '```')


@bot.command()
@commands.is_owner()
async def execute(ctx, *args):
    print(args)
    try:
        execargs = ''
        for arg in args:
            execargs = execargs + ' ' + arg
        while execargs.startswith(' '):
            execargs = execargs[1:]
        execargs = remove_formattation(execargs)
    except Exception as e:
        print(e)
    try:
        result = StringIO()
        with redirect_stdout(result), redirect_stderr(result):
            exec(f'async def __ex(ctx): ' + ''.join(f'\n {l}' for l in execargs.split('\n')))
            await locals()['__ex'](ctx)
        result = result.getvalue()
        if result:
            await ctx.reply(f'Resultado: ```py\n{result}```')
        else:
            await ctx.message.add_reaction('🚫')
    except Exception as exc:
        exc_type, exc_value, exc_tb = sys.exc_info()
        idk = traceback.format_exc()
        print(idk)
        if not exc_type and not exc_value:
            await ctx.message.add_reaction('🚫')
        else:
            exc = traceback.format_exception_only(exc_type, exc_value)
            exc = ' '.join(exc)
            if '```' in exc:
                exc = exc.replace('```', '')
            await ctx.reply(f'Exception: ```py\n{exc}```')


@bot.command(
    help='Mostra se o bot está funcionando e qual seu tempo de resposta'
)
async def ping(ctx):
    pingtime = time.perf_counter()
    message = await ctx.reply('Pong! 🏓')
    ping = (time.perf_counter() - pingtime) * 1000
    embed = discord.Embed()
    embed.add_field(name='Latência do bot', value=f'{int(bot.latency * 1000)} ms', inline=True)
    embed.add_field(name='Tempo de resposta', value=f'{int(ping)} ms', inline=True)
    await message.edit(embed=embed)
    #await message.edit(content=f'Pong! 🏓\nBot latency: {int(bot.latency * 1000)}ms\nResponse time: {int(ping)}ms')


@bot.command(
    help='Envia uma mensagem para um canal. --silent=True para deletar o comando enviado'
)
@commands.cooldown(1, 10, commands.BucketType.user)
async def say(ctx, channel: Optional[discord.TextChannel]=None, *message, silent=False):
    saymessage = ''
    for arg in message:
        if arg == '--silent=true' or arg == '--silent=True':
            silent = True
            continue
        saymessage = saymessage + ' ' + arg
    if channel is None:
        await ctx.reply(saymessage)
    else:
        await channel.send(saymessage)
    if silent:
        await ctx.message.delete()


@bot.command()
async def codificar(ctx, *base_64, attachment: Optional=None, image: Optional[bool]=False):
    if base_64:
        message = ''
        for arg in base_64:
            if '--image=true' in arg or '--image=True' in arg:
                image = True
                print('true')
                continue
            message = message + ' ' + arg
        base_64 = message
        base_64 = remove_formattation(base_64)
    if ctx.message.attachments:
        attachment_url = ctx.message.attachments[0].url
        file_request = requests.get(attachment_url)
        base_64 = file_request.content
    '''tmp = re.search('^\w+:\w+/(\w+);base64,', base_64)
    print('hee')
    if tmp:
        print(base_64)
        base_64 = base_64.replace(tmp.group(), '')
        image = True
        #print(file_request.content)'''
    try:
        if image:
            print('try')
            try:
                print('encod')
                print('encod')
                encoded = base64.encodebytes(base_64)
                print('encod')
            except Exception as e:
                traceback.print_exc()
                print('hereeer')
        else:
            base_64 = base_64.encode()
            encoded = base64.b64encode(base_64)
        encoded = encoded.decode()
    except Exception as e:
        traceback.print_exc()
    try:
        await ctx.reply(f'Base64 codificado: ```\n{encoded}```')
    except discord.errors.HTTPException:
        with open(f'{ctx.author.id}.txt', 'w') as file:
            file.write(encoded)
        file = discord.File(f'{ctx.author.id}.txt')
        await ctx.reply('Base64 codificado: ', file=file)
        os.remove(f'{ctx.author.id}.txt')


@bot.command()
async def decodificar(ctx, *base_64: Optional[str], attachment: Optional=None, image: Optional=False):
    print('start')
    #image = True
    if base_64:
        for arg in base_64:
            message = ''
            if '--image=True' in base_64 or '--image=true' in base_64:
                print('true')
                image = True
                continue
            message = message + ' ' + arg
        base_64 = message
        base_64 = remove_formattation(base_64)
            
    if ctx.message.attachments:
        attachment_url = ctx.message.attachments[0].url
        file_request = requests.get(attachment_url)
        base_64 = file_request.content
        print('hee')
        '''tmp = re.search('^(\w+:\w+/(\w+);base64,)', base_64)
        print('hee')
        if tmp:
            base_64 = base_64.replace(tmp.group(1), '')
            image = True
            print('true')'''
    print('if imfg')
    if image:
        print('try')
        try:
            decoded = base64.decodebytes(base_64)
        except Exception:
            traceback.print_exc()
            await ctx.reply('Não identificado como uma imagem em bytes codificado em Base64')
            return
        '''if tmp.group(2) == 'jpeg' or tmp.group(2) == 'jpg':
            openwith = 'jpeg'
        elif tmp.group(2) == 'png':
            openwith = 'png'
        elif tmp.group(2) == 'bmp':
            openwith = 'bmp'
        else:'''
        openwith = 'jpeg'
        print('aaa')
        with open(f'{ctx.author.id}.{openwith}', 'wb') as file:
            file.write(decoded)
        file = discord.File(f'{ctx.author.id}.{openwith}')
        await ctx.reply('Imagem decodificada em Base64: ', file=file)
        os.remove(f'{ctx.author.id}.{openwith}')
        return
    try:
        decoded = base64.b64decode(base_64)
        decoded = decoded.decode()
    except Exception:
        traceback.print_exc()
        await ctx.reply('Não identificado como código em Base64')
        return
    try:
        await ctx.reply(f'Base64 decodificado: ```\n{decoded}```')
    except discord.errors.HTTPException:
        with open(f'{ctx.author.id}.txt', 'w') as file:
            file.write(decoded)
        file = discord.File(f'{ctx.author.id}.txt')
        await ctx.reply('Base64 decodificado: ', file=file)
        os.remove(f'{ctx.author.id}.txt')


@bot.command()
async def textlength(ctx, *text: Optional[str], attachment: Optional[discord.Attachment]=None):
    if text:
        args = ''
        for arg in text:
            args = args + ' ' + arg
        args = remove_formattation(args)
        args = replace_emoji_id_by_name(args)
    if ctx.message.attachments:
        attachment_url = ctx.message.attachments[0].url
        file_request = requests.get(attachment_url)
        args = file_request.content
        args = args.decode()
    while args.startswith(' '):
        args = args[1:]
    length = len(args)
    if length == 1:
        await ctx.reply(f'Isso é apenas {length} caracter')
    else:
        await ctx.reply(f'Essa frase têm {length} caracteres')


@bot.command()
async def calcular(ctx, *args):
    message = ''
    for arg in args:
        message = message + ' ' + arg
    print(message)
    tmp = re.search('\((.+)\)', message)
    numberslist = []
    operator = [None]
    operant = []
    if tmp:
        print('found')
        numberslist = tmp.group(1).split(',')
        print('kk')
        for i in range(len(numberslist)):
            try:
                print(numberslist[i])
                if isinstance(numberslist[i], float):
                    numberslist[i] = float(numberslist[i])
                elif isinstance(numberslist[i], int):
                    numberslist[i] = int(numberslist[i])
            except ValueError:
                await ctx.reply(f'Eu ainda não conheço esse tipo de operação com {numberslist[i]}!')
        print('final')
        message = message.replace(tmp.group(), '')
    print('aca')
    print(message)
    '''for item in lst:
        if len(item) &gt; 1 and not item.isdigit():
        return False
    return True'''
    message = message.split(' ')
    splitted = ''
    message2 = []
    for index, value in enumerate(message):
        if value == '' or value == ' ':
            continue
        if '**' in value or '^' in value:
            operator.append('**')
            splitted = value.split('**')
            splitted = ' ** '.join(splitted)
            value = splitted
        if 'x' in value or '*' in value:
            operator.append('*')
            splitted = value.split('*')
            splitted = ' * '.join(splitted)
            value = splitted
        if '/' in value:
            operator.append('/')
            splitted = value.split('/')
            splitted = ' / '.join(splitted)
            value = splitted
        if '+' in value:
            operator.append('+')
            splitted = value.split('+')
            splitted = ' + '.join(splitted)
            value = splitted
        if '-' in value:
            #if not re.search('(?:\*\*|\^|\*|x|\+|-|/)\s*-', value):
            operator.append('-')
            splitted = value.split('-')
            splitted = ' - '.join(splitted)
            value = splitted
        if value.isnumeric():
            operant.append(int(value))
        if re.search('^\d+\.?\d*$', value):
            operant.append(float(value))
        #message = splitted
        for i in value.split():
            message2.append(i)
        print(message)
        print(value)
        print(splitted, 'splitted')
    print('k')
    print(message2)
    '''operant = []
    message = ' '.join(message)
    message = message.split(' ')
    for i in message:
        print(i)
        if i.isnumeric():
            operant.append(int(i))
        elif re.search('^\d+\.?\d*$', i):
            operant.append(float(i))'''
    print(message)
    print(operator, operant)
    operator = [None]
    operant = []
    for index, value in enumerate(message2):
        print(value)
        if value == '' or value == ' ' or not value:
            continue
        if value == '*' or value == 'x':
            operator.append('*')
        elif value == '/':
            operator.append('/')
        elif value == '+':
            operator.append('+')
        elif value == '-':
            operator.append('-')
        elif value == '**' or value == '^':
            operator.append('**')
        elif value.isnumeric():
            operant.append(int(value))
        elif re.search('^\d+\.?\d*$', value):
            operant.append(float(value))
        else:
            tmp = re.search('^(?:(\*\*|\^|\*|x|\+|-|/))(\d+.?\d*)$', value)
            if tmp:
                message2.insert(index + 1, tmp.group(2))
                message2.insert(index + 1, tmp.group(1))
            else:
                tmp = re.search('^(\d+.?\d*)(?:(\*\*|\^|\*|x|\+|-|/))$')
                if tmp:
                    message2.insert(index + 1, tmp.group(2))
                    message2.insert(index + 1, tmp.group(1))
                else:
                    tmp = re.search('^(\d+.?\d*)(?:(\*\*|\^|\*|x|\+|-|/))(\d+.?\d*)$')
                    if tmp:
                        message2.insert(index + 1, tmp.group(3))
                        message2.insert(index + 1, tmp.group(2))
                        message2.insert(index + 1, tmp.group(1))
                    else:
                        await ctx.reply(f'Eu ainda não conheço esse tipo de operação com {value}!')
                        return
    print(operant, operator)
    print(numberslist)
    if len(operator) <= 1:
        await ctx.reply('Você deve especificar um operador aritmético!')
        return
    storedoperator = None
    if numberslist:
        if len(operator) > 2:
            storedoperator = operator[1]
            del operator[1] # delete to ignore the first operator (because it will be used with the numberlist later)
    print(operant, operator)
    result = 0
    for index, value in enumerate(operant):
        if index == 0:
            if len(operant) <= index + 1:
                result = operant[index]
                break
            else:
                continue
        else:
            if isinstance(value, list):
                await ctx.reply('Listas numéricas devem ser escritas antes de qualquer operador')
                return
        if isinstance(operant[index-1], list):
            if len(operant) <= index + 1:
                result = operant[index]
            else:
                continue
        if index == len(operator):
            break
        print('aca')
        print(operant[index-1], operator[index], operant[index])
        if operator[index] == '*':
            result = operant[index-1] * operant[index]
        elif operator[index] == '/':
            result = operant[index-1] / operant[index]
        elif operator[index] == '+':
            result = operant[index-1] + operant[index]
        elif operator[index] == '-':
            result = operant[index-1] - operant[index]
        elif operator[index] == '**':
            result = operant[index-1] ** operant[index]
        operant[index] = result
    numbersresult = []
    print('veei')
    print(result)
    print('que')
    try:
        if storedoperator:
            operator[1] = storedoperator
            print(operator[1])
    except:
        traceback.print_exc()
    try:
        print('fim')
        if numberslist:
            print('yes')
            if re.search('\d+\.?\d*', str(result)):
                result_isfloat = True
            else:
                result_isfloat = False
            for index, value in enumerate(numberslist):
                print(index, value)
                if result_isfloat:
                    numberslist[index] = float(numberslist[index])
                    print(numberslist)
                    if operator[1] == '*':
                        numbersresult.append(numberslist[index] * result)
                    elif operator[1] == '/':
                        numbersresult.append(numberslist[index] / result)
                    elif operator[1] == '+':
                        numbersresult.append(numberslist[index] + result)
                    elif operator[1] == '-':
                        numbersresult.append(numberslist[index] - result)
                    elif operator[1] == '**':
                        numbersresult.append(numberslist[index] ** result)
            print('aqui')
            print(numbersresult)
            print('vache')
            print('antes')
            for index, value in enumerate(numbersresult):
                print(index, value)
                numbersresult[index] = float(numbersresult[index])
                numbersresult[index] = str(round(numbersresult[index], 2))
            numbersresult = ', '.join(numbersresult)
            result = f'({numbersresult}) {operator[1]} {result}'
            print('aaa')
            print(result)
    except:
        traceback.print_exc()
    try:
        print('aooooo')
        print('result:', result)
        await ctx.reply(f'Resultado: {result}')
    except discord.errors.HTTPException:
        try:
            with open(f'{ctx.author.id}.txt', 'w') as file:
                file.write(str(result))
            file = discord.File(f'{ctx.author.id}.txt')
            await ctx.reply('Resultado: ', file=file)
            os.remove(f'{ctx.author.id}.txt')
        except: traceback.print_exc()


@bot.command()
@commands.is_owner()
async def teste(ctx):
    await ctx.reply('teste')


@bot.command()
@commands.is_owner()
async def leave_current_guild(ctx):
    await ctx.reply('Saindo do servidor... :(')
    guild = bot.get_guild(int(ctx.guild.id))
    await guild.leave()


@bot.command()
@commands.is_owner()
async def change_username(ctx, *name):
    username = ''
    for arg in name:
        username = username + ' ' + arg
    if len(username) >= 32:
        await ctx.reply('O nome não pode ter mais de 32 caracteres')
    else:
        try:
            await bot.user.edit(username=username)
            await ctx.reply('Novo nome: ' + username)
        except Exception as exc:
            await ctx.reply(exc)


@bot.command()
async def info(ctx):
    guild_count = 0
    member_count = 0
    for guild in bot.guilds:
        guild_count += 1
        member_count += int(guild.member_count)
    end = time.time()
    #e = int(time.time() - start_time)
    #print('{:02d}:{:02d}:{:02d}'.format(e // 3600, (e % 3600 // 60), e % 60))
    #elapsed_time = time.time() - start_time
    #time.strftime('%H:%M:%S', time.gmtime(elapsed_time))
    hours, rem = divmod(end-bot.uptime, 3600)
    minutes, seconds = divmod(rem, 60)
    elapsed = '{:0>2}:{:0>2}:{:05.2f}'.format(int(hours), int(minutes), seconds)
    embed = discord.Embed(Title='Info', description='Informações do bot')
    embed.add_field(name='Link de convite', value='[Convite do bot](https://discord.com/api/oauth2/authorize?client_id=843698163785269298&permissions=4228381815&scope=bot)', inline=True)
    embed.add_field(name='API', value='Discord.py', inline=True)
    embed.add_field(name='Desenvolvedor', value=bot.appinfo.owner.mention, inline=True)
    embed.add_field(name='Tempo online', value=elapsed, inline=True)
    embed.add_field(name='Servidores', value=guild_count, inline=True)
    embed.add_field(name='Usuários', value=member_count, inline=True)
    #embed.set_footer(name='test')
    await ctx.reply(embed=embed)
    #await message.edit(embed=embed, content='')


'''@bot.command()
async def exec(ctx, *args):
    if ctx.author == bot.appinfo.owner:
        execargs = ''
        for arg in args:
            execargs = execargs + ' ' + arg
        await exec(execargs)'''


def randomstars(length):
    star = ['.', '。', '•']
    caracters = ''
    for i in range(length * 10):
        caracter = ''
        percentage = random.randint(0, 100)
        if percentage <= 95: # percentage to get space instead of star
            caracter = ' '
        else:
            numb = random.randint(0, 2)
            caracter = star[numb]
        caracters += caracter
    return caracters
            

async def ejectmsg2(msg, mymsg, currmsg):
    stars = [None]
    length = len(mymsg)
    for i in range(1, 8):
        stars.append(randomstars(length))
    leftstars = list()
    rightstars = list()
    leftstars.append(stars[4][0:(int(len(stars[4]) / 2))])
    rightstars.append(stars[4][(int(len(stars[4]) / 2)):-1])
    leftstars.append(stars[5][0:(int(len(stars[5]) / 2))])
    rightstars.append(stars[5][(int(len(stars[5]) / 2)):-1])
    sendedmsg = ''
    mymsg2 = str(random.randint(1, 3)) + ' Impostor remains'
    length2 = int(length * 2)
    length3 = length2
    print(f'{mymsg!r}')
    for caracter in mymsg:
        currmsg += caracter
        length2 -= 1
        if caracter == '\\':
            continue
        elif caracter == ' ':
            continue
        else:
            sendedmsg = sendedmsg.format('{}\n{}\n{}\n')
            #sendedmsg = f'{stars[1]}\n{stars[2]}\n{stars[3]}\n{leftstars[0]:<{length2}}{currmsg:^{length2}}{rightstars[0]:>{length2}}\n{leftstars[1]:<{length3}}{" ":^{length3}}{rightstars[1]:>{length3}}\n{stars[6]}\n{stars[7]}'
            print(sendedmsg)
            #msg = msg
            #print('1kkk')
            await msg.edit(content=sendedmsg)
            #print('2kkk')
            await asyncio.sleep(0.7)
        
    sendedmsg = sendedmsg.split('\n')
    del sendedmsg[4]
    del sendedmsg[4]
    del sendedmsg[4]
    sendedmsg = '\n'.join(sendedmsg)
    currmsg = ''
    length2 = length3
    for caracter in mymsg2:
        currmsg += caracter
        length2 -= 1
        if caracter == ' ':
            continue
        else:
            await msg.edit(content=sendedmsg + f'\n{leftstars[1]:<{length2}}{currmsg:^{length2}}{rightstars[1]:>{length2}}\n{stars[6]}\n{stars[7]}')
            await asyncio.sleep(0.7)


async def ejectmsg(msg, mymsg, currmsg):
    sendedmsg = ''
    for caracter in mymsg:
        currmsg += caracter
        if caracter == '\\':
            continue
        elif caracter == ' ':
            continue
        else:
            sendedmsg = '. 　　　。　　　　•　 　ﾟ　　。 　　.              。\n \
　　　.　　　 　　.　　　　　。　　 。　. 　       .          •      。\n \
.　　 。　　　　　 ඞ 。 . 　　 • 　　  . 　•                。\n \
　　ﾟ　　  {:^20}\n \
　　　　　      {:^20} 　 　　 \n \
 　　ﾟ　　　.　　  •　. 　　　　.　 .           •   。         .        。'.format(currmsg, ' ')
            await msg.edit(content=sendedmsg)
            await asyncio.sleep(0.7)
        
    mymsg = str(random.randint(1, 3)) + ' Impostor remains'
    sendedmsg = sendedmsg.split('\n')
    del sendedmsg[4]
    del sendedmsg[4]
    sendedmsg = '\n'.join(sendedmsg)
    currmsg = ''
    for caracter in mymsg:
        currmsg += caracter
        if caracter == ' ':
            continue
        else:
            await msg.edit(content=sendedmsg + '\n　　　　　        {:20} 　 　　 \n \
 　　ﾟ　　　.　　  •　. 　　　　.　 .           •   。         .        。'.format(currmsg))
            await asyncio.sleep(0.7)


@bot.command()
@commands.max_concurrency(1, commands.BucketType.guild, wait=False)
async def ejetar(ctx, *args):
    msg = await ctx.channel.send('.')
    mymsg = ''
    for arg in args:
        mymsg = mymsg + ' ' + arg
    mymsg = mymsg + ' was{}an Impostor'.format((random.randint(0, 1) and ' not ' or ' '))
    currmsg = ''

    asyncio.run_coroutine_threadsafe(ejectmsg(msg, mymsg, currmsg), bot.loop)


@bot.command()
@commands.max_concurrency(1, commands.BucketType.guild, wait=False)
async def ejetar2(ctx, *args):
    msg = await ctx.channel.send('.')
    mymsg = ''
    for arg in args:
        mymsg = mymsg + ' ' + arg
    impostor = random.randint(0, 1)
    '''if impostor == 1:
        mymsg = mymsg + ' was an Impostor'
    else:
        mymsg = mymsg + ' was not an Impostor'''
    mymsg = mymsg + ' was an Impostor'#' was{}an Impostor'.format((random.randint(0, 1) and ' not ' or ' '))
    currmsg = ''

    asyncio.run_coroutine_threadsafe(ejectmsg2(msg, mymsg, currmsg), bot.loop)

@bot.command()
async def impostor(ctx, *args):
    msg = await ctx.channel.send('.')
    mymsg = ''
    for arg in args:
        mymsg = mymsg + ' ' + arg
    currmsg = ''
    
    async def impostormsg(msg, mymsg, currmsg):
        for caracter in mymsg:
            if caracter == ' ':
                currmsg += caracter
                continue
            else:
                currmsg += caracter
                await msg.edit(content=currmsg)
                await asyncio.sleep(0.7)

    asyncio.run_coroutine_threadsafe(impostormsg(msg, mymsg, currmsg), bot.loop)


#t = Thread(target=run_tkinter)
k = Thread(target=keep_alive.run)
k.start()
#t.start()

bot.run(bot_token)
#runall()
#run2()



'''@tasks.loop(seconds=0.1)
async def run_tk():
    print('a')
    root.mainloop()
    root.forget()'''

#client.run(bot_token)

'''async def run_tkinter():
    while True:
        root.mainloop()
        await asyncio.sleep(1)
client.loop.create_task(run_tkinter())
client.run(bot_token)'''


'''def run_discord():
    bot.run(bot_token)

def run_tkinter():
    tkint.root.mainloop() # RuntimeError: Calling Tcl from different apartment'''

'''def runall():
    loop = asyncio.get_event_loop()
    loop.create_task(run_discord())
    loop.create_task(asyncio.sleep(1))
    Thread(loop.run_forever())

def run2():
    loop = asyncio.get_event_loop()
    loop.create_task(run_tkinter())
    loop.create_task(asyncio.sleep(1))
    Thread(loop.run_forever())'''

'''def run1():
    loop = asyncio.get_event_loop()
    loop.create_task(run_discord())
    loop.run_forever()

def run2():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop = asyncio.get_event_loop()
    loop.create_task(run_tkinter())
    loop.run_forever()

thread1 = Thread(target=run1)
thread1.start()

thread2 = Thread(target=run2)
thread2.start()'''

'''def runall():
    loop = asyncio.get_event_loop()
    loop.create_task(run_discord())
    loop.create_task(run_tkinter())
    loop.run_forever()


runall()'''