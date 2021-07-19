import json
import os
import random
import re
import requests

cwd = os.getcwd()
# ----------------------------------------------#
banWordFile = cwd+"/Data Files/bannedWords.data"
prefixFile = cwd+"/Data Files/prefix.data"
modListFile = cwd+"/Data Files/modList.data"
# ----------------------------------------------#
susStringFile = (cwd+"/Data Files/susString.data")
# ----------------------------------------------#
default_prefix = "$"
# ----------------------------------------------#

def genRand(randRange=100):
    return random.randint(0,randRange)


def sliceAndCap(text):
    textStr = text
    while textStr[0] == " ":
        textStr = textStr[1:]
    textStr = " ".join(word[:1].upper() + word[1:] for word in textStr.split(" "))
    return textStr


def dumpJson(pyObj,fileName):
    with open(fileName,"w") as dump:
        json.dump(pyObj,dump)


def loadJson(fileName):
    with open(fileName,"r") as load:
        pyObj = json.load(load)
    return pyObj


def createFiles():

    if os.path.exists(os.path.join(os.getcwd(),banWordFile)):
        try:
            if type(loadJson(banWordFile)) == type(list()):
                pass
        except:
            with open(banWordFile,"w") as wf:
                wf.write("[]")
    else:
        with open(banWordFile,"w") as bwf:
            bwf.write("[]")
    # --------------------------------------------------------------- #
    if os.path.exists(os.path.join(os.getcwd(),modListFile)):
        try:
            if type(loadJson(modListFile)) == type(list()):
                pass
        except:
            with open(modListFile,"w") as modF:
                modF.write("[]")
    else:
        with open(modListFile,"w") as mdf:
            mdf.write("[]")
    # --------------------------------------------------------------- #
    if os.path.exists(os.path.join(os.getcwd(),prefixFile)):
        try:
            if type(loadJson(prefixFile)) == type(str()):
                pass
        except:
            with open(prefixFile,"w") as pf:
                pf.write(f'\"{default_prefix}\"')
    else:
        with open(prefixFile,"w") as pf:
            pf.write(f'\"{default_prefix}\"')
    # --------------------------------------------------------------- #
    if os.path.exists(os.path.join(os.getcwd(),susStringFile)):
        try:
            if type(loadJson(susStringFile)) == type(list()):
                pass
        except:
            with open(susStringFile,"w") as sf:
                sf.write("[]")
    else:
        with open(susStringFile,"w") as ssf:
            ssf.write("[]")
    # --------------------------------------------------------------- #

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
    we take 'url' of each 'gif' and store it in a 'list'
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
    categ = category.split(" ")
    search_categ = "+".join(categ)
    tUrl = f"https://g.tenor.com/v1/search?q={search_categ}&media_filter=minimal&key={tenor_API_key}&limit={number_of_GIFs}"
    tReq = requests.get(url=tUrl)

    if tReq.status_code == 200:
        responseContent = json.loads(tReq.text)

        print("Main API URL =", tUrl)
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


def isDiscTag(stringToMatchDiscordTag):
    if re.fullmatch(r'[\w\s%!.&*-]+#\d{4}',stringToMatchDiscordTag):
        return True
    else:
        return False


if __name__ == '__main__':
    print(isDiscTag("Uranium#4939"))
    print(sliceAndCap("hello"))