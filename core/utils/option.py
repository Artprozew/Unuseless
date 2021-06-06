import shlex
from typing import TypeVar, List

opt = TypeVar('opt')

class Option(List[opt]):
    def __init__(self):
        pass
        

class OptionParam():
    def __init__(self, option=None):
        self.options = {}
        if option:
            self.parse_option(option)

    def parse_option(self, option):
        if isinstance(option, (list, tuple)):
            option = ' '.join(option)
        if isinstance(option, str):
            option = shlex.split(option)
        for key, value in zip(option, option[1:]+['--']):
            if key.startswith('-'):
                self.options[key.strip('-')] = True if value.startswith('-') else value

    def is_option(self, *option):
        for opt in option:
            if opt in self.options.keys():
                return self.options[opt]
        return False