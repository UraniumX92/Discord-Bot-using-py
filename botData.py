import botFuncs

#TODO: {bot_prefix}help prompt response
#   list which contains commands
#   then a dict whose keys are list[i], value = str - description of the command and usage
#TO.DO: sus command strings list

#----------------------------------- Bot Variables -----------------------------------#
bot_prefix = botFuncs.loadJson(botFuncs.prefixFile)
#-------------------------------------------------------------------------------------#

#-------------------------------- Bot Commands Data ----------------------------------#
bannedWords = botFuncs.loadJson(botFuncs.banWordFile)
modsList = botFuncs.loadJson(botFuncs.modListFile)


#---------------------------------- Commands lists and description Dictionaries ----------------------------------#
commandsList = [
    'working',
    'mybotprefix',
    'prefix',
    'regfind',
    'fax',
    'sneak'
]

modCmdList = [
    'banword',
    'mod',
    'resetmybotprefix'
]
#-------------------------------------------------- Dictionaries --------------------------------------------------#
commandDescription_dict = {
    commandsList[0] : 'Type this command to check if bot is active and responding to messages.',
    commandsList[1] : 'Type this command to check the current prefix of bot.',
    commandsList[2] : 'Type this command to change prefix (maximum length of prefix can be 3).',
    commandsList[3] : 'Type this command to extract emails or discord tags from the text you enter after command.',
    commandsList[4] : 'Type this command to get random % of some quality given in commad.',
    commandsList[5] : 'Type this command to make bot say anything you say after command, your message will get deleted instantly.'
}

modCmdDescription_dict = {
    modCmdList[0] : 'Type this command to add , remove banned words , can also show list of banwords',
    modCmdList[1] : 'Type this command to add , remove Mods , can also show list of Mods.',
    modCmdList[2] : 'Type this command to reset the bot prefix back to `$` '
}

#-------------------------- Functions to create help prompt messages using real time prefix --------------------------#
def helpPromt_func(prefix):
    """Takes commandsList form botData and makes a prompt message for help command"""
    help_prompt = f'```\n'
    for i in range(len(commandsList)):
        if i == 1: # command(s) with no prefix
            help_prompt += f'{commandsList[i]} --> {commandDescription_dict[commandsList[i]]}\n'
        else:
            help_prompt += f'{prefix}{commandsList[i]} --> {commandDescription_dict[commandsList[i]]}\n'
    help_prompt += (f'\n'
                    f'Tip: just type {prefix}{{command}} to know the usage of the complex commands.\n'
                    f'\t for mod commands type this: {prefix}help mod\n'
                    f'```')
    return help_prompt


def modHlelpPromt_func(prefix):
    """Takes modCmdList from botData and makes a prompt message for mod help command"""
    modHelp_prompt = f'```\n'
    for j in range(len(modCmdList)):
        if j == 2: # command(s) with no prefix
            modHelp_prompt += f'{modCmdList[j]} --> {modCmdDescription_dict[modCmdList[j]]}\n'
        else:
            modHelp_prompt += f'{prefix}{modCmdList[j]} --> {modCmdDescription_dict[modCmdList[j]]}\n'
    modHelp_prompt += (f'\n'
                       f'Tip: just type {prefix}{{command}} to know the usage of the complex commands.\n'
                       f'```')
    return modHelp_prompt



if __name__ == '__main__':
    susStrInp = input("Enter sus string to append, // to skip: ")
    if susStrInp == "//":
        pass
    else:
        susList.append(susStrInp)
        botFuncs.dumpJson(susList,botFuncs.susStringFile)

    for item in susList:
        print(item)

    print(help_prompt)
    print(modHelp_prompt)
