import re
import os
from dotenv import load_dotenv
import json
import random
import discord
from discord.ext import commands
import requests
from datetime import datetime

load_dotenv()
# ----------------------------------------------#
default_bot_prefix = "$"
# ----------------------------------------------#

def genRand(randRange=100):
    return random.randint(0,randRange)


def capFistChar(string:str):
    return string[:1].upper() + string[1:]


def getDateTime():
    return datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S")


def dumpJson(pyObj,fileName):
    with open(fileName,"w") as dump:
        json.dump(pyObj,dump,
                  indent=4)


def loadJson(fileName):
    with open(fileName,"r") as load:
        return json.load(load)


def is_owner(ctx:commands.Context):
    owner_id = os.environ['MY_DISCORD_USER_ID']
    return str(ctx.author.id) == owner_id


def load_cogs(client:commands.Bot):
    cog_count = 0
    for filename in os.listdir('./Cogs'):
        if filename.endswith('.py'):
            extension = filename[:-3]
            client.load_extension(f"Cogs.{extension}")
            cog_count += 1
    print(f"Loaded {cog_count} Cogs.")


def log_func(log_string:str, file_name, newlines:int=2):
    new_lines = newlines if newlines >= 1 else 1
    with open(file_name,"a") as logf:
        logf.write(f"{log_string}"+"\n"*new_lines)


def getTenorList(category):
    """
    Tenor's API request's JSON structure:
    whole response is a `dict` with 2 keys
    1 result
    2 next
    result is a `list` of `dict` which containts the info of media which we got
    that `dict` contains a key 'media' which is a `list` of `dict` , the `dict` is having media format as `key`
    so we take 'gif' value from the `dict`
    'gif' returns a `dict` which contains info about that specific gif such as 'preview' and 'url'
    we take 'url' of each 'gif' and store it in a `list`
    this fucntion returns the `list` of gif urls

    structure example:
    ```
    {
        'results' : [
            {
                ...
                ...
                'media' : [
                    {
                        'mp4' : {
                            ...
                            'url' : "https://url/for&the.mp4"
                        }

                        'gif' : {
                            ...
                            ...
                            'url' : "https://this.is.what.we.store.gif"
                        }
                        ...
                    }
                ]
            }
        ]
    }
    """
    number_of_GIFs = 20
    tenor_API_key = os.environ['TENOR_API']
    search_categ = "+".join(category.split(" "))    # replacing " " with "+"
    tUrl = f"https://g.tenor.com/v1/search?q={search_categ}&media_filter=minimal&key={tenor_API_key}&limit={number_of_GIFs}"
    tReq = requests.get(url=tUrl)

    if tReq.status_code == 200:
        responseContent = json.loads(tReq.text)

        resList = responseContent['results']
        listOfDict2 = list()

        for dict in resList:
            listOfDict2.append(dict['media'])

        urlsList = list()

        for xlist in listOfDict2:
            for xdict in xlist:
                try:
                    urlsList.append(xdict['gif']['url'])
                except:
                    pass
        return urlsList
    else:
        return None


def isDiscTag(stringDiscTag):
    # For Unit testing :
    matches = re.findall(r'[\w\s%!.&*-]+#\d{4}',stringDiscTag)
    if matches:
        return True,matches[0]
    else:
        return False,None


if __name__ == '__main__':
    x = 'b'
    while(x != 'a'):
        x = input("enter text for isDiscTag func test: ")
        if x == getTenorList.__name__:
            codet = getTenorList.__code__
            print(codet.co_varnames)
