import datetime
import discord
from discord.ext import commands
import aiohttp
import typing
import utils
import re
import imghdr
import base64
import pytz
import io
import urllib


class Utilidades(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(aliases=['format', 'code', 'beautify'])
    async def source(self, ctx, red: typing.Optional[int]=0, green: typing.Optional[int]=0, blue: typing.Optional[int]=0, alpha: typing.Optional[int]=255, *, code: utils.option.OptionConverter, theme: utils.option.Option='dracula', language: utils.option.Option='python'):
        theme = code.is_option('theme', 't')
        theme = theme if theme else 'dracula'
        language = code.is_option('language', 'l')
        language = language if language else 'python'
        if code.startswith('```'):
            tmp = code.split()
            if tmp[0][3:]:
                language = tmp[0][3:]
                if language == 'py':
                    language = 'python'
            code = code[3 + len(language):]
            if code.endswith('```'):
                code = code[:-3]
        payload = {
            "code": urllib.parse.quote(code),
            "backgroundColor": f"rgba({red}, {green}, {blue}, {alpha})",
            "language": language,
            "theme": theme
                }
        async with aiohttp.ClientSession() as session:
            async with session.post('https://carbonnowsh.herokuapp.com/', json=payload, headers={"Content-Type": "application/json"}) as resp:
                img = await resp.read()
                await ctx.reply(file=discord.File(io.BytesIO(img), filename='test.png'))


    @commands.command(aliases=['activity', 'presence'])
    async def atividade(self, ctx, user: typing.Optional[discord.User], page: typing.Optional[int]):
        if user:
            member = ctx.guild.get_member(user.id)
            if not member:
                return await ctx.reply('Não consegui achar esse usuário')
            activity = member.activities
            if not activity:
                return await ctx.reply('Parece que esse usuário não está com nenhuma atividade no status')
        else:
            activity = ctx.guild.get_member(ctx.message.author.id).activities
            if not activity:
                return await ctx.reply('Parece que você não está com nenhuma atividade no status')
        if not page:
            activity = activity[0]
        else:
            page = page - 1
            if page >= len(activity):
                page = len(activity) - 1
            if page < 0:
                page = 0
            activity = activity[page]
        if activity:
            embed = discord.Embed(timestamp=datetime.datetime.utcnow())
            if activity.type == discord.ActivityType.listening:
                embed.add_field(name='Título', value=activity.title, inline=False)
                embed.add_field(name='Artista', value=activity.artist, inline=False)
                embed.add_field(name='Álbum', value=activity.album, inline=False)
                embed.set_thumbnail(url=activity.album_cover_url)
            elif activity.type == discord.ActivityType.custom:
                embed.add_field(name='Nome', value=activity.name, inline=False)
            #elif activity.type == discord.ActivityType.streaming:
            #  
            else:
                embed.add_field(name='Nome', value=activity.name, inline=False)
                embed.add_field(name='Detalhes', value=activity.details, inline=False)
                embed.add_field(name='Estado', value=activity.state if not activity.party else f'{activity.state} ({activity.party["size"][0]}/{activity.party["size"][1]})', inline=False)
            if hasattr(activity, 'start'):
                if activity.start:
                    start = activity.start.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Brazil/East'))
                    embed.add_field(name='Começo', value=start.strftime('%d/%m/%y %H:%M:%S'), inline=False)
                    elapsed = datetime.datetime.now(tz=pytz.timezone('Brazil/East')) - start
                    embed.add_field(name='Decorrido', value=str(datetime.timedelta(seconds=elapsed.seconds)), inline=False)

            '''if activity.created_at:
                logtime = activity.created_at.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Brazil/East'))
                embed.add_field(name='Criado', value=logtime.strftime('%d/%m/%y %H:%M:%S'), inline=False)
                if activity.timestamps:
                    if activity.timestamps['start']:
                        #sla = datetime.datetime.utcfromtimestamp(int(activity.timestamps['start']))
                        #print(sla)'''
            if hasattr(activity, 'large_image_url'):
                if activity.large_image_url:
                    embed.set_thumbnail(url=activity.large_image_url)
                    embed.description = activity.large_image_text
            if hasattr(activity, 'small_image_url'):
                if activity.small_image_url:
                    embed.set_author(name=activity.small_image_text, icon_url=activity.small_image_url)
                    #embed.set_footer(icon_url=activity.small_image_url, text='sla')
            await ctx.reply(embed=embed)


    @commands.group(aliases=['encode'])
    async def codificar(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.reply('Você deve especificar um método de codificação')


    @codificar.command(aliases=['b64', 'base64'])
    async def base_64(self, ctx, *, decoded: typing.Optional[str], attachment: typing.Optional[discord.Attachment]=None):
        if decoded:
            decoded = utils.funcs.remove_formattation(decoded)

        if ctx.message.attachments:
            attachment = True
            async with aiohttp.ClientSession() as session:
                async with session.get(ctx.message.attachments[0].url) as response:
                    decoded = await response.read()

        elif not decoded:
            await ctx.reply('Coloque uma mensagem ou uma imagem para ser codificada!')

        if attachment:
            encoded = base64.encodebytes(decoded)
        else:
            encoded = base64.b64encode(decoded.encode())

        encoded = encoded.decode()
        reply = f'Base64 decodificado: ```\n{encoded}```'
        if len(reply) >= 4000:
            await ctx.reply('Base64 decodificado:', file=discord.File(io.BytesIO(encoded), filename=f'base64_text.txt'))
        else:
            await ctx.reply(reply)


    @codificar.command(aliases=['morse'])
    async def morse_code(self, ctx, *, decoded: utils.option.OptionConverter, whitespaces: utils.option.Option=False):
        morse_alphabet = {
        'A'   :    '.-',       'B'   :   '-...',       'C'   :   '-.-.',
        'D'   :    '-..',      'E'   :   '.',          'F'   :   '..-.',
        'G'   :    '--.',      'H'   :   '....',       'I'   :   '..',
        'J'   :    '.---',     'K'   :   '-.-',        'L'   :   '.-..',
        'M'   :    '--',       'N'   :   '-.',         'O'   :   '---',
        'P'   :    '.--.',     'Q'   :   '--.-',       'R'   :   '.-.',
        'S'   :    '...',      'T'   :   '-',          'U'   :   '..-',
        'V'   :    '...-',     'W'   :   '.--',        'X'   :   '-..-',
        'Y'   :    '-.--',     'Z'   :   '--..',       '1'   :   '.----',
        '2'   :    '..---',    '3'   :   '...--',      '4'   :   '....-',
        '5'   :    '.....',    '6'   :   '-....',      '7'   :   '--...',
        '8'   :    '---..',    '9'   :   '----.',      '0'   :   '-----',
        ', '  :    '--..--',   '.'   :    '.-.-.-',    '?'   :   '..--..',
        '/'   :    '-..-.',    '-'   :   '-....-',     '('   :   '-.--.',
        ')'   :    '-.--.-',   ' '   :   '/'
        }

        encoded = ''
        whitespaces = decoded.is_option('whitespaces', 'w')
        if not whitespaces:
            last_char = ''
            for char in decoded.upper():
                if char != ' ' or last_char != ' ':
                    try:
                        encoded += morse_alphabet[char] + ' '
                    except KeyError:
                        encoded += '(?)'
                last_char = char
        else:
            for char in decoded.upper():
                encoded += morse_alphabet[char] + ' '
        await ctx.reply(f'Código morse codificado `{encoded}`')
            


    @commands.group(aliases=['decode'])
    async def decodificar(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.reply('Você deve especificar um método de decodificação')


    @decodificar.command(aliases=['b64', 'base_64'])
    async def base64(self, ctx, *, encoded: typing.Optional[utils.option.OptionConverter], attachment: typing.Optional[discord.Attachment]=None, image: typing.Optional[utils.option.Option]=False):
        if encoded is not None:
            image = encoded.is_option('image', 'i')
            encoded = utils.funcs.remove_formattation(encoded)
            encoded = encoded.replace('\n', '')
                
        if ctx.message.attachments:
            attachment = True
            async with aiohttp.ClientSession() as session:
                async with session.get(ctx.message.attachments[0].url) as response:
                    encoded = await response.read()
                    encoded = encoded.decode()

        if encoded is None and not attachment:
            return await ctx.reply('Coloque um código em Base64 para ser decodificado!')
        
        uri = re.findall('(data:\w+/(\w+);base64,)', encoded)
        for i in uri:
            encoded = encoded.replace(i[0], '')
            image = i[1]

        try:
            decoded64 = base64.b64decode(encoded)
        except (base64.binascii.Error, UnicodeDecodeError):
            try:
                decoded64 = base64.b64decode(encoded + '=')
            except (base64.binascii.Error, UnicodeDecodeError):
                try:
                    decoded64 = base64.b64decode(encoded + '==')
                except (base64.binascii.Error, UnicodeDecodeError):
                    return await ctx.reply('Não identificado como um código em Base64')

        for test in imghdr.tests:
            result = test(decoded64[:44], None)
            if result:
                image = result
                break

        if image:
            await ctx.reply('Imagem decodificada em Base64:', file=discord.File(io.BytesIO(decoded64), filename=f'base64_image.{image if image != True else "png"}'))
        else:
            try:
                reply = f'Base64 decodificado: ```\n{decoded64.decode()}```'
            except UnicodeDecodeError:
                return await ctx.reply('Não identificado como um código em Base64')
            if len(reply) >= 4000:
                await ctx.reply('Base64 decodificado:', file=discord.File(io.BytesIO(decoded64), filename=f'base64_text.txt'))
            else:
                await ctx.reply(reply)

    
    @decodificar.command(aliases=['morse_code'])
    async def morse(self, ctx, *, encoded):
        morse_alphabet = {
        '.-'      :     'A',       '-...'     :      'B',    '-.-.'     :     'C',
        '-..'     :     'D',       '.'        :      'E',    '..-.'     :    'F',
        '--.'     :     'G',       '....'     :      'H',    '..'       :   'I',
        '.---'    :     'J',       '-.-'      :      'K',    '.-..'     :    'L',
        '--'      :     'M',       '-.'       :      'N',    '---'      :   'O',
        '.--.'    :     'P',       '--.-'     :      'Q',    '.-.'      :     'R',
        '...'     :     'S',       '-'        :      'T',    '..-'      :    'U',
        '...-'    :     'V',       '.--'      :      'W',    '-..-'     :    'X',
        '-.--'    :     'Y',       '--..'     :      'Z',    '.----'    :     '1',
        '..---'   :     '2',       '...--'    :      '3',    '....-'    :    '4',
        '.....'   :     '5',       '-....'    :      '6',    '--...'    :    '7',
        '---..'   :     '8',       '----.'    :      '9',    '-----'    :    '0',
        '--..--'  :     ', ',      '.-.-.-'   :      '.',    '..--..'   :    '?',
        '-..-.'   :     '/',       '-....-'   :      '-',    '-.--.'    :     '(',
        '-.--.-'  :     ')'
        }

        decoded = ''
        morse_char = ''
        encoded += ' ' # Extra space at the end to "append" the last character to the string
        for char in encoded:
            if char == ' ':
                if morse_char:
                    try:
                        decoded += morse_alphabet[morse_char]
                    except KeyError:
                        decoded += '(?)'
                    morse_char = ''
            elif char == '/':
                decoded += ' '
            else:
                morse_char += char
        await ctx.reply(f'Código morse decodificado: `{decoded}`')


    @commands.command(aliases=['length'])
    async def textlength(self, ctx, *, text: typing.Optional[str], attachment: typing.Optional[discord.Attachment]=None):
        args = ''
        if text:
            args = utils.funcs.remove_formattation(text)
        elif ctx.message.attachments:
            async with aiohttp.ClientSession() as session:
                async with session.get(ctx.message.attachments[0].url) as response:
                    args = await response.read()
            args = args.decode()
        else:
            ctx.reply('Você deve colocar alguma mensagem ou um arquivo de texto')

        while args.startswith(' '):
            args = args[1:]

        tmp = re.findall('(<\w*(:\w+:)\d+>)', args) # Find emojis and count them only as 1
        length = len(args)

        if tmp:
            for group in tmp:
                length -= len(group[0])
                length += 1

        if length == 1:
            await ctx.reply(f'Isso é apenas {length} caracter/emoji')
        else:
            wordcount = len(args.split())
            if wordcount > 1:
                await ctx.reply(f'Esse texto tem {length} caracteres/emojis e {wordcount} palavras')
            else:
                await ctx.reply(f'Esse texto tem {length} caracteres/emojis')


    @commands.command(aliases=['calc', 'calculadora'])
    async def calcular(self, ctx, *, args):
        tmp = re.search('\((.+)\)', args)
        numberslist = []
        operator = [None]
        operant = []

        if tmp:
            numberslist = tmp.group(1).split(',')
            for i in enumerate(numberslist):
                try:
                    if isinstance(numberslist[i], float):
                        numberslist[i] = float(numberslist[i])
                    elif isinstance(numberslist[i], int):
                        numberslist[i] = int(numberslist[i])
                except ValueError:
                    await ctx.reply(f'Eu ainda não conheço esse tipo de operação com {numberslist[i]}!')
            args = args.replace(tmp.group(), '')

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

        '''operant = []
        args = ' '.join(args)
        args = args.split(' ')
        for i in args:
            print(i)
            if i.isnumeric():
                operant.append(int(i))
            elif re.search('^\d+\.?\d*$', i):
                operant.append(float(i))'''

        operator = [None]
        operant = []

        for index, value in enumerate(message2):
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

        if len(operator) <= 1:
            await ctx.reply('Você deve especificar um operador aritmético!')
            return

        storedoperator = None

        if numberslist:
            if len(operator) > 2:
                storedoperator = operator[1]
                del operator[1] # delete to ignore the first operator (because it will be used with the numberlist later)

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
        if storedoperator:
            operator[1] = storedoperator
        if numberslist:
            if re.search('\d+\.?\d*', str(result)):
                result_isfloat = True
            else:
                result_isfloat = False
            for index, value in enumerate(numberslist):
                if result_isfloat:
                    numberslist[index] = float(numberslist[index])
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

            for index, value in enumerate(numbersresult):
                numbersresult[index] = float(numbersresult[index])
                numbersresult[index] = str(round(numbersresult[index], 2))
            numbersresult = ', '.join(numbersresult)
            result = f'({numbersresult}) {operator[1]} {result}'

        reply = f'Resultado: {result}'
        if len(reply) >= 4000:
            await ctx.reply('Resultado:', file=discord.File(io.BytesIO(result), filename=f'result.txt'))
        else:
            await ctx.reply(f'Resultado: {result}')


def setup(bot):
    bot.add_cog(Utilidades(bot))