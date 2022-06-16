import os
import re

class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def search_cogs_paths(*cogs, return_all_cogs: bool=False, directory=None):
    """
    This function will search for the specified cog(s) in the cogs folder and will return
    its path(s). If return_all_cogs is set to True, it will return the paths of all cogs.
    The folder to search the cogs can also be specified.

    Return: list (string if only one cog is specified) (the list can be empty if nothing is found)
    NOTE: The paths returned will be in the format of dotted paths
    ------"""

    cogpaths = []
    if not directory:
        directory = os.path.dirname(os.path.dirname(__file__)) + r'\commands\cogs'
    for root, dirs, files in os.walk(directory):
        dirs[:] = [direc for direc in dirs if not direc == '__pycache__']
        root = root.replace(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '') # Remove everything before the main directory
        while root.startswith('\\'):
            root = root[1:]
        for file in files:
            if file.endswith('.py'):
                if return_all_cogs:
                    cogpaths.append('{}.{}'.format(root.replace('/', '.').replace('\\\\', '.').replace('\\', '.'), file[:-3]))
                if cogs:
                    if file[:-3] in cogs:
                        if len(cogs) == 1 and not return_all_cogs:
                            return '{}.{}'.format(root.replace('/', '.').replace('\\\\', '.').replace('\\', '.'), file[:-3])
                        elif not len(cogs) == 1:
                            cogpaths.append('{}.{}'.format(root.replace('/', '.').replace('\\\\', '.').replace('\\', '.'), file[:-3]))
    return cogpaths


def replace_emoji_id_by_name(message):
    tmp = re.findall('(<\w*(:\w+:)\d+>)', message)
    if tmp:
        for group in tmp:
            message = message.replace(group[0], group[1])
    return message


async def replace_user_id_by_name(bot, message):
    tmp = re.findall('(<@!?(\d+)>)', message)
    if tmp:
        for group in tmp:
            member = await bot.fetch_user(group[1])
            if member:
                if member.id == bot.appinfo.owner.id:
                    message = f'{colors.FAIL}{message}{colors.ENDC}'
                    message = message.replace(group[0], f'{colors.OKBLUE}@{member}{colors.FAIL}')
                else:
                    message = message.replace(group[0], f'{colors.OKBLUE}@{member}{colors.ENDC}')
    return message


def remove_formattation(formatted_string):
    formatted_string = re.sub('^(```[a-zA-Z]*)', '', formatted_string)
    formatted_string = re.sub('(```)$', '', formatted_string)
    formatted_string = re.sub('^(`)', '', formatted_string)
    formatted_string = re.sub('(`)$', '', formatted_string)
    return formatted_string


def reaction_check(message=None, emoji=None, author=None, ignore_bot=True): # Thanks to Patrick Haugh on StackOverflow for sharing this function
    '''Function to check arguments made mainly to use with the Client.wait_for "check" parameter
    
    Usage example:
    check = reaction_check(ctx.message, '❔', ctx.message.author)
    reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)'''

    def make_sequence(seq):
        from collections.abc import Sequence
        if seq is None:
            return ()
        if isinstance(seq, Sequence) and not isinstance(seq, str):
            return seq
        else:
            return (seq,)

    message = make_sequence(message)
    message = tuple(m.id for m in message)
    emoji = make_sequence(emoji)
    author = make_sequence(author)

    def check(reaction, user):
        if ignore_bot and user.bot:
            return False
        if message and reaction.message.id not in message:
            return False
        if emoji and reaction.emoji not in emoji:
            return False
        if author and user not in author:
            return False
        return True
    return check