import discord
from discord.ext import commands
from typing import Optional


class Utilidades(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def codificar(self, ctx, *base_64, attachment: Optional=None, image: Optional[bool]=False):
        if base_64:
            message = ''
            for arg in base_64:
                if '--image=true' in arg or '--image=True' in arg:
                    image = True
                    print('true')
                    continue
                message = message + ' ' + arg
            base_64 = message
            base_64 = remove_formattation(base_64)
        if ctx.message.attachments:
            attachment_url = ctx.message.attachments[0].url
            file_request = requests.get(attachment_url)
            base_64 = file_request.content
        '''tmp = re.search('^\w+:\w+/(\w+);base64,', base_64)
        print('hee')
        if tmp:
            print(base_64)
            base_64 = base_64.replace(tmp.group(), '')
            image = True
            #print(file_request.content)'''
        try:
            if image:
                print('try')
                try:
                    print('encod')
                    print('encod')
                    encoded = base64.encodebytes(base_64)
                    print('encod')
                except Exception as e:
                    traceback.print_exc()
                    print('hereeer')
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
    async def decodificar(ctx, *base_64: Optional[str], attachment: Optional=None, image: Optional=False):
        print('start')
        #image = True
        if base_64:
            for arg in base_64:
                message = ''
                if '--image=True' in base_64 or '--image=true' in base_64:
                    print('true')
                    image = True
                    continue
                message = message + ' ' + arg
            base_64 = message
            base_64 = remove_formattation(base_64)
                
        if ctx.message.attachments:
            attachment_url = ctx.message.attachments[0].url
            file_request = requests.get(attachment_url)
            base_64 = file_request.content
            print('hee')
            '''tmp = re.search('^(\w+:\w+/(\w+);base64,)', base_64)
            print('hee')
            if tmp:
                base_64 = base_64.replace(tmp.group(1), '')
                image = True
                print('true')'''
        print('if imfg')
        if image:
            print('try')
            try:
                decoded = base64.decodebytes(base_64)
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
            print('aaa')
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
    async def textlength(ctx, *text: Optional[str], attachment: Optional[discord.Attachment]=None):
        if text:
            args = ''
            for arg in text:
                args = args + ' ' + arg
            args = remove_formattation(args)
            args = replace_emoji_id_by_name(args)
        if ctx.message.attachments:
            attachment_url = ctx.message.attachments[0].url
            file_request = requests.get(attachment_url)
            args = file_request.content
            args = args.decode()
        while args.startswith(' '):
            args = args[1:]
        length = len(args)
        if length == 1:
            await ctx.reply(f'Isso é apenas {length} caracter')
        else:
            await ctx.reply(f'Essa frase têm {length} caracteres')


    @commands.command()
    async def calcular(ctx, *args):
        message = ''
        for arg in args:
            message = message + ' ' + arg
        print(message)
        tmp = re.search('\((.+)\)', message)
        numberslist = []
        operator = [None]
        operant = []
        if tmp:
            print('found')
            numberslist = tmp.group(1).split(',')
            print('kk')
            for i in range(len(numberslist)):
                try:
                    print(numberslist[i])
                    if isinstance(numberslist[i], float):
                        numberslist[i] = float(numberslist[i])
                    elif isinstance(numberslist[i], int):
                        numberslist[i] = int(numberslist[i])
                except ValueError:
                    await ctx.reply(f'Eu ainda não conheço esse tipo de operação com {numberslist[i]}!')
            print('final')
            message = message.replace(tmp.group(), '')
        print('aca')
        print(message)
        '''for item in lst:
            if len(item) > 1 and not item.isdigit():
            return False
        return True'''
        message = message.split(' ')
        splitted = ''
        message2 = []
        for index, value in enumerate(message):
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
            #message = splitted
            for i in value.split():
                message2.append(i)
            print(message)
            print(value)
            print(splitted, 'splitted')
        print('k')
        print(message2)
        '''operant = []
        message = ' '.join(message)
        message = message.split(' ')
        for i in message:
            print(i)
            if i.isnumeric():
                operant.append(int(i))
            elif re.search('^\d+\.?\d*$', i):
                operant.append(float(i))'''
        print(message)
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
            print('aca')
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
        print('veei')
        print(result)
        print('que')
        try:
            if storedoperator:
                operator[1] = storedoperator
                print(operator[1])
        except:
            traceback.print_exc()
        try:
            print('fim')
            if numberslist:
                print('yes')
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
                print('aqui')
                print(numbersresult)
                print('vache')
                print('antes')
                for index, value in enumerate(numbersresult):
                    print(index, value)
                    numbersresult[index] = float(numbersresult[index])
                    numbersresult[index] = str(round(numbersresult[index], 2))
                numbersresult = ', '.join(numbersresult)
                result = f'({numbersresult}) {operator[1]} {result}'
                print('aaa')
                print(result)
        except:
            traceback.print_exc()
        try:
            print('aooooo')
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