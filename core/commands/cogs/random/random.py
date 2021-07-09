import datetime
import discord
from discord.ext import commands


class Random(commands.Cog, name='Aleatórios'):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(aliases=['info_canal', 'infocanal', 'channelinfo'])
    async def channel_info(self, ctx):
        embed = discord.Embed(title='Informações sobre o canal', timestamp=datetime.datetime.utcnow())
        embed.add_field(name='Canal', value=ctx.channel.name)
        embed.add_field(name='ID', value=ctx.channel.id)
        embed.add_field(name='Categoria', value=ctx.channel.category)
        embed.add_field(name='ID da categoria', value=ctx.channel.category_id)
        embed.add_field(name='Criado em', value=ctx.channel.created_at)
        embed.add_field(name='Guild', value=ctx.channel.guild)
        embed.add_field(name='Delay do modo lento', value=ctx.channel.slowmode_delay)
        embed.add_field(name='Tipo de canal', value=ctx.channel.type)
        await ctx.reply(embed=embed)

    
    @commands.command(aliases=['reversetext', 'reverse', 'inverter', 'inverter_texto', 'invertertexto'])
    async def reverse_text(self, ctx, *, text):
        await ctx.reply(text[::-1])

    @commands.command()
    async def gusta(self, ctx, *, text):
        await ctx.reply(', '.join(text.split(',')))

def setup(bot):
    bot.add_cog(Random(bot))