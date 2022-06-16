import shlex
from discord.ext import commands


class Option():
    pass


class OptionConverter(commands.Converter):
    async def convert(self, ctx, argument):
        option = OptionParam(argument)
        return OptionParam(option.content, option.options)


class OptionParam(str): # Still needs some improvements?
    def __new__(cls, option=None, options=None):
        cls.options = options
        cls.content = option
        if cls.content and cls.options is None:
            cls.options = {}
            cls.parse_option(cls, cls.content)
        return super().__new__(cls, option)


    def __str__(self):
        return self.content


    def __add__(self, other):
        return OptionParam(str(self) + other, self.options)


    def __radd__(self, other):
        return OptionParam(other + str(self), self.options)


    def parse_option(self, option):
        if isinstance(option, (list, tuple)):
            option = ' '.join(option)
        if isinstance(option, str):
            lex = shlex.shlex(option)
            lex.quotes = '"'
            lex.whitespace_split = True
            lex.commenters = '\\'
            option = list(lex)
        for key, value in zip(option, option[1:]+['--']):
            key = key.lower()
            if key.startswith('-'):
                if value.startswith('-'):
                    self.options[key.strip('-')] = True
                elif value.startswith('"') and value.endswith('"'):
                    self.options[key.strip('-')] = value[1:-1]
                else:
                    self.options[key.strip('-')] = value
                self.content = self.content.replace(' ' + key, '')
                if not value.startswith('-'):
                    self.content = self.content.replace(' ' + value, '')


    def is_option(self, *option):
        for opt in option:
            opt = opt.lower()
            if opt in self.options.keys():
                return self.options[opt]
        return False
