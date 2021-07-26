import botFuncs
import discord
from discord.ext import commands

#-------------------------------- Bot Commands Data ----------------------------------#
bannedWords = botFuncs.loadJson(botFuncs.banWordFile)
modsList = botFuncs.loadJson(botFuncs.modListFile)
#-------------------------------- Fun Commands Data ----------------------------------#
susList = botFuncs.loadJson(botFuncs.susStringFile)
reactionsList = ['😂','🤮','💀','🤡','💩']

#---------------------------------- {Commands : Description}  Dictionaries ----------------------------------#

commandsDescription_dict = {
    'regfind'   : "Type this command to extract emails or discord tags from the text you enter after command.",
    'fax'       : "Type this command to get random % of some quality given in command.",
    'sneak'     : "Type this command to make bot say anything you say after command, your message will get deleted instantly.",
    'gif'       : "Gives a Random GIF from tenor - from a given category",
    'code'      : "Encloses the text given in command in a given format of code snippet.",
    'dvc'       : "sends a funny message depending on the platform mentioned-user is active on (Mobile | PC)",
    'dm'        : "sends dm to mentioned user, message = message of command author in command. \n\t(limitation: only users who are in guild can get these messages from bot).",
    'dmid'      : "same as {direct_anonymous|dm} but takes user-id instead of user mention,\n\tWorks even if user is not in guild , but should have DM\'s open.",
    'avatar'    : "Shows Avatar of mentioned user, if not mentioned, then shows user\'s avatar."
}

modCmdDescription_dict = {
    'purge'     : "Deletes the speci    fied number of messages from the channel.",
    'banword'   : "Type this command to add , remove banned words , can also show list of banwords",
    'mute'      : "If User is having higher role than muted role, then bot moves the muted role above user\'s highest role \n\tand then mutes the user.",
    'unmute'    : "Unmutes the user.",
    'kick'      : "Kicks the user from guild.",
    'ban'       : "Bans the user from guild.",
    'unban'     : "Un-bans the user form guild.",
    'filter'    : "Turn the message filter for banwords on/off using +/-",
    'pin'       : "Turn the 'Pin Message on Reactions' feature on/off using +/-",
    'rlimit'    : "Bot Feature 'Pin Message on Reactions' : Set the number of reactions needed to pin the message ",
    'difflimit' : "Bot Feature 'Pin Message on Reactions' : Set the number of different reactions required to pin the message"
}

#-------------------------- Functions to create help prompt messages using real time prefix --------------------------#
def helpPromt_func(member : discord.Member, client : commands.Bot):
    """Takes commandsList form botData and makes a Embed message for help command"""
    embed = discord.Embed(title="User Commands:", color=discord.Colour.dark_gold())
    embed.set_thumbnail(url=client.user.avatar_url)
    for command,description in commandsDescription_dict.items():
        embed.add_field(name=command,value=botFuncs.capFistChar(description),inline=False)
    embed.add_field(name="Note:",value="For mod commands, type this: mod_help or mh")

    member_name = str(member.name) + '#' + str(member.discriminator)
    embed.set_footer(text=f"Requested by {member_name}", icon_url=member.avatar_url)
    return embed



def modHlelpPromt_func(member : discord.Member, client : commands.Bot):
    """Takes modCmdList from botData and makes a Embed message for mod help command"""
    embed = discord.Embed(title="Mod Commands:", color=discord.Colour.dark_gold())
    embed.set_thumbnail(url=client.user.avatar_url)
    for command,description in modCmdDescription_dict.items():
        embed.add_field(name=command,value=botFuncs.capFistChar(description),inline=False)

    member_name = str(member.name) + '#' + str(member.discriminator)
    embed.set_footer(text=f"Requested by {member_name}", icon_url=member.avatar_url)
    return embed


if __name__ == '__main__':
    susStrInp = input("Enter sus string to append, // to skip: ")
    if susStrInp == "//":
        pass
    else:
        susList.append(susStrInp)
        botFuncs.dumpJson(susList,botFuncs.susStringFile)

    for item in susList:
        print(item)
