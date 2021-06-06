"""
The MIT License (MIT)

Copyright (c) 2015-present Rapptz

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import discord.ext.commands.converter
from discord.ext.commands.converter import Greedy
import typing
from typing import Literal, Union
from core.utils.option import Option
import traceback

def signature(command):
    if command.usage is not None:
            return command.usage

    params = command.clean_params
    if not params:
        return ''

    result = []
    for name, param in params.items():
        print(name, param)
        print('aaaaaa')
        #greedy = isinstance(param.annotation, Greedy)
        greedy = False
        print('aaaaaa')
        optionparam = isinstance(param.annotation, Option)
        print('aaaaaa')
        optional = False  # postpone evaluation of if it's an optional argument
        '''try:
            print(param.annotation)
            print(name, param)
            print(Option)
            print(type(Option))
            #isinstance(Option(), Option)
            paramannotation = param.annotation
            print(paramannotation)
        except:
            traceback.print_exc()'''

        for paramtype in typing.get_args(param.annotation):
            '''print(paramtype)
            if isinstance(paramtype, Option):
                optionparam = True'''
                if hasattr(paramtype, '__name__'):
                    if paramtype.__name__ == 'Option':
                        optionparam = True

        print(optionparam)
        print('aaaaaaaaa')
        # for typing.Literal[...], typing.Optional[typing.Literal[...]], and Greedy[typing.Literal[...]], the
        # parameter signature is a literal list of it's values
        annotation = param.annotation.converter if greedy else param.annotation
        origin = getattr(annotation, '__origin__', None)
        if not greedy and origin is Union:
            none_cls = type(None)
            union_args = annotation.__args__
            optional = union_args[-1] is none_cls
            if len(union_args) == 2 and optional:
                annotation = union_args[0]
                origin = getattr(annotation, '__origin__', None)

        if origin is Literal:
            name = '|'.join(f'"{v}"' if isinstance(v, str) else str(v) for v in annotation.__args__)
        if param.default is not param.empty:
            # We don't want None or '' to trigger the [name=value] case and instead it should
            # do [name] since [name=None] or [name=] are not exactly useful for the user.
            should_print = param.default if isinstance(param.default, str) else param.default is not None
            if should_print:
                result.append(f'[{name}={param.default}]' if not greedy else
                                f'[{name}={param.default}]...')
                continue
            else:
                result.append(f'[{name}]')

        elif param.kind == param.VAR_POSITIONAL:
            if command.require_var_positional:
                result.append(f'<{name}...>')
            else:
                result.append(f'[{name}...]')
        elif greedy:
            result.append(f'[{name}]...')
        elif optional:
            result.append(f'[{name}]')
        else:
            result.append(f'<{name}>')
    
    return ' '.join(result)