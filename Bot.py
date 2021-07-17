import discord
import random
import os
import re
#-------------------------------------------------- My Files - Imports --------------------------------------------------#
import botFuncs
import botData
#---------------------------------------- To get ENVIRONMENT variables from .env ----------------------------------------#
import dotenv
dotenv.load_dotenv()
#------------------------------------------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------------------------------------------------#
cwd = os.getcwd()
banWordFile = (cwd+"/Data Files/bannedWords.data")
prefixFile = (cwd+"/Data Files/prefix.data")
#------------------------------------------------------------------------------------------------------------------------#
botFuncs.createFiles()
bot_prefix = botData.bot_prefix
operatorList = ["+","-","*"] # --> List of operators used in different commands to add , remove and show respectively
#------------------------------------------------------------------------------------------------------------------------#
client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user} is online and ready to go.')
    print(f'Current Bot prefix is : {bot_prefix}')


@client.event
async def on_message(message):
    global bot_prefix
    # Data to extract from each message
    fUserName = str(message.author)
    userName = fUserName.split("#")[0]
    fullMsgList = str(message.content).split(" ")
    lowerMsgList = [word.lower() for word in fullMsgList]
    channelName = str(message.channel)

    if message.author == client.user:
        return

    #TODO-false------------------------------------------------ Help Commands for users and mods ------------------------------------------------#
    if fullMsgList[0] == (f'{bot_prefix}help'):
        if message.content.startswith(f'{bot_prefix}help mod'):
            if fUserName not in botData.modsList:
                await message.channel.send('Only Mods can use this command! and you are not a Mod')
                return
            else:
                modHelpPrompt = botData.modHlelpPromt_func(bot_prefix)
                await message.channel.send(modHelpPrompt)
                return
        else:
            helpPrompt = botData.helpPromt_func(bot_prefix)
            await message.channel.send(helpPrompt)
        return

    #TODO-false------------------------------------------------ Banned Words Warning -------------------------------------------------#
    if not fullMsgList[0] == (f'{bot_prefix}banword') and fUserName in botData.modsList:
        if any(bnword in lowerMsgList for bnword in botData.bannedWords):
            await message.add_reaction("❗")
            await message.channel.send(f"{userName} Watch your language!")
            return

    #TODO-false------------------------------------------------ MOD COMMAND >> Banword Control by Mods -------------------------------------------------#
    # can add , remove words to/from bannedWords | can show the list of banned words
    if fullMsgList[0] == (f"{bot_prefix}banword"):
        # if user tries to escape warning by using $banword in start of message, this will cover up such cases and warn them
        if fUserName not in botData.modsList and any(bnword in lowerMsgList for bnword in botData.bannedWords):
            await message.add_reaction("❗")
            await message.channel.send(f"{userName} Watch your language!")
            return

        try:
            operator = fullMsgList[1].lower()
            banWord = fullMsgList[2].lower()
            cmdWord = fullMsgList[2].lower()
            if operator == "+":
                if banWord not in botData.bannedWords:
                    botData.bannedWords.append(banWord.lower())
                    botFuncs.dumpJson(botData.bannedWords,banWordFile)
                    responseStr = f'Added {banWord} to banned list.'
                else:
                    responseStr = f'{banWord} is already in banned words list.'
            elif operator == "-":
                if banWord in botData.bannedWords:
                    botData.bannedWords.remove(banWord)
                    botFuncs.dumpJson(botData.bannedWords,banWordFile)
                    responseStr = f'Removed {banWord} from the banned words list.'
                else:
                    responseStr = f"can't delete something which is not in banned words' list."
            elif operator == "*" and cmdWord == "show":
                responseStr = '```\nList of Banned words:\n'
                i = 1
                for bword in botData.bannedWords:
                    responseStr += f'{i}. {bword}\n'
                    i+=1
                responseStr += '```'
            else:
                responseStr = (f'```\nIncorrect usage of command {bot_prefix}banword\n'
                               f'correct usage:\n'
                               f'{bot_prefix}banword {{opertaor}} {{word}}\n'
                               f'operator : + , -\n'
                               f'+ to add the word to banned words list\n'
                               f'- to remove the word from banned words list\n'
                               f'Util:\n'
                               f'{bot_prefix}banword * show\n'
                               f'shows all banned words'
                               f'```')

        except Exception as xcept:
            responseStr = (f'```\nIncorrect usage of command {bot_prefix}banword\n'
                           f'correct usage:\n'
                           f'{bot_prefix}banword {{word}} {{opertaor}}\n'
                           f'operator : + , -\n'
                           f'+ to add the word to banned words list\n'
                           f'- to remove the word from banned words list\n'
                           f'Util:\n'
                           f'{bot_prefix}banword * show\n'
                           f'shows all banned words'
                           f'```')

        await message.channel.send(responseStr)
        return
    #TODO-false------------------------------------------------ MOD COMMAND >> 'mod' command to add or remove mods ------------------------------------------------#
    # can add , remove Mod to/from modsList | can show the list of Mods
    if fullMsgList[0] == (f'{bot_prefix}mod'):
        if fUserName not in botData.modsList:
            return

        try:
            operator_mod = fullMsgList[1]
            nameToAdd = fullMsgList[2][1:-1]

            if not botFuncs.isDiscTag(nameToAdd):
                nameToAdd = fullMsgList[2]

            if nameToAdd == "Uranium#4939":
                await message.add_reaction("😂")
                await message.channel.send(f'HAHA Nice Try! `{nameToAdd}` is Owner of this Bot and this bot is not a public bot, so u cant add or remove them from Mod list')
                return

            if operator_mod == "*" and nameToAdd == "show":
                modStr = (f'```\n'
                          f'Displaying List of bot\'s moderators:\n')
                i = 1
                for mod in botData.modsList:
                    modStr += f'Mod - {i} : {mod}\n'
                    i += 1
                modStr += f'```'
                await message.add_reaction("✅")

            elif operator_mod == "+" and botFuncs.isDiscTag(nameToAdd):
                if nameToAdd in botData.modsList:
                    await message.channel.send(f'{nameToAdd} is already in Mods list!')
                    return
                botData.modsList.append(nameToAdd)
                botFuncs.dumpJson(botData.modsList,botFuncs.modListFile)
                modStr = (f'Successfully added `{nameToAdd}` in bot\'s Mod list.')
                await message.add_reaction("✅")

            elif operator_mod == "-" and botFuncs.isDiscTag(nameToAdd):
                if nameToAdd not in botData.modsList:
                    await message.channel.send('Cant remove something which doesn\'nt exist.')
                    return
                botData.modsList.remove(nameToAdd)
                botFuncs.dumpJson(botData.modsList,botFuncs.modListFile)
                modStr = (f'Successfully removed `{nameToAdd}` from bot\'s Mod list.')
                await message.add_reaction("✅")

            else:
                modStr = (f'{userName}, That\'s not the way to use this command\n'
                          f'correct usage:\n'
                          f'```\n'
                          f'{bot_prefix}mod {{operator}} {{`user#1234`}}\n'
                          f'operators:\n'
                          f'+ = add\n- = remove\n'
                          f'to show list of mods, type this:\n'
                          f'{bot_prefix}mod * show\n'
                          f'```')

        except:
            modStr = (f'{userName}, That\'s not the way to use this command\n'
                      f'correct usage:\n'
                      f'```\n'
                      f'{bot_prefix}mod {{operator}} {{`user#1234`}}\n'
                      f'operators:\n'
                      f'+ = add\n'
                      f'- = remove\n'
                      f'to show list of mods, type this:\n'
                      f'{bot_prefix}mod * show\n'
                      f'```')
        await message.channel.send(modStr)

    #TODO-false------------------------------------------------ Util Command to see if bot is responding or not -------------------------------------------------#
    if fullMsgList[0] == (f'{bot_prefix}working'):
        wrkStr = "Yes, It's working\nTesting succesful!"
        await message.add_reaction("✅")
        await message.channel.send(wrkStr)
        return

    #TODO-false------------------------------------------------ Util Commands to show current prefix or to reset to default prefix -------------------------------------------------#
    if fullMsgList[0] == ('mybotprefix'):
        await message.channel.send(f'Current Bot prefix is `{bot_prefix}`')
        return
    elif lowerMsgList[0] == ('ResetMyBotPrefix'.lower()):
        if fUserName not in botData.modsList:
            await message.channel.send('Only Mods can reset prefix! and you are not a Mod')
            return
        print(f'Bot prefix changing from \'{bot_prefix}\' to \'{botFuncs.default_prefix}\'')
        bot_prefix = botFuncs.default_prefix
        botFuncs.dumpJson(bot_prefix,prefixFile)
        await  message.channel.send(f'Bot prefix successfully reset to `{bot_prefix}`')
        return
    #TODO-false------------------------------------------------ Util Prefix Customisation Command -------------------------------------------------#
    if fullMsgList[0] == (f'{bot_prefix}prefix'):
        prefixPrompt = ('Note: Maximum prefix size can be 3 characters\n'
                        'even if you entered a long prefix, bot will only take first 3 characters as prefix')
        prefixStr = (prefixPrompt)

        try:
            temp_prefix = fullMsgList[1]
            new_prefix = temp_prefix[:3] if len(temp_prefix) >= 3  else temp_prefix[:len(temp_prefix)]
            print(f'Bot prefix changing from \'{bot_prefix}\' to \'{new_prefix}\'')
            bot_prefix = new_prefix
            botFuncs.dumpJson(new_prefix,prefixFile)
            prefixStr = (f'Successfully set new prefix as `{new_prefix}`')
        except:
            prefixStr= (f"Enter some character(s) to set as prefix!\n"
                        f"Example: `{bot_prefix}prefix x!`\n"
                        f"sets prefix as `x!`")
        await message.channel.send(prefixStr)
        return

    #TODO-false------------------------------------------------ Util Finding Possible Emails and Discord Tags Using Regex -------------------------------------------------#
    if fullMsgList[0] == (f'{bot_prefix}regfind'): # $regfind {email | disctag} in- whole bunch of words here
        strToSend = str()
        try:
            toFind = lowerMsgList[1]
            boolOperator_present = fullMsgList[2] == "in-"
            find_in_str = " ".join(fullMsgList[3:])
            boolCommandWrong = True

            if toFind.lower() == "email" and boolOperator_present:
                matches = re.findall(r'[\w%./-]+@[a-zA-Z0-9]+[-]*[a-zA-Z0-9]*\.com', find_in_str)
                toFind = "Email"
                boolCommandWrong = False
            elif toFind.lower() == "disctag" and boolOperator_present:
                matches = re.findall(r'[\w%!.&*-]+#\d{4}', find_in_str)
                toFind = "Discord Tag"
                boolCommandWrong = False

            strToSend = (f'```\n{len(matches)} Possible {toFind} matches were extracted from the given text.\n')
            i = 1
            for match in matches:
                strToSend += f'{toFind}-{i} : {match}\n'
                i+=1
            strToSend += '```'

            if (not boolOperator_present) and boolCommandWrong:
                strToSend = ('Incorrect usage of command `regfind`\n'
                         f'{userName}, correct usage is:\n'
                         f'```\n'
                         f'{bot_prefix}regfind {{email | disctag}} in- {{Your text here}}\n'
                         f'\nUsage:\n'
                         f'| --> or\n'
                         '{} exclude the brackets\n'
                         '```')

        except:
            #correct usage example
            strToSend = ('Incorrect usage of command `regfind`\n'
                         f'{userName}, correct usage is:\n'
                         f'```\n'
                         f'{bot_prefix}regfind {{email | disctag}} in- {{Your text here}}\n'
                         f'\nUsage:\n'
                         f'| --> or\n'
                         '{} --> exclude the brackets\n'
                         '```')
        await message.channel.send(strToSend)
        return

    #TODO-false------------------------------------------------ Fun Command fax to display RNG% of some given quality -------------------------------------------------#
    if fullMsgList[0] == (f"{bot_prefix}fax"):
        try:
            objectx = fullMsgList[1]
            objectx = botFuncs.sliceAndCap(objectx)
            strToSend = f'{objectx} is {botFuncs.genRand()}%'
            if len(fullMsgList) >=2:
                for i in range(2,len(fullMsgList)):
                    strToSend += f' {fullMsgList[i]}'
            strToSend += "!"
        except:
            strToSend = (f'{userName}, That\'s the wrong way to use this command\n'
                         f'correct usage:\n'
                         f'```\n'
                         f'{bot_prefix}fax {{thing}} {{quality}}\n'
                         f'for example: {{{bot_prefix}fax bot cool}} will send:\n'
                         f'bot is (random number)% cool!\n'
                         f'Note:\n'
                         f'- Exclude the {{}} brackets.\n'
                         f'```')
        await message.channel.send(strToSend)
        return

    #TODO-false------------------------------------------------ Fun sneak command to imitate message author and del message ------------------------------------------------#
    if fullMsgList[0] == (f'{bot_prefix}sneak'):
        sneakList = fullMsgList
        sneakList.pop(0)
        sneakSend = " ".join(sneakList)
        await message.delete()
        await message.channel.send(sneakSend)
        return

BOT_TOKEN = os.environ['BOT_TOKEN']

client.run(BOT_TOKEN)

#Complete all these to make bot v1
#TO.DO: email and discord tag regex command -my idea ✅
#TO.DO: sneak command which repeats whatever user says, but it deletes the user message instantly - my idea ✅
#TO.DO: admin/mod list -my idea ✅


