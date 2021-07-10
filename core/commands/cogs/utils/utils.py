import discord
from discord.ext import commands
import aiohttp
import typing
from core import utils
import re
import base64
import traceback
import os


class Utilidades(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(
        help='Codifica uma mensagem ou imagem em código Base64'
    )
    async def codificar(self, ctx, *, base_64: typing.Optional[str], attachment: typing.Optional[discord.Attachment]=None):
        if base_64:
            base_64 = utils.funcs.remove_formattation(base_64)
        if ctx.message.attachments:
            attachment = True
            async with aiohttp.ClientSession() as session:
                async with session.get(ctx.message.attachments[0].url) as response:
                    base_64 = await response.read()
        else:
            await ctx.reply('Coloque uma mensagem ou uma imagem para ser codificada!')
        '''tmp = re.search('^\w+:\w+/(\w+);base64,', base_64)
        print('hee')
        if tmp:
            print(base_64)
            base_64 = base_64.replace(tmp.group(), '')
            image = True
            #print(file_request.content)'''
        try:
            if attachment:
                try:
                    encoded = base64.encodebytes(base_64)
                except Exception as e:
                    traceback.print_exc()
                    print('exception')
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


    @commands.command()
    async def decodificar(self, ctx, *, base_64: typing.Optional[str], attachment: typing.Optional[discord.Attachment]=None, image: utils.option.Option=False):
        image = utils.option.OptionParam(base_64, True)
        if image.content:
            base_64 = utils.funcs.remove_formattation(image.content)
                
        elif ctx.message.attachments:
            attachment = True
            async with aiohttp.ClientSession() as session:
                async with session.get(ctx.message.attachments[0].url) as response:
                    base_64 = await response.read()
        '''tmp = re.search('^(\w+:\w+/(\w+);base64,)', base_64)
        print('hee')
        if tmp:
            base_64 = base_64.replace(tmp.group(1), '')
            image = True
            print('true')'''
        print('if imfg')
        if image.is_option('image', 'i'):
            try:
                decoded = base64.b64decode(base_64)
                #decoded = base64.decodebytes(decoded)
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


    @commands.command()
    async def textlength(self, ctx, *, text: typing.Optional[str], attachment: typing.Optional[discord.Attachment]=None):
        args = ''
        if text:
            args = utils.funcs.remove_formattation(text)
            #args = utils.funcs.replace_emoji_id_by_name(args)
        elif ctx.message.attachments:
            async with aiohttp.ClientSession() as session:
                async with session.get(ctx.message.attachments[0].url) as response:
                    args = await response.read()
            args = args.decode()
        while args.startswith(' '):
            args = args[1:]
        length = len(args)
        tmp = re.findall('(<\w*(:\w+:)\d+>)', args)
        if tmp:
            length = len(args)
            for group in tmp:
                length -= len(group[0])
                length += 1
        if length == 1:
            await ctx.reply(f'Isso é apenas {length} caracter/emoji')
        else:
            await ctx.reply(f'Essa frase tem {length} caracteres/emojis')


    @commands.command()
    async def calcular(self, ctx, *, args):
        print(args)
        tmp = re.search('\((.+)\)', args)
        numberslist = []
        operator = [None]
        operant = []
        if tmp:
            numberslist = tmp.group(1).split(',')
            for i in range(len(numberslist)):
                try:
                    print(numberslist[i])
                    if isinstance(numberslist[i], float):
                        numberslist[i] = float(numberslist[i])
                    elif isinstance(numberslist[i], int):
                        numberslist[i] = int(numberslist[i])
                except ValueError:
                    await ctx.reply(f'Eu ainda não conheço esse tipo de operação com {numberslist[i]}!')
            args = args.replace(tmp.group(), '')
        print(args)
        '''for item in lst:
            if len(item) > 1 and not item.isdigit():
            return False
        return True'''
        args = args.split(' ')
        splitted = ''
        message2 = []
        for index, value in enumerate(args):
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
            #args = splitted
            for i in value.split():
                message2.append(i)
            print(args)
            print(value)
            print(splitted, 'splitted')
        print(message2)
        '''operant = []
        args = ' '.join(args)
        args = args.split(' ')
        for i in args:
            print(i)
            if i.isnumeric():
                operant.append(int(i))
            elif re.search('^\d+\.?\d*$', i):
                operant.append(float(i))'''
        print(args)
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
            print('calc')
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
        print(result)
        if storedoperator:
            operator[1] = storedoperator
            print(operator[1])
        if numberslist:
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
            print(numbersresult)
            for index, value in enumerate(numbersresult):
                print(index, value)
                numbersresult[index] = float(numbersresult[index])
                numbersresult[index] = str(round(numbersresult[index], 2))
            numbersresult = ', '.join(numbersresult)
            result = f'({numbersresult}) {operator[1]} {result}'
            print('result')
            print(result)
        try:
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

def setup(bot):
    bot.add_cog(Utilidades(bot))