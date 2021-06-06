from discord.ext import commands
from  core import utils

async def cog_handler(ctx, mode, bot, cog):
    if '.' in cog:
        try:
            if mode == 'reload':
                bot.reload_extension(cog)
                await ctx.reply('Cog recarregado!')
            elif mode == 'load':
                bot.load_extension(cog)
                await ctx.reply('Cog carregado!')
            elif mode == 'unload':
                bot.unload_extension(cog)
                await ctx.reply('Cog descarregado!')
        except commands.ExtensionNotFound:
            await ctx.reply('Cog não encontrado')
        except commands.ExtensionNotLoaded:
            await ctx.reply('O cog ainda não foi carregado')
        except commands.ExtensionAlreadyLoaded:
            await ctx.reply('O cog já está carregado')
        except (commands.ExtensionError, commands.ExtensionFailed):
            await ctx.reply('Falha')
    else:
        cog = utils.funcs.search_cogs_paths(cog)
        await cog_handler(ctx, mode, bot, cog)


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(aliases=['loadcog', 'lcog'])
    @commands.is_owner()
    async def load_cog(self, ctx, cog):
        await cog_handler(ctx, 'load', self.bot, cog)


    @commands.command(aliases=['unloadcog', 'ucog'])
    @commands.is_owner()
    async def unload_cog(self, ctx, cog):
        await cog_handler(ctx, 'unload', self.bot, cog)


    @commands.command(aliases=['reloadcog', 'rcog'])
    @commands.is_owner()
    async def reload_cog(self, ctx, cog):
        await cog_handler(ctx, 'reload', self.bot, cog)

    
    @commands.command(aliases=['reloadallcogs', 'rall'])
    @commands.is_owner()
    async def reload_all_cogs(self, ctx, load_again: utils.option.Option=None):
        opt = utils.option.OptionParam(load_again)
        cogs = utils.funcs.search_cogs_paths(return_all_cogs=True)
        failed = False
        for cog in cogs:
            try:
                self.bot.reload_extension(cog)
            except commands.errors.ExtensionNotLoaded:
                if not opt.is_option('load_again', 'l'):
                    self.bot.load_extension(cog)
            except (commands.ExtensionFailed, commands.ExtensionError) as exc:
                await ctx.reply(f'Falha ao recarregar a extensão {cog}\n```{exc}```')
                failed = True
        if not failed:
            await ctx.reply(f'Todos os Cogs foram recarregados!')

    @commands.command()
    @commands.is_owner()
    async def teste(self, ctx):
        await ctx.reply('teste')


    @commands.command()
    @commands.is_owner()
    async def leave_current_guild(self, ctx):
        await ctx.reply('Saindo do servidor... :(')
        guild = await self.bot.get_guild(int(ctx.guild.id))
        await guild.leave()


    @commands.command()
    @commands.is_owner()
    async def change_username(self, ctx, *name):
        username = ''
        for arg in name:
            username = username + ' ' + arg
        if len(username) >= 32:
            await ctx.reply('O nome não pode ter mais de 32 caracteres')
        else:
            try:
                await self.bot.user.edit(username=username)
                await ctx.reply('Novo nome: ' + username)
            except Exception as exc:
                await ctx.reply(exc)


    @commands.command()
    @commands.is_owner()
    async def evaluate(self, ctx, *args, awaitfirst=False):
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


    @commands.command()
    @commands.is_owner()
    async def execute(self, ctx, *args):
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


def setup(bot):
    bot.add_cog(Owner(bot))