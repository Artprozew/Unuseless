import datetime
import typing
import re
import discord
from discord.ext import commands

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
            #cogs += f'{cog.qualified_name}'
            cmds = await self.filter_commands(command, sort=True)
            if len(cmds) == 0:
                continue
            category = getattr(cog, 'qualified_name', 'Sem categoria')
            embed.add_field(name=category, value=f'{len(cmds)} {"comando" if len(cmds) == 1 else "comandos"}', inline=True)
        '''for cog, command in mapping.items():
            filtered = await self.filter_commands(command, sort=True)
            cmd_signature = [self.get_command_signature(cmd) for cmd in filtered]
            if cmd_signature:
                category = getattr(cog, 'qualified_name', 'Sem categoria')
                embed.add_field(name=category, value='\n'.join(cmd_signature), inline=True)'''
        
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
        await channel.send(embed=embed)


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
        print(group)
        print(dir(group))
        print(type(group))
    

    async def send_error_message(self, error):
        tmp = re.match('No command called "(.+)" found', error)
        if tmp:
            error = f'Não achei um comando/grupo com o nome "{tmp.group(1)}".'
        embed = discord.Embed(title='Erro', description=str(error), timestamp=datetime.datetime.utcnow())
        channel = self.get_destination()
        await channel.send(embed=embed)
            

class Help(commands.Cog, name='Ajuda'):
    def __init__(self, bot):
        self._original_help_command = bot.help_command
        attributes = {
            'name': 'ajuda',
            'aliases': ['ajudas', 'help', 'helps', 'commands', 'comandos'],
            'cooldown': commands.Cooldown(2, 5.0, commands.BucketType.user)
        }
        bot.help_command = CustomHelp(command_attrs=attributes)
        bot.help_command.cog = self


    def cog_unload(self):
        self.bot.help_command = self._original_help_command


def setup(bot):
    bot.add_cog(Help(bot))