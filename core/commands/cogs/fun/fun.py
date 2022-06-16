import asyncio
import random
import time
import typing

import discord
from discord.ext import commands

from core import utils # pylint: disable=import-error


class Fun(commands.Cog, name='Diversão'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        help='Faz uma corrida'
    )
    @commands.max_concurrency(1, commands.BucketType.channel)
    async def corrida(self, ctx, *, racers: typing.Union[discord.Member, str, None]):
        if racers:
            racers = racers.split(', ')
            if len(racers) <= 1:
                return await ctx.reply(f'{racers[0]} não pode correr sozinho')
        participants = []
        await ctx.channel.send('INICIANDO A CORRIDA! 🚦')
        await asyncio.sleep(3)
        await ctx.channel.send('3')
        await asyncio.sleep(1)
        await ctx.channel.send('2')
        await asyncio.sleep(1)
        await ctx.channel.send('1')
        await asyncio.sleep(1)
        await ctx.channel.send('VAAAAAII!!!!')

        async def ShowRanking(participants):
            if participants:
                random.shuffle(participants)
                ranking = ''
                for index, value in enumerate(participants):
                    index += 1
                    if index == 1:
                        ranking += f'Primeiro 🥇: {value}\n'
                    elif index == 2:
                        ranking += f'Segundo 🥈: {value}\n'
                    elif index == 3:
                        ranking += f'Terceiro 🥉: {value}\n'
                    else:
                        ranking += f'{index}º: {value}\n'
                await ctx.channel.send(f'Corrida finalizada! 🏁\nGanhadores:\n{ranking}')

        if racers:
            await asyncio.sleep(5)
            await ShowRanking(racers)
        else:
            def check(message):
                msg = message.content.lower()
                if any(i in msg for i in ('run', 'sprint', 'corre')):
                    if message.channel == ctx.channel:
                        return True
                return False

            async def waitRace():
                try:
                    timer = time.time() + 20
                    while True:
                        timer2 = time.time()
                        if timer2 >= timer:
                            break
                        message = await self.bot.wait_for('message', check=check, timeout=20.0)
                        if not message.author.mention in participants and not message.author.discriminator == '0000':
                            participants.append(message.author.mention)
                    if participants:
                        await ShowRanking(participants)
                except asyncio.TimeoutError:
                    if not participants:
                        await ctx.channel.send('Ninguém participou da corrida')
                    if participants:
                        await ShowRanking(participants)

            asyncio.run_coroutine_threadsafe(waitRace(), self.bot.loop)


    @commands.command(aliases=['8ball', 'bolamagica', 'bola_magica', 'magicball', 'magic_ball'])
    async def ball8(self, ctx, *, message):
        if not message.endswith('?'):
            return await ctx.reply('Você não me fez nenhuma pergunta :thinking:')
        answers = (
            'Mas é claro.',
            'Mas é claro que não.',
            'Com certeza.',
            'Com certeza não.',
            'Eu acredito que sim.',
            'Eu acredito que não.',
            'Talvez.',
            'Provavelmente sim.',
            'Provavelmente não.',
        )
        answer = random.randint(0, len(answers) - 1)
        if not any(i == answer for i in (0, 1, 2, 3)):
            await ctx.reply(random.choice(('Estou pensando...', 'Hmmmmm...', 'Deixe-me pensar...')))
            await asyncio.sleep(random.randint(2, 7))
        await ctx.reply(answers[answer])


    @commands.command(
        help='Envia uma mensagem (para um canal, caso for especificado). --silent para deletar o comando enviado',
        aliases=['repetir', 'dizer', 'falar']
        )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def say(self, ctx, channel: typing.Optional[discord.TextChannel]=None, *, message: utils.option.OptionConverter, silent: utils.option.Option=False):
        if channel is None:
            await ctx.send(message)
        else:
            await channel.send(message)
        if message.is_option('silent', 's'):
            await ctx.message.delete()


    @commands.command()
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def ejetar(self, ctx, *, args):
        msg = await ctx.channel.send('.')
        args = args + ' was{}an Impostor'.format((random.randint(0, 1) and ' not ' or ' '))
        currmsg = ''

        def randomstars(length):
            star = ['.', '。', '•']
            caracters = ''
            for i in range(int(length * 5)):
                caracter = ''
                percentage = random.randint(0, 100)
                if percentage <= 95: # percentage to get space instead of star
                    caracter = ' '
                else:
                    numb = random.randint(0, 2)
                    caracter = star[numb]
                caracters += caracter
            return caracters

        stars = [None]
        length = len(args)
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
        for caracter in args:
            currmsg += caracter
            length2 -= 1
            if caracter == '\\':
                continue
            elif caracter == ' ':
                continue
            else:
                #sendedmsg = sendedmsg.format('{}\n{}\n{}\n')
                sendedmsg = f'{stars[1]}\n{stars[2]}\n{stars[3]}\n{leftstars[0]:<{length2}}{currmsg:^{length2}}{rightstars[0]:>{length2}}\n{leftstars[1]:<{length3}}{" ":^{length3}}{rightstars[1]:>{length3}}\n{stars[6]}\n{stars[7]}'
                await msg.edit(content=sendedmsg)
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


    @commands.command()
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def impostor(self, ctx, *, args):
        msg = await ctx.channel.send('.')
        currmsg = ''
        for char in args:
            if char == ' ':
                currmsg += char
                continue
            else:
                currmsg += char
                await msg.edit(content=currmsg)
                await asyncio.sleep(0.7)

def setup(bot):
    bot.add_cog(Fun(bot))
