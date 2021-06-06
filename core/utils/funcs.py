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

def search_cogs_paths(*cogs, return_all_cogs: bool=False, directory='core/commands/cogs'):
    """
    This function will search for the specified cog(s) in the cogs folder and will return
    its path(s). If return_all_cogs is set to True, it will return the paths of all cogs.
    The folder to search the cogs can also be specified.

    Return: list (or string if only one cog is specified)
    NOTE: The paths returned will be in the format of dotted paths
    ------"""

    cogpaths = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [dir for dir in dirs if not dir == '__pycache__']
        for file in files:
            if file.endswith('.py'):
                if return_all_cogs:
                    cogpaths.append(f'{root.replace("/", ".")}.{file[:-3]}')
                if cogs:
                    if file[:-3] in cogs:
                        if len(cogs) == 1 and not return_all_cogs:
                            return f'{root.replace("/", ".")}.{file[:-3]}'
                        elif not len(cogs) == 1:
                            cogpaths.append(f'{root.replace("/", ".")}.{file[:-3]})')
    return cogpaths


async def replace_emoji_id_by_name(message):
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
