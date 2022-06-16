import datetime
import typing
import re
import discord
from discord.ext import commands
from core import utils
import unidecode
import asyncio

class CustomHelp(commands.HelpCommand):
    def get_command_signature(self, command): # This is a workaround because i couldn't implement this modifying the original Command.signature from Discord.py
        """
        This function will try to know if the typehint annotation of the commands is a "Option Parameter"
        and then will return its signature as [--OptionName] format
        """
        signature = ''
        for name, key, param in zip(command.signature.split(), command.clean_params.keys(), command.clean_params.values()):
            if param.annotation:
                if getattr(param.annotation, '_name', False) == 'Option' or getattr(param.annotation, '__name__', False) == 'Option':
                        signature += f'[--{key}] '
                else:
                    for paramtype in typing.get_args(param.annotation):
                        if getattr(paramtype, '__name__', False) == 'Option':
                            signature += f'[--{key}] '
                            break
                    else:
                        signature += f'{name} '
            else:
                signature += f'{name} '

        return f'{command.qualified_name} {signature}'


    async def send_bot_help(self, mapping):
        embed = discord.Embed(title='Ajuda', timestamp=datetime.datetime.utcnow(), description=
        f'O prefixo do bot para esse servidor é " **{self.clean_prefix}** " \n'
        f'Você pode digitar **{self.clean_prefix}ajuda [comando | grupo]** para saber mais sobre um comando ou grupo de comandos\n\n')
        embed.add_field(name='Grupos de comandos', value='\u200b', inline=False)

        for cog, command in mapping.items():
            cmds = await self.filter_commands(command, sort=True)
            if len(cmds) == 0:
                continue
            category = getattr(cog, 'qualified_name', 'Sem categoria')
            embed.add_field(name=category, value=f'{len(cmds)} {"comando" if len(cmds) == 1 else "comandos"}', inline=True)
        
        channel = self.get_destination()
        await channel.send(embed=embed)


    async def send_command_help(self, command):
        embed = discord.Embed(title=self.get_command_signature(command), timestamp=datetime.datetime.utcnow())
        help = command.help
        brief = command.brief
        alias = command.aliases
        usage = command.usage
        if help:
            embed.add_field(name='Ajuda', value=help, inline=False)
        if brief:
            embed.add_field(name='Descrição', value=brief, inline=False)
        if usage:
            embed.add_field(name='Modo de usar', value=usage, inline=False)
        if alias:
            embed.add_field(name='Outros nomes dado à esse comando', value=', '.join(alias), inline=False)

        channel = self.get_destination()
        if not help and not alias and not usage and not brief:
            embed.add_field(name=':(', value='Esse comando não tem nenhuma informação registrada')
        message = await channel.send(embed=embed)

        await message.add_reaction('❔')
        check = utils.funcs.reaction_check(message, '❔')
        try:
            reaction, _ = await self.context.bot.wait_for('reaction_add', timeout=10.0, check=check)
            await reaction.remove(self.context.bot.user)
            embed = discord.Embed(title='Ajuda com sintaxe dos comandos', timestamp=datetime.datetime.utcnow(), description=
            f'''**Legenda dos parâmetros**:
            `<parâmetro>` = Argumento necessário.
            `[parâmetro]` = Argumento opcional.
            `[--nome]` = Opcional, colocado no final da mensagem. Pode ser usado sozinho ou com mais argumentos caso necessário (Ex.: --nome Arthur). Geralmente pode ser usado alternativamente colocando apenas as suas iniciais (Ex.: --n Arthur).
            
            Lembrando que não é necessário colocar os argumentos entre <> ou [].

            Exemplo de argumentos para o comando `repetir`: `{self.clean_prefix}repetir Grapete repete --silent`. Esse comando com esses argumentos faz com que o bot repita "Grapete repete" apenas, e o parâmetro "--silent" faz com que o comando enviado seja apagado logo depois, ele não será mostrado na mensagem.''')
            await message.reply(embed=embed)
        except asyncio.TimeoutError:
            await message.remove_reaction('❔', self.context.bot.user)
        return


    async def send_cog_help(self, cog):
        embed = discord.Embed(title=f'Ajuda com Grupo: {cog.qualified_name}', description='Comandos do grupo de comandos', timestamp=datetime.datetime.utcnow())
        commands = ''
        for command in cog.walk_commands():
            commands += f'{self.get_command_signature(command)}\n'
        embed.add_field(name=cog.qualified_name, value=commands, inline=False)
        channel = self.get_destination()
        await channel.send(embed=embed)
    

    async def send_group_help(self, group):
        embed = discord.Embed(title=f'Ajuda com Grupo: {group.qualified_name}', description='Comandos do grupo de comandos', timestamp=datetime.datetime.utcnow())
        commands = ''
        for command in group.walk_commands():
            commands += f'{self.get_command_signature(command)}\n'
        embed.add_field(name=group.qualified_name, value=commands, inline=False)
        channel = self.get_destination()
        await channel.send(embed=embed)
    

    async def send_error_message(self, error):
        tmp = re.match('No command called "(.+)" found', error)
        if tmp:
            mapping = self.get_bot_mapping()
            for cog, _ in mapping.items():
                category = getattr(cog, 'qualified_name', 'Sem categoria')
                if unidecode.unidecode(category).lower() == tmp.group(1).lower():
                    await self.send_cog_help(cog)
                    return
            error = f'Não achei um comando/grupo com o nome "{tmp.group(1)}".'
        embed = discord.Embed(title='Erro', description=str(error), timestamp=datetime.datetime.utcnow())
        channel = self.get_destination()
        await channel.send(embed=embed)
            

class Help(commands.Cog, name='Ajuda'):
    def __init__(self, bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        attributes = {
            'name': 'ajuda',
            'aliases': ['help', 'commands', 'cmds', 'comandos'],
            'cooldown': commands.Cooldown(2, 5.0, commands.BucketType.user)
        }
        bot.help_command = CustomHelp(command_attrs=attributes)
        bot.help_command.cog = self


    def cog_unload(self):
        self.bot.help_command = self._original_help_command
        
    def teardown(self):
        self.bot.help_command = self._original_help_command


def setup(bot):
    bot.add_cog(Help(bot))