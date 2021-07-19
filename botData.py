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
#-------------------------------- Fun Commands Data ----------------------------------#
susList = botFuncs.loadJson(botFuncs.susStringFile)
reactionsList = ["😂","🤨","🤣","😆","🤔","😠","🤖","🥵","👀","☝","😳","😬","🙄","🤠","⛔","😈","💀","🤡","❌","⁉️"]

#---------------------------------- Commands lists and description Dictionaries ----------------------------------#
commandsList = [
    'regfind',
    'fax',
    'sneak',
    'gif',
    'code',
    'dvc',
    'dm',
    'dmid'
]

modCmdList = [
    'banword',
    'mute',
    'unmute',
    'kick',
    'ban',
    'unban',
]
#-------------------------------------------------- Dictionaries --------------------------------------------------#
commandDescription_dict = {
    commandsList[0] : 'Type this command to extract emails or discord tags from the text you enter after command.',
    commandsList[1] : 'Type this command to get random % of some quality given in commad.',
    commandsList[2] : 'Type this command to make bot say anything you say after command, your message will get deleted instantly.',
    commandsList[3] : 'Gives a Random GIF from tenor - from a given category',
    commandsList[4] : 'Encloses the text given in command in a given format of code snippet.',
    commandsList[5] : 'sends a funny message depending on the platform mentioned-user is active on (Mobile | PC)',
    commandsList[6] : 'sends dm to mentioned user, message = message of command author in command. \n\t(limitation: only users who are in guild can get these messages from bot).',
    commandsList[7] : 'same as {direct_anonymous|dm} but takes user-id instead of user mention,\n\tWorks even if user is not in guild , but should have DM\'s open.'
}

modCmdDescription_dict = {
    modCmdList[0] : 'Type this command to add , remove banned words , can also show list of banwords',
    modCmdList[1] : 'If User is having higher role than muted role, then bot moves the muted role above user\'s highest role \n\tand then mutes the user.',
    modCmdList[2] : 'Unmutes the user.',
    modCmdList[3] : 'Kicks the user from guild.',
    modCmdList[4] : 'Bans the user from guild.',
    modCmdList[5] : 'Un-bans the user form guild.'
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
