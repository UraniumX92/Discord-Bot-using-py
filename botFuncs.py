import json
import os
import random
import re
import requests
from datetime import datetime

cwd = os.getcwd()
# ----------------------------------------------#
banWordFile = (cwd+"/Data Files/bannedWords.data")
prefixFile = (cwd+"/Data Files/prefix.data")
modListFile = (cwd+"/Data Files/modList.data")
switchesFile = (cwd+"/Data Files/switches&data.data")
# ----------------------------------------------#
susStringFile = (cwd+"/Data Files/susString.data")
# ----------------------------------------------#
default_prefix = "$"
# ----------------------------------------------#

def genRand(randRange=100):
    return random.randint(0,randRange)


def capFistChar(string:str):
    return string[:1].upper() + string[1:]


def getDateTime():
    return datetime.now().strftime("%d-%m-%Y %H:%M:%S")


def dumpJson(pyObj,fileName):
    with open(fileName,"w") as dump:
        json.dump(pyObj,dump)


def loadJson(fileName):
    with open(fileName,"r") as load:
        pyObj = json.load(load)
    return pyObj


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
    createFile_snippet(modListFile,list(),'[]')
    # --------------------------------------------------------------- #
    createFile_snippet(prefixFile,str(),default_prefix)
    # --------------------------------------------------------------- #
    createFile_snippet(susStringFile,list(),'[]')
    # --------------------------------------------------------------- #
    createFile_snippet(switchesFile,dict(),'{}')

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


if __name__ == '__main__':
    x = 'b'
    while(x != 'a'):
        x = input("enter text for isDiscTag func test: ")
        if x == getDateTime.__name__:
            print(getDateTime())

