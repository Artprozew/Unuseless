import time
import datetime
import sys
import os
import textwrap
import discord
from discord.ext import commands
import psutil
import humanize
import pytz

class Bot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(help='Informações do bot', aliases=['bot_info', 'info_bot', 'infobot', 'about', 'sobre'])
    async def botinfo(self, ctx):
        guild_count = 0
        member_count = 0
        for guild in self.bot.guilds:
            guild_count += 1
            member_count += int(guild.member_count)
        end = time.time()
        uptime = int(self.bot.uptime)
        hours, rem = divmod(end - uptime, 3600)
        minutes, seconds = divmod(rem, 60)
        elapsed = '{:0>2}:{:0>2}:{:0>2.0f}'.format(int(hours), int(minutes), seconds)
        pingtime = time.perf_counter()
        embed = discord.Embed(title='Medindo o ping...')
        message = await ctx.reply(embed=embed)
        ping = (time.perf_counter() - pingtime) * 1000
        cmds = 0
        for _ in self.bot.walk_commands():
            cmds += 1
        process = psutil.Process(os.getpid())
        cpu_usage = psutil.cpu_percent()
        cpu_cores = psutil.cpu_count()
        cpu_threads = psutil.cpu_count(logical=False)
        total_ram = humanize.naturalsize(psutil.virtual_memory().total)
        used_ram = humanize.naturalsize(psutil.virtual_memory().used)
        process_used_ram = humanize.naturalsize(process.memory_info()[0])
        process_uptime = time.time() - process.create_time()
        process_pid = process.pid
        embed = discord.Embed(timestamp=datetime.datetime.utcnow())
        host = 'Repl.it'
        if os.name == 'nt':
            host = 'Local'
        embed.add_field(name='__Informações do bot__', value='\u200b', inline=False)
        embed.add_field(name='Nome', value=self.bot.user.name)
        embed.add_field(name='Discord Tag', value=f'#{self.bot.user.discriminator}')
        embed.add_field(name='ID', value=self.bot.user.id)
        embed.add_field(name='Servidores', value=guild_count)
        embed.add_field(name='Usuários', value=member_count)
        embed.add_field(name='Online', value=f'<t:{uptime}:R> (<t:{uptime}:f> ({elapsed}))')
        embed.add_field(name='Desenvolvedor', value=self.bot.appinfo.owner.mention)
        embed.add_field(name='Total de comandos', value=cmds)
        embed.add_field(name='Link de convite do bot', value='[Clique aqui](https://discord.com/api/oauth2/authorize?client_id=843698163785269298&permissions=4228381815&scope=bot)')
        embed.add_field(name='\u200b', value='\u200b', inline=False)
        embed.add_field(name='__Informações para nerds__', value=textwrap.dedent(f'''
        ```yaml
        Linguagem de programação: Python ({sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro})
        Biblioteca: Discord.py ({discord.__version__})
        Websocket Ping: {int(self.bot.latency * 1000)} ms
        Typing Ping: {int(ping)} ms
        Hosting: {host} (Free hosting)
        Uso de CPU: {cpu_usage}%
        Cores/Threads: {cpu_cores} / {cpu_threads}
        RAM: {used_ram} / {total_ram} (Process: {process_used_ram})
        Process PID: {process_pid}
        Process Uptime: {process_uptime}```'''), inline=False)
        '''embed.add_field(name='Link de convite', value='[Convite do bot](https://discord.com/api/oauth2/authorize?client_id=843698163785269298&permissions=4228381815&scope=bot)', inline=True)
        embed.add_field(name='Python',  value=f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} <:python:850174248663384075>')
        embed.add_field(name='Library', value=f'Discord.py {discord.__version__} <:dpylogo:850199786241654834>\n', inline=True)
        embed.add_field(name='Desenvolvedor', value=self.bot.appinfo.owner.mention, inline=True)
        embed.add_field(name='Online desde', value=f'<t:{int(self.bot.uptime)}:F>', inline=True)
        embed.add_field(name='Online há', value=f'<t:{int(self.bot.uptime)}:R> ({elapsed})', inline=True)
        embed.add_field(name='Servidores', value=guild_count, inline=True)
        embed.add_field(name='Usuários', value=member_count, inline=True)'''
        #embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        #embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)
        await message.edit(content='', embed=embed)


    @commands.command(help='Mostra se o bot está funcionando e qual seu tempo de resposta')
    async def ping(self, ctx):
        pingtime = time.perf_counter()
        message = await ctx.reply('Pong! 🏓')
        ping = (time.perf_counter() - pingtime) * 1000
        embed = discord.Embed()
        embed.add_field(name='Websocket Ping 🌐', value=f'```{int(self.bot.latency * 1000)} ms```', inline=False)
        embed.add_field(name='Typing Ping <a:typing:850173912796364830>', value=f'```{int(ping)} ms```', inline=False)
        await message.edit(embed=embed)


    @commands.command()
    async def changelog(self, ctx):
        channel = self.bot.get_guild(850168576287178843).get_channel(862857795136651264)
        logs = []
        async for message in channel.history(limit=6, oldest_first=True):
            logs.append((message.content, message.created_at))
        #logs = '\n'.join(logs)
        embed = discord.Embed(timestamp=datetime.datetime.utcnow())
        embed.add_field(name='__Bot changelog__', value='\u200b', inline=False)
        for log in logs:
            logtime = log[1].replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Brazil/East'))
            embed.add_field(name=logtime.strftime('%d/%m/%y %H:%M'), value=f'**↳** {log[0]}', inline=True)
        #embed.add_field(name='\u200b', value='\u200b', inline=False)
        embed.set_footer(text='Brazil/East timezone')
        #embed.set_footer(text='More: <link to server in #changelogs>')
        await ctx.reply(embed=embed)
        

    @commands.command(aliases=['convite', 'convidar'])
    async def invite(self, ctx):
        embed = discord.Embed(title='Link de convite do bot', url='https://discord.com/api/oauth2/authorize?client_id=843698163785269298&permissions=4228381815&scope=bot', timestamp=datetime.datetime.utcnow())
        await ctx.reply(embed=embed)


    @commands.command(aliases=['tempo_online', 'tempoonline'])
    async def uptime(self, ctx):
        uptime = int(self.bot.uptime)
        elapsed = datetime.datetime.now() - datetime.datetime.fromtimestamp(uptime)
        elapsed = str(datetime.timedelta(seconds=elapsed.seconds))
        embed = discord.Embed(timestamp=datetime.datetime.utcnow())
        embed.add_field(name='Online', value=f'<t:{uptime}:R> (<t:{uptime}:f> ({elapsed}))')
        await ctx.reply(embed=embed)

def setup(bot):
    bot.add_cog(Bot(bot))