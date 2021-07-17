import json
import os
import random
import re

cwd = os.getcwd()
# ----------------------------------------------#
banWordFile = cwd+"/Data Files/bannedWords.data"
prefixFile = cwd+"/Data Files/prefix.data"
modListFile = cwd+"/Data Files/modList.data"
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


def readnClear(filename):
    with open(filename) as f:
        lines = f.readlines()
    if len(lines) >= 1000:
        with open(filename, "w") as fclear:
            fclear.write("")
        print("Cleared message log File")


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

    print("Done with file creation.")


def isDiscTag(stringToMatchDiscordTag):
    if re.fullmatch(r'[\w\s%!.&*-]+#\d{4}',stringToMatchDiscordTag):
        return True
    else:
        return False


if __name__ == '__main__':
    print(isDiscTag("Uranium#4939"))
    print(sliceAndCap("hello"))