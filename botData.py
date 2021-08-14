import os

import botFuncs
import discord
from discord.ext import commands
import os
import dotenv
dotenv.load_dotenv()

owner_id = int(os.environ['MY_DISCORD_USER_ID'])
#-------------------------------- Bot Commands Data ----------------------------------#
bannedWords = botFuncs.loadJson(botFuncs.banWordFile)
devsList = botFuncs.loadJson(botFuncs.devsListFile)
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
    'device'    : "sends a funny message depending on the platform mentioned-user is active on (Mobile | PC)",
    'dm'        : "sends dm to mentioned user, message = message of command author in command. \n\t(limitation: only users who are in guild can get these messages from bot).",
    'dmid'      : "same as {direct_anonymous|dm} but takes user-id instead of user mention,\n\tWorks even if user is not in guild , but should have DM\'s open.",
    'avatar'    : "Shows Avatar of mentioned user, if not mentioned, then shows user\'s avatar.",
    'react'     : "reply a message with this command (emoji/emoji_name) to make bot react with emoji on referenced message",
    'activity'  : "Shows the activity and its details of mentioned user, if not mentioned then shows activity of command user, Spotify activity has separate format and details.",
    'nick'      : "set nick name of mentioned user",
    'snipe'     : "Get the deleted or edited message history by using this command within 1 minute of Deletion or Edition of message",
    'invite'    : "Get the invite link of bot, and invite the bot to your server!",
    'ping'      : "Ping Pong! Get the reaction time of Bot using this command!"
}

modCmdDescription_dict = {
    'purge'             : "Deletes the specified number of messages from the channel.",
    'banword'           : "Type this command to add , remove banned words , can also show list of banwords",
    'mute'              : "If User is having higher role than muted role, then bot moves the muted role above user\'s highest role \n\tand then mutes the user.",
    'unmute'            : "Unmutes the user.",
    'kick'              : "Kicks the user from guild.",
    'ban'               : "Bans the user from guild.",
    'unban'             : "Un-bans the user form guild.",
    'switch'            : "shows the Switches and data",
    'switch filter'     : "Turn the message filter for banwords on/off using +/-",
    'switch pswitch'    : "Turn the 'Pin Message on Reactions' feature on/off using +/-",
    'switch rlimit'     : "Bot Feature 'Pin Message on Reactions' : Set the number of reactions needed to pin the message ",
    'switch difflimit'  : "Bot Feature 'Pin Message on Reactions' : Set the number of different reactions required to pin the message",
    'switch delsnipe'   : "Bot Feature 'delete message snipe' : on/off",
    'switch editsnipe'  : "Bot Feature 'edit message snipe' : on/off",
    'pin'               : "Reply a message with this command to pin the referenced message",
    'unpin'             : "Reply a message with this command to un-pin the referenced message",
    'changevc'          : "use this command to move members within Voice Channels, if channel name is not provided , then it disconnects the mentioned user from VC",
    'role add'          : "use this command to add role to mentioned user",
    'role remove'       : "use this command to remove role from mentioned user",
    'role show'         : "use this command to show the list of roles of mentioned user"
}

devCmdDescription_dict = {
    'devs' : "shows the list of White listed users, who can use dev commands",
    'devs (add|remove)' : "add or remove user from devs list",
    'logs' : "sends `errorLogs.txt` as `discord.File`",
    'logs messages' : "sends `errorMessages.txt` as `discord.File`",
    'logs clear' : "Enter the name of Logs file with this command to clear the specified Log File",
    'getf' : ("Use this command to get the files from source code by entering path (path starting from main directory)\n"
              "if path is not provided, then shows the list of files which can be fetched using command")
}

#-------------------------- Functions to create help prompt messages using real time prefix --------------------------#
def helpPrompt_func(member:discord.Member, client:commands.Bot,prefix):
    """Takes commandsDescription_dict and returns discord.Embed for user help command"""
    embed = discord.Embed(title="User Commands:", color=discord.Colour.dark_gold())
    embed.set_thumbnail(url=client.user.avatar_url)
    for command,description in commandsDescription_dict.items():
        embed.add_field(name=command,value=botFuncs.capFistChar(description),inline=False)
    embed.add_field(name="Note:",value=f"For mod commands, type this: **{prefix}modhelp** or **{prefix}mh**\n"
                                       f"For Dev commands, type this: **{prefix}devhelp** or **{prefix}devh**",inline=False)

    embed.set_footer(text=f"Requested by {member}", icon_url=member.avatar_url)
    return embed


def modHelpPrompt_func(member:discord.Member, client:commands.Bot):
    """Takes modCmdDescription_dict and returns discord.Embed for mod help command"""
    embed = discord.Embed(title="Mod Commands:", color=discord.Colour.dark_gold())
    embed.set_thumbnail(url=client.user.avatar_url)
    for command,description in modCmdDescription_dict.items():
        embed.add_field(name=command,value=botFuncs.capFistChar(description),inline=False)

    embed.set_footer(text=f"Requested by {member}", icon_url=member.avatar_url)
    return embed


def devHelpPrompt_func(member:discord.Member,client:commands.Bot):
    """takes devCmdDescription_dict and returns discord.Embed for dev help command"""
    embed = discord.Embed(title="Dev Commands:",color=discord.Colour.dark_gold())
    embed.set_thumbnail(url=client.user.avatar_url)
    for command,description in devCmdDescription_dict.items():
        embed.add_field(name=command,value=botFuncs.capFistChar(description),inline=False)

    embed.set_footer(text=f"Requested by {member}", icon_url=member.avatar_url)
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
