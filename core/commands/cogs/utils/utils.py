import datetime
import io
import urllib
import typing
import re
import imghdr

import discord
from discord.ext import commands
import aiohttp
import base64
import pytz
import unidecode

from core import utils # pylint: disable=import-error


class Utilidades(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(aliases=['format', 'code', 'beautify'])
    async def source(self, ctx, red: typing.Optional[int]=0, green: typing.Optional[int]=0, blue: typing.Optional[int]=0, alpha: typing.Optional[int]=255, *, code: utils.option.OptionConverter, theme: utils.option.Option='dracula', language: utils.option.Option='python'):
        theme = code.is_option('theme', 't')
        theme = theme if theme else 'dracula'
        language = code.is_option('language', 'l')
        language2 = language
        if code.startswith('```'):
            tmp = code.split()
            if tmp[0][3:]:
                language = tmp[0][3:]
            code = code[3 + len(language):]
            if code.endswith('```'):
                code = code[:-3]
        language = language2 if language2 else language
        language = language if language else 'python'
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
    async def atividade(self, ctx, user: typing.Optional[discord.User], page: typing.Optional[int]=0, *, name: typing.Optional[str]=None):
        activity = None
        if user:
            user = ctx.guild.get_member(user.id)
            if not user:
                return await ctx.reply('Não consegui achar esse usuário')
            activity = user.activities
            if not activity:
                return await ctx.reply('Parece que esse usuário não está com nenhuma atividade no status')
        else:
            user = ctx.message.author
            activity = user.activities
            if not activity:
                return await ctx.reply('Parece que você não está com nenhuma atividade no status')

        non_custom = [activ for activ in activity if not activ.type == discord.ActivityType.custom]
        if name:
            for activ in non_custom:
                activ_name = getattr(activ, 'name', None)
                if activ_name:
                    if name.lower() == activ_name.lower():
                        activity = activ
                        break
            else:
                return await ctx.reply('Eu não consegui achar uma atividade com esse nome')
        else:
            page = page - 1
            if page >= len(non_custom):
                page = len(non_custom) - 1
            if page < 0:
                page = 0
            if page > len(non_custom):
                if user == ctx.message.author:
                    return await ctx.reply('Parece que você não está com nenhuma atividade no status')
                return await ctx.reply('Parece que esse usuário não está com nenhuma atividade no status')
            activity = non_custom[page]


        class MyEmbed():
            def __init__(self, activity: discord.Activity, username: str):
                self.embed = discord.Embed(timestamp=datetime.datetime.utcnow())
                self.activity = activity
                self.username = username
                self.activity_set = False
                self.activity_type = None
                self.acrivity_color = None

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_value, exc_tb):
                return True

            def __call__(self, activ_type: str, activ_color: int=None):
                self.activity_type = activ_type
                if activ_color:
                    self.embed.colour = activ_color
                return self

            def ActivityField(self, attr: str, name: str):
                attr = getattr(self.activity, attr, None)
                if attr is not None:
                    if self.activity_type and not self.activity_set:
                        self.embed.add_field(name=f'__{self.username} está {self.activity_type}__', value='\u200b', inline=False)
                        self.activity_set = True
                    self.embed.add_field(name=name, value=attr, inline=False)
                    return True
                return False

            def ActivityStatus(self, status: str, attr: str, activ_color: int=None):
                attr = getattr(self.activity, attr, None)
                if attr is not None:
                    if activ_color:
                        self.embed.colour = activ_color
                    self.activity_type = f'{status} {attr}'
                    return True
                return False


        if activity:
            embed = MyEmbed(activity, user.name)

            if hasattr(activity, 'large_image_url'):
                if activity.large_image_url is not None:
                    embed.embed.set_thumbnail(url=activity.large_image_url)
                    if hasattr(activity, 'large_image_text'):
                        if activity.large_image_text is not None:
                            embed.embed.description = activity.large_image_text

            if hasattr(activity, 'small_image_url'):
                if activity.small_image_url is not None:
                    if hasattr(activity, 'small_image_text'):
                        if activity.small_image_text is not None:
                            embed.embed.set_author(name=activity.small_image_text, icon_url=activity.small_image_url)
                        else:
                            embed.embed.set_author(name='\u200b', icon_url=activity.small_image_url)
                    else:
                        embed.embed.set_author(name='\u200b', icon_url=activity.small_image_url)

            if hasattr(activity, 'assets'):
                if 'large_image' in activity.assets:
                    link = re.search('https/(.+)', activity.assets['large_image'])
                    if link:
                        embed.embed.set_thumbnail(url='https://' + link.group(1))

            if activity.type == discord.ActivityType.listening:
                if hasattr(activity, 'title'):
                    with embed('Ouvindo Spotify', 0x1ed760):
                        embed.ActivityField('title', 'Título')
                        embed.ActivityField('artist', 'Artista')
                        embed.ActivityField('album', 'Álbum')
                    if hasattr(activity, 'album_cover_url'):
                        embed.embed.set_thumbnail(url=activity.album_cover_url)
                else:
                    embed.ActivityStatus('Ouvindo', 'name')

            if activity.type == discord.ActivityType.streaming:
                pass

            if activity.type == discord.ActivityType.watching:
                embed.ActivityStatus('Assistindo', 'name')
                embed.ActivityField('name', 'Nome')

            if activity.type == discord.ActivityType.playing:
                name = getattr(activity, 'name', None)
                if name is not None:
                    with embed(f'Jogando {name}', 0xFF0000 if name == 'YouTube' else 0x000000):
                        embed.ActivityField('name', 'Nome')

            embed.ActivityField('details', 'Detalhes')

            if hasattr(activity, 'state'):
                if activity.state is not None:
                    if hasattr(activity, 'party'):
                        if 'size' in activity.party:
                            embed.embed.add_field(name='Estado', value=f'{activity.state} ({activity.party["size"][0]}/{activity.party["size"][1]})', inline=False)
                        else:
                            embed.ActivityField('state', 'Estado')
                    else:
                        embed.ActivityField('state', 'Estado')

            if hasattr(activity, 'start'):
                if activity.start is not None:
                    timenow = datetime.datetime.now(tz=pytz.timezone('Brazil/East'))
                    start = activity.start.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Brazil/East'))
                    embed.embed.add_field(name='Desde', value=start.strftime(f'{"%d/%m/%y" if start.day != timenow.day else ""} %H:%M:%S'), inline=False)
                    elapsed = timenow - start
                    embed.embed.add_field(name='Decorrido', value=str(datetime.timedelta(seconds=elapsed.seconds)), inline=False)

            if hasattr(activity, 'end'):
                if activity.end is not None:
                    remaining = activity.end.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Brazil/East')) - datetime.datetime.now(tz=pytz.timezone('Brazil/East'))
                    embed.embed.add_field(name='Restante', value=str(datetime.timedelta(seconds=remaining.seconds)), inline=False)

            await ctx.reply(embed=embed.embed)


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
            await ctx.reply('Base64 decodificado:', file=discord.File(io.BytesIO(encoded), filename='base64_text.txt'))
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
        decoded = unidecode.unidecode(decoded)
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
        await ctx.reply(f'Código morse codificado: `{encoded}`')



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
                await ctx.reply('Base64 decodificado:', file=discord.File(io.BytesIO(decoded64), filename='base64_text.txt'))
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
        if text:
            text = utils.funcs.remove_formattation(text)
        elif ctx.message.attachments:
            async with aiohttp.ClientSession() as session:
                async with session.get(ctx.message.attachments[0].url) as response:
                    text = await response.read()
            text = text.decode()
        else:
            ctx.reply('Você deve colocar alguma mensagem ou um arquivo de texto')

        while text.startswith(' '):
            text = text[1:]

        tmp = re.findall('(<\w*(:\w+:)\d+>)', text) # Find emojis and count them only as 1
        length = len(text)

        if tmp:
            for group in tmp:
                length -= len(group[0])
                length += 1

        if length == 1:
            await ctx.reply(f'Isso é apenas {length} caracter/emoji')
        else:
            wordcount = len(text.split())
            if wordcount > 1:
                await ctx.reply(f'Esse texto tem {length} caracteres/emojis e {wordcount} palavras')
            else:
                await ctx.reply(f'Esse texto tem {length} caracteres/emojis')


    @commands.command(aliases=['calc', 'calculadora', 'calculate'])
    async def calcular(self, ctx, *, args): # Its pretty messy because i couldnt use eval, but it does work and also there is a trick with numbers between parentheses
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
