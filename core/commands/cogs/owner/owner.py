import sys
import traceback
import io
import contextlib
import asyncio
import copy
import os

from discord.ext import commands

from core import utils # pylint: disable=import-error


async def cog_handler(ctx, bot, mode, cog):
    if not '.' in cog:
        cog = utils.funcs.search_cogs_paths(cog)
        if not cog:
            return 'Cog não encontrado'
        return await cog_handler(ctx, bot, mode, cog)

    try:
        if mode == 'reload':
            await bot.reload_extension(cog)
            return f'Cog `{cog}` recarregado!'
        elif mode == 'load':
            await bot.load_extension(cog)
            return f'Cog `{cog}` carregado!'
        elif mode == 'unload':
            await bot.unload_extension(cog)
            return f'Cog `{cog}` descarregado!'
        else:
            raise RuntimeWarning(f"No mode of handling cog '{cog}' was chosen")
    except commands.ExtensionNotFound:
        return f'Cog `{cog}` não encontrado'
    except commands.ExtensionNotLoaded:
        return 'O cog ainda não foi carregado'
    except commands.ExtensionAlreadyLoaded:
        return 'O cog já está carregado'
    except (commands.ExtensionError, commands.ExtensionFailed) as exc:
        exc_type, _, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        return f'Falha ao recarregar a extensão {cog}:\n```{exc} ({exc_type} {fname}:{exc_tb.tb_lineno})```'


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        loop = asyncio.get_event_loop()
        return await self.bot.is_owner(ctx.author)

    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx):
        await self.bot.tree.sync()
        return await ctx.reply("Synchronized")

    @commands.command(aliases=['l'])
    @commands.is_owner()
    async def last(self, ctx, max_msgs: int=1, limit: int=25):
        last_msgs = []
        bot_prefix = await self.bot.get_prefix(ctx.message) # Or just remember the last command?
        async for message in ctx.channel.history(limit=limit):
            if message.author == ctx.message.author:
                if message.content.startswith(tuple(bot_prefix)):
                    this_cmd = False
                    for prefix in bot_prefix:
                        for alias in self.last.aliases: # pylint: disable=no-member
                            if message.content.startswith(prefix + alias):
                                this_cmd = True
                    if not this_cmd:
                        last_msgs.append(message)
            if len(last_msgs) == max_msgs:
                break

        for i in last_msgs:
            msg = copy.copy(i)
            msg._update({'content': i.content}) # pylint: disable=protected-access
            ctx2 = await ctx.bot.get_context(msg, cls=type(ctx))
            await ctx2.command.reinvoke(ctx2)


    @commands.command(aliases=['turn_off', 'turnoff'])
    @commands.is_owner()
    async def shutdown(self, ctx, name=None):
        if name:
            name = name.lower()
            if name == 'local' or name == 'pc':
                msg = await ctx.reply('Você tem certeza?')
                await msg.add_reaction('✅')
                check = utils.funcs.reaction_check(msg, '✅', ctx.message.author)
                try:
                    reaction, _ = await self.bot.wait_for('reaction_add', timeout=10.0, check=check)
                    await ctx.reply('Bot desligado 💀')
                    await reaction.remove(self.bot.user)
                    await self.bot.close()
                    sys.exit()
                except asyncio.TimeoutError:
                    await msg.remove_reaction('✅', self.bot.user)
        else:
            msg = await ctx.reply('Você tem certeza?')
            await msg.add_reaction('✅')
            check = utils.funcs.reaction_check(msg, '✅', ctx.message.author)
            try:
                reaction, _ = await self.bot.wait_for('reaction_add', timeout=10.0, check=check)
                await ctx.reply('Bot desligado 💀')
                await reaction.remove(self.bot.user)
                await self.bot.close()
                sys.exit()
            except asyncio.TimeoutError:
                await msg.remove_reaction('✅', self.bot.user)


    @commands.command(aliases=['loadcog', 'lcog'])
    @commands.is_owner()
    async def load_cog(self, ctx, cog):
        await ctx.reply(await cog_handler(ctx, self.bot, 'load', cog))


    @commands.command(aliases=['unloadcog', 'ucog'])
    @commands.is_owner()
    async def unload_cog(self, ctx, cog):
        await ctx.reply(await cog_handler(ctx, self.bot, 'unload', cog))


    @commands.command(aliases=['reloadcog', 'rcog'])
    @commands.is_owner()
    async def reload_cog(self, ctx, cog):
        await ctx.reply(await cog_handler(ctx, self.bot, 'reload', cog))


    @commands.command(aliases=['reloadallcogs', 'rall'])
    @commands.is_owner()
    async def reload_all_cogs(self, ctx, *, args: utils.option.OptionConverter=None, prevent_load: utils.option.Option=None):
        if args is not None:
            prevent_load = args.is_option('prevent_load', 'pl', 'p')
        cogs = utils.funcs.search_cogs_paths(return_all_cogs=True)
        failed = False
        for cog in cogs:
            try:
                await self.bot.reload_extension(cog)
            except commands.ExtensionNotLoaded:
                if not prevent_load:
                    await self.bot.load_extension(cog)
            except (commands.ExtensionFailed, commands.ExtensionError) as exc:
                exc_type, _, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                await ctx.reply(f'Falha ao recarregar a extensão {cog}:\n```{exc} ({exc_type} {fname}:{exc_tb.tb_lineno})```')
                failed = True
        if not failed:
            await ctx.reply('Todos os Cogs foram recarregados!')



    @commands.command()
    @commands.is_owner()
    async def teste(self, ctx):
        await ctx.reply(ctx.channel.last_message)


    @commands.command(aliases=['leaveguild', 'leaveserver', 'leave_server'])
    @commands.is_owner()
    async def leave_guild(self, ctx):
        msg = await ctx.reply('Você tem certeza?')
        await msg.add_reaction('✅')
        check = utils.funcs.reaction_check(msg, '✅', ctx.message.author)
        try:
            reaction, _ = await self.bot.wait_for('reaction_add', timeout=10.0, check=check)
            await ctx.reply('Saindo do servidor 😢')
            await reaction.remove(self.bot.user)
            guild = self.bot.get_guild(int(ctx.guild.id))
            await guild.leave()
        except asyncio.TimeoutError:
            await msg.remove_reaction('✅', self.bot.user)


    @commands.command()
    @commands.is_owner()
    async def change_username(self, ctx, name: str):
        name
        if len(name) >= 32:
            await ctx.reply('O nome não pode ter mais de 32 caracteres')
        else:
            await self.bot.user.edit(username=name)
            await ctx.reply('Novo nome: ' + name)


    @commands.command(aliases=['eval'])
    @commands.is_owner()
    async def evaluate(self, ctx, *, args: utils.option.OptionConverter, awaitfirst: utils.option.Option=None):
        awaitfirst = args.is_option('awaitfirst', 'af')
        args = utils.funcs.remove_formattation(args)
        try:
            if awaitfirst:
                await ctx.reply(await eval(args)) # pylint: disable=eval-used
            else:
                await ctx.reply(eval(args)) # pylint: disable=eval-used
        except Exception: # pylint: disable=broad-except
            exc_type, exc_value, _ = sys.exc_info()
            #exc = traceback.format_exc(chain=False)
            if exc_type.__name__ == 'HTTPException':
                await ctx.reply(f'Returned an empty string (`{exc_value}`)')
            else:
                exc = traceback.format_exception_only(exc_type, exc_value)
                exc = ' '.join(exc)
                if '```' in exc:
                    exc = exc.replace('```', '')
                await ctx.reply(f'Exception: ```py\n{exc}```')


    @commands.command(aliases=['exec'])
    @commands.is_owner()
    async def execute(self, ctx, *, args: utils.option.OptionConverter, noformattation: utils.option.Option=False, raw: utils.option.Option=False):
        noformattation = args.is_option('noformattation', 'nf')
        raw = args.is_option('raw', 'r')
        args = utils.funcs.remove_formattation(args)
        try:
            result = io.StringIO()
            with contextlib.redirect_stdout(result), contextlib.redirect_stderr(result):
                exec('async def __ex(self, ctx): ' + ''.join(f'\n {line}' for line in args.split('\n'))) # pylint: disable=exec-used
                await locals()['__ex'](self, ctx)
            result = result.getvalue()
            if result:
                if raw:
                    await ctx.reply(result)
                elif noformattation:
                    await ctx.reply(f'Resultado: {result}')
                else:
                    await ctx.reply(f'Resultado: ```py\n{result}```')
            else:
                await ctx.message.add_reaction('🔇')
        except Exception: # pylint: disable=broad-except
            exc_type, exc_value, _ = sys.exc_info()
            if exc_type.__name__ == 'HTTPException':
                await ctx.message.add_reaction('🔇')
            else:
                exc = traceback.format_exception_only(exc_type, exc_value)
                exc = ' '.join(exc)
                if '```' in exc:
                    exc = exc.replace('```', '')
                await ctx.reply(f'Exception: ```py\n{exc}```')


async def setup(bot):
    await bot.add_cog(Owner(bot))
