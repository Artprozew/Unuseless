import shlex
from typing import TypeVar, List
from discord.ext import commands


opt = TypeVar('opt')

class Option(List[opt]):
    def __init__(self):
        return True
        

class OptionConverter(commands.Converter):
    async def convert(self, ctx, args):
        return OptionParam(args, True)


class OptionParam(): # Still needs some improvements
    def __init__(self, option=None, strip=False):
        self.options = {}
        self.content = option
        if option:
            self.parse_option(option, strip)

    def parse_option(self, option, strip=False):
        if isinstance(option, (list, tuple)):
            option = ' '.join(option)
        if isinstance(option, str):
            option = shlex.split(option)
        if strip:
            strip = ''
        for key, value in zip(option, option[1:]+['--']):
            key = key.lower()
            if key.startswith('-'):
                self.options[key.strip('-')] = True if value.startswith('-') else value
                if strip != False:
                    self.content = self.content.replace(key, '')
                    if not value.startswith('-'):
                        self.content = self.content.replace(value, '')

    def is_option(self, *option):
        for opt in option:
            opt = opt.lower()
            if opt in self.options.keys():
                return self.options[opt]
        return False