import asyncio
import random
from typing import Optional
import discord
from discord.ext import commands

class Fun(commands.Cog, name='Diversão'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def corrida(self, ctx, *racers):
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
            random.shuffle(users)
            winners = ''
            for index, value in enumerate(users):
                index += 1
                if index == 1:
                    winners += f'Primeiro 🥇: {value}\n'
                elif index == 2:
                    winners += f'Segundo 🥈: {value}\n'
                elif index == 3:
                    winners += f'Terceiro 🥉: {value}\n'
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
                    message = await self.bot.wait_for('message', check=check, timeout=10.0)
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


    @commands.command(
        help='Envia uma mensagem para um canal. --silent=True para deletar o comando enviado'
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def say(self, ctx, channel: Optional[discord.TextChannel]=None, *message, silent=False):
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

    def randomstars(self, length):
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
            

    async def ejectmsg2(self, msg, mymsg, currmsg):
        stars = [None]
        length = len(mymsg)
        for i in range(1, 8):
            stars.append(self.randomstars(length))
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


    async def ejectmsg(self, msg, mymsg, currmsg):
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


    @commands.command()
    @commands.max_concurrency(1, commands.BucketType.guild, wait=False)
    async def ejetar(self, ctx, *args):
        msg = await ctx.channel.send('.')
        mymsg = ''
        for arg in args:
            mymsg = mymsg + ' ' + arg
        mymsg = mymsg + ' was{}an Impostor'.format((random.randint(0, 1) and ' not ' or ' '))
        currmsg = ''

        asyncio.run_coroutine_threadsafe(self.ejectmsg(msg, mymsg, currmsg), self.bot.loop)


    @commands.command()
    @commands.max_concurrency(1, commands.BucketType.guild, wait=False)
    async def ejetar2(self, ctx, *args):
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

        asyncio.run_coroutine_threadsafe(self.ejectmsg2(msg, mymsg, currmsg), self.bot.loop)

    @commands.command()
    async def impostor(self, ctx, *args):
        msg = await ctx.channel.send('.')
        mymsg = ''
        for arg in args:
            mymsg = mymsg + ' ' + arg
        currmsg = ''
        
        async def impostormsg(self, msg, mymsg, currmsg):
            for caracter in mymsg:
                if caracter == ' ':
                    currmsg += caracter
                    continue
                else:
                    currmsg += caracter
                    await msg.edit(content=currmsg)
                    await asyncio.sleep(0.7)

        asyncio.run_coroutine_threadsafe(impostormsg(msg, mymsg, currmsg), self.bot.loop)


def setup(bot):
    bot.add_cog(Fun(bot))