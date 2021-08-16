import json
import os
import random
import re
import discord
from discord.ext import commands
import requests
from datetime import datetime

cwd = os.getcwd()
# ----------------------------------------------#
banWordFile = ("./Data Files/bannedWords.json")
prefixesFile = ("./Data Files/prefixes.json")
devsListFile = ("./Data Files/developers.json")
switchesFile = ("./Data Files/switches&data.json")
# ----------------------------------------------#
errorsLogFile = ("./Err Logs/errorLogs.txt")
errMessageLogFile = ("./Err Logs/errorMessages.txt")
# ----------------------------------------------#
susStringFile = ("./Data Files/susString.json")
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


def is_dev(ctx:commands.Context):
    devsList = loadJson(devsListFile)
    return str(ctx.author.id) in devsList.keys()


def load_cogs(client:commands.Bot):
    cog_count = 0
    for filename in os.listdir('./Cogs'):
        if filename.endswith('.py'):
            extension = filename[:-3]
            client.load_extension(f"Cogs.{extension}")
            cog_count += 1
    print(f"Loaded {cog_count} Cogs.")


def createFile_snippet(fileName,typeOfObject,textToWrite = ""):
    if os.path.exists(os.path.join(os.getcwd(),fileName)):
        try:
            if type(loadJson(fileName)) == type(typeOfObject):
                pass
        except:
            with open(fileName,"w") as f:
                f.write(textToWrite)
    else:
        with open(fileName,"w") as f:
            f.write(textToWrite)


def createFiles():

    createFile_snippet(banWordFile,list(),'[]')
    # --------------------------------------------------------------- #
    createFile_snippet(susStringFile,list(),'[]')

    print("Done with file creation.")


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


def get_local_prefix(message:discord.Message):
    """
    takes discord.Message as argument and returns the prefix for the guild which message belongs to
    returns default prefix of bot if command is used in DM of Bot
    """
    try:
        return loadJson(prefixesFile)[str(message.guild.id)]
    except AttributeError:
        """If commands are used in dm , only default bot prefix can be used"""
        return default_bot_prefix


if __name__ == '__main__':
    x = 'b'
    while(x != 'a'):
        x = input("enter text for isDiscTag func test: ")
        if x == getTenorList.__name__:
            codet = getTenorList.__code__
            print(codet.co_varnames)
