import time
import datetime
import sys
import discord
from discord.ext import commands

class Bot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(help='Informações do bot', aliases=['bot_info'])
    async def botinfo(self, ctx):
        guild_count = 0
        member_count = 0
        for guild in self.bot.guilds:
            guild_count += 1
            member_count += int(guild.member_count)
        end = time.time()
        #e = int(time.time() - start_time)
        #print('{:02d}:{:02d}:{:02d}'.format(e // 3600, (e % 3600 // 60), e % 60))
        #elapsed_time = time.time() - start_time
        #time.strftime('%H:%M:%S', time.gmtime(elapsed_time))
        hours, rem = divmod(end-self.bot.uptime, 3600)
        minutes, seconds = divmod(rem, 60)
        elapsed = '{:0>2}:{:0>2}:{:0>2.0f}'.format(int(hours), int(minutes), seconds)
        embed = discord.Embed(Title='Info', description='Informações do bot', timestamp=datetime.datetime.utcnow())
        embed.add_field(name='Link de convite', value='[Convite do bot](https://discord.com/api/oauth2/authorize?client_id=843698163785269298&permissions=4228381815&scope=bot)', inline=True)
        embed.add_field(name='Python',  value=f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} <:python:850174248663384075>')
        embed.add_field(name='Library', value=f'Discord.py {discord.__version__} <:dpylogo:850199786241654834>\n', inline=True)
        embed.add_field(name='Desenvolvedor', value=self.bot.appinfo.owner.mention, inline=True)
        embed.add_field(name='Tempo online', value=elapsed, inline=True)
        embed.add_field(name='Servidores', value=guild_count, inline=True)
        embed.add_field(name='Usuários', value=member_count, inline=True)
        await ctx.reply(embed=embed)


    @commands.command(help='Mostra se o bot está funcionando e qual seu tempo de resposta')
    async def ping(self, ctx):
        pingtime = time.perf_counter()
        message = await ctx.reply('Pong! 🏓')
        ping = (time.perf_counter() - pingtime) * 1000
        embed = discord.Embed()
        embed.add_field(name='Websocket Ping 🌐', value=f'{int(self.bot.latency * 1000)} ms', inline=False)
        embed.add_field(name='Typing Ping <a:typing:850173912796364830>', value=f'{int(ping)} ms', inline=False)
        await message.edit(embed=embed)


    @commands.command(aliases=['convite', 'convidar'])
    async def invite(self, ctx):
        embed = discord.Embed(title='Link de convite do bot', url='https://discord.com/api/oauth2/authorize?client_id=843698163785269298&permissions=4228381815&scope=bot', timestamp=datetime.datetime.utcnow())
        await ctx.reply(embed=embed)

    @commands.command()
    async def uptime(self, ctx):
        end = time.time()
        hours, rem = divmod(end-self.bot.uptime, 3600)
        minutes, seconds = divmod(rem, 60)
        elapsed = '{:0>2}:{:0>2}:{:0>2.0f}'.format(int(hours), int(minutes), seconds)
        await ctx.reply(f'{elapsed}')

def setup(bot):
    bot.add_cog(Bot(bot))