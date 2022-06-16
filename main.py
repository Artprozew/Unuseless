import os
import datetime
import time
import asyncio
import logging
import traceback

from discord.ext import commands
import discord
import pytz

from core import utils

'''from threading import Thread
import keep_alive
Thread(target=keep_alive.run).start()'''

logging.basicConfig(
    format='[%(asctime)s.%(msecs)03d] (%(name)s.%(funcName)s:%(lineno)d) %(levelname)s: %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S',
    level=logging.INFO
    )
log = logging.getLogger(__name__)
logging.getLogger('discord.http').setLevel(logging.WARNING)
logging.getLogger('discord.gateway').setLevel(logging.WARNING)

bot = commands.Bot(
    owner_id=585965764952195103,
    command_prefix=commands.when_mentioned_or('>'),
    case_insensitive=True,
    intents=discord.Intents.default().all(),
    activity=discord.Activity(type=discord.ActivityType.listening, name='comandos com " > " | >help')
    )
bot._BotBase__cogs = commands.core._CaseInsensitiveDict() # pylint: disable=protected-access


@bot.event
async def on_connect():
    if not hasattr(bot, 'appinfo'):
        bot.appinfo = await bot.application_info()
    bot.uptime = time.time()


@bot.event
async def on_disconnect():
    elapsed = datetime.datetime.now() - datetime.datetime.fromtimestamp(bot.uptime)
    elapsed = str(datetime.timedelta(seconds=elapsed.seconds))
    channel = bot.get_channel(856341000843034686)
    await channel.send(f'Estou offline! Eu estive online por {elapsed}')
    print(f'Estou offline! Eu estive online por {elapsed}')


@bot.event
async def on_ready():
    timeanddate = datetime.datetime.now(pytz.timezone('Brazil/East'))
    #weekday = ['Segunda-Feira', 'Terça-Feira', 'Quarta-Feira', 'Quinta-Feira', 'Sexta-Feira', 'Sábado', 'Domingo'][timeanddate.weekday()]
    weekday = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][timeanddate.weekday()]
    print(
    '\033[92m' + 'BOT IS NOW ONLINE.' + '\033[0m\n'
    f'Bot user: {bot.user} ID: {bot.user.id}. Running Discord.py {discord.__version__}\n'
    f'{timeanddate.strftime(f"Date: %d/%m/%y, {weekday}. Hour: %H:%M:%S")}')


@bot.event
async def on_error(event, *args, **kwargs):
    embed = discord.Embed(title=':x: Event Error', colour=0xe74c3c)
    embed.add_field(name='Event', value=event)
    embed.description = f'```py\n{traceback.print_exc()}\n```'
    embed.timestamp = datetime.datetime.utcnow()
    await bot.appinfo.owner.send(embed=embed)
    traceback.print_exc()


@bot.event
async def on_command_error(ctx, error):
    if hasattr(ctx.command, 'on_error'): # Ignore commands with local error handlers
        return

    cog = ctx.cog
    if cog:
        if not cog._get_overridden_method(cog.cog_command_error) is None: # pylint: disable=protected-access
            return

    error = getattr(error, 'original', error)

    if isinstance(error, commands.MaxConcurrencyReached):
        return await ctx.reply('Já tem alguém usando esse comando!')

    elif isinstance(error, commands.BotMissingPermissions):
        permissions = '\n'.join([f'{permission}' for permission in error.missing_perms])
        return await ctx.reply(f'Eu não consegui fazer o que foi pedido pois não tenho permissão para:\n{permissions}')

    elif isinstance(error, commands.TooManyArguments):
        return await ctx.reply('Argumentos inválidos')

    elif isinstance(error, commands.BadArgument):
        return await ctx.reply('Argumentos inválidos')

    elif isinstance(error, commands.MissingRequiredArgument):
        if hasattr(error, 'param'):
            return await ctx.reply(f'O argumento do parâmetro `{error.param.name}` está faltando!')
        else:
            return await ctx.reply('Argumentos inválidos')

    elif isinstance(error, commands.DisabledCommand):
        return await ctx.reply('Esse comando está desativado')

    elif isinstance(error, commands.NoPrivateMessage):
        return await ctx.reply('Esse comando não pode ser usado em DMs')

    elif isinstance(error, commands.NotOwner):
        return

    elif isinstance(error, commands.CommandNotFound):
        await ctx.message.add_reaction('❔')
        check = utils.funcs.reaction_check(ctx.message, '❔', ctx.message.author)
        try:
            reaction, _ = await bot.wait_for('reaction_add', timeout=5.0, check=check)
            await reaction.remove(bot.user)
            await ctx.send_help()
            # helpcmd = discord.utils.get(bot.commands, name='ajuda') # doesnt work on 1.7.3?
            # if helpcmd:
            #    await helpcmd.callback(ctx)
        except asyncio.TimeoutError:
            await ctx.message.remove_reaction('❔', bot.user)
        return

    elif isinstance(error, commands.CommandOnCooldown):
        if ctx.author.id == bot.appinfo.owner.id:
            ctx.command.reset_cooldown(ctx)
            try:
                return await ctx.command.reinvoke(ctx)
            except Exception as exc: # pylint: disable=broad-except
                return await on_command_error(ctx, exc)
        return await ctx.reply(f'O comando tá em cooldown! Espera uns {error.retry_after:.1f} segundos aí.')

    else:
        if isinstance(error, discord.errors.HTTPException):
            if hasattr(error, 'status') and hasattr(error, 'code'):
                if error.status == 400 and error.code == 50006:
                    await ctx.reply('Parece que a ordem dos argumentos não está certa ou há argumentos faltando na mensagem.')
        else:
            ctx.reply('Houve um erro ao reproduzir esse comando, as informações do erro foram enviadas para o desenvolvedor.')
            print(f'Erro na execução do comando: {ctx.command}: {error}')
            traceback.print_exception(type(error), error, error.__traceback__)
            log.warning('Erro na execução do comando: %s: %s', ctx.command, error)


def main():
    log.info('Loading extensions...')
    start_perf = time.perf_counter()
    failed = False
    additional_ext = ['jishaku']
    for ext in additional_ext:
        try:
            bot.load_extension(ext)
        except (commands.ExtensionNotFound, commands.NoEntryPointError, commands.ExtensionFailed, ModuleNotFoundError) as exc:
            log.warning('Failed to load external extension: %s: %s', ext, exc)
            failed = True

    for root, _, files in os.walk(os.path.dirname(__file__) + r'\core\commands\cogs'):
        root = root.replace(os.path.dirname(__file__), '')
        while root.startswith('\\'):
            root = root[1:]
        for file in files:
            if file.endswith('.py'):
                try:
                    bot.load_extension('{}.{}'.format(root.replace('\\\\', '.').replace('\\', '.').replace('/', '.'), file[:-3]))
                except (commands.ExtensionNotFound, commands.NoEntryPointError, commands.ExtensionFailed, ModuleNotFoundError) as exc:
                    log.warning('Failed to load extension: %s: %s', file, exc)
                    traceback.print_exc()
                    failed = True
    if not failed:
        log.info('Loaded all extensions successfully in %fs', time.perf_counter() - start_perf)

    bot.run(os.environ['bot_token'])


if __name__ == '__main__':
    main()
