import os
import botFuncs
import discord
from discord.ext import commands
import os
import dotenv
dotenv.load_dotenv()

owner_id = int(os.environ['MY_DISCORD_USER_ID'])
#--------------------------------------- Files ---------------------------------------#
banWordFile = ("./Data Files/bannedWords.json")
prefixesFile = ("./Data Files/prefixes.json")
devsListFile = ("./Data Files/developers.json")
switchesFile = ("./Data Files/switches&data.json")
wordsFile = ("./Data Files/words.json")
topwordsFile = ("./Data Files/topwords1000.json")
quotesFile = ("./Data Files/quotes.json")
# ----------------------------------------------#
guild_joined_EventLogFile = ("./Bot Event Logs/guild_joined.txt")
guild_removed_EventLogFile = ("./Bot Event Logs/guild_remove.txt")
devs_update_EventLogFile = ("./Bot Event Logs/devs_updates.txt")
user_optin_EventLogFile = ("./Bot Event Logs/user_optin.txt")
user_optout_EventLogFile = ("./Bot Event Logs/user_optout.txt")
# ----------------------------------------------#
errorsLogFile = ("./Err Logs/errorLogs.txt")
errMessageLogFile = ("./Err Logs/errorMessages.txt")
# ----------------------------------------------#
susStringFile = ("./Data Files/susString.json")
#-------------------------------- Bot Commands Data ----------------------------------#
bannedWords = botFuncs.loadJson(banWordFile)
devsList = botFuncs.loadJson(devsListFile)
#-------------------------------- Fun Commands Data ----------------------------------#
susList = botFuncs.loadJson(susStringFile)
reactionsList = ['😂','🤮','💀','🤡','💩']
default_bot_prefix = "$"
#-------------------------------------- Embed Limits --------------------------------------#
embed_title_limit = 256 #same for field name
embed_field_value_limit = 1024
embed_description_limit = 4096
embed_footertext_limit = embed_description_limit
embed_fields_limit = 25
#---------------------------------- {Commands : Description}  Dictionaries ----------------------------------#
help_cmd_dict = {
    'help fun' : "Shows the help for Fun Commands",
    'help (utility | util)' : "shows the help for Utility Commands",
    'help custom' : "shows the help for Custom Commands",
    'help reddit' : "shows the help for Reddit Commands",
    'help (moderators | mods | mod)' : "shows the help for Moderator Commands",
    'help (developers | devs | dev)' : "shows the help for Developer Commands"
}

util_cmd_dict = {
    'regfind'   : "Type this command to extract emails or discord tags from the text you enter after command.",
    'gif'       : "Gives a Random GIF from tenor - from a given category",
    'code'      : "Encloses the text given in command in a given format of code snippet.",
    'avatar': "Shows Avatar of mentioned user, if not mentioned, then shows user's avatar.",
    'react': "reply a message with this command (emoji/emoji_name) to make bot react with emoji on referenced message",
    'activity': "Shows the activity and its details of mentioned user, if not mentioned then shows activity of command user, Spotify activity has separate format and details.",
    'nick': "set nick name of mentioned user",
    'snipe': "Get the deleted or edited message history by using this command within 1 minute of Deletion or Edition of message",
    'invite': "Get the invite link of bot, and invite the bot to your server!",
    'ping': "Ping Pong! Get the reaction time of Bot using this command!",
    'tsnow {time_in_hours_min_sec}': "use this command to get the unix timestamp from UTC timezone. If you want your time then add or remove time like this +5h30m | -2h30m30s. Note that h,m,s should be strictly in order",
    'fromts {timestamp}': "use this command to get Date and time from a unix timestamp"

}

fun_cmd_dict = {
    'fax'            : "Type this command to get random % of some quality given in command.",
    'sneak'          : "Type this command to make bot say anything you say after command, your message will get deleted instantly.",
    'device'         : "sends a funny message depending on the platform mentioned-user is active on (Mobile | PC | Web)",
    'dm'             : "sends dm to mentioned user, message = message of command author in command. \n\t(limitation: only users who are in guild can get these messages from bot).",
    'dmid'           : "same as {direct_anonymous|dm} but takes user-id instead of user mention,\n\tWorks even if user is not in guild , but should have DM\'s open.",
    'getquote'       : "get a random quote."
}

game_cmd_dict = {
    'hangman'        : "play a game of hangman.",
    'tictactoe help' : "shows commands to play tictactoe against AI or friends.",
    'typing help'    : "shows commands to play typing game (random words or quotes)."
}

modCmdDescription_dict = {
    'purge'                  : "Deletes the specified number of messages from the channel. if user is mentioned with this command, then deletes the user's messages from the specified number of messages given.",
    'banword'                : "Type this command to add , remove banned words , can also show list of banwords",
    'mute'                   : "If User is having higher role than muted role, then bot moves the muted role above user's highest role \n\tand then mutes the user.",
    'unmute'                 : "Unmutes the user.",
    'kick'                   : "Kicks the user from guild.",
    'ban'                    : "Bans the user from guild.",
    'unban'                  : "Un-bans the user form guild.",
    'switch'                 : "shows the Switches and data",
    'switch filter'          : "Turn the message filter for banwords on/off using +/-",
    'switch pswitch'         : "Turn the 'Pin Message on Reactions' feature on/off using +/-",
    'switch rlimit'          : "Bot Feature 'Pin Message on Reactions' : Set the number of reactions needed to pin the message ",
    'switch difflimit'       : "Bot Feature 'Pin Message on Reactions' : Set the number of different reactions required to pin the message",
    'switch delsnipe'        : "Bot Feature 'delete message snipe' : on/off",
    'switch editsnipe'       : "Bot Feature 'edit message snipe' : on/off",
    'pin'                    : "Reply a message with this command to pin the referenced message",
    'unpin'                  : "Reply a message with this command to un-pin the referenced message",
    'changevc'               : "use this command to move members within Voice Channels, if channel name is not provided , then it disconnects the mentioned user from VC",
    'role add'               : "use this command to add role to mentioned user",
    'role remove'            : "use this command to remove role from mentioned user",
    'role show'              : "use this command to show the list of roles of mentioned user",
    'removecmd | cmd-'       : "use this command to remove the custom command from server's Custom Commands",
    'setchannel | setch'     : "use this command in a channel to set that channel for user join/leave messages",
    'setmsg {msg_type}'      : "use this command to set the messages to be sent by bot when a user joins/leaves the server, in place of 'msg_type' you can write 'join'/'leave' to set the respective messages",
    'disablejoinleave | djl' : "use this command to disable the setting of user join/leave messages"
}

devCmdDescription_dict = {
    'devs' : "shows the list of White listed users, who can use dev commands",
    'devs (add|remove)' : "add or remove user from devs list",
    'logs' : "sends `errorLogs.txt` as `discord.File`",
    'logs messages' : "sends `errorMessages.txt` as `discord.File`",
    'logs clear' : "Enter the name of Logs file with this command to clear the specified Log File",
    'getf' : ("Use this command to get the files from source code by entering path (path starting from main directory)\n"
              "if path is not provided, then shows the list of files which can be fetched using command"),
    'guilds' : "use this command to get the list of guilds of bot and their id's"
}

#-------------------------- Functions to create help prompt messages using real time prefix --------------------------#
def help_embed(title,dictx:dict,member:discord.Member,client:commands.Bot):
    """Takes a dict {command_name : command description} and returns a discord.Embed to send as help command"""
    embed = discord.Embed(title=title, color=discord.Colour.dark_gold())
    embed.set_thumbnail(url=client.user.avatar_url)

    for command,description in dictx.items():
        embed.add_field(name=command,value=botFuncs.capFistChar(description),inline=False)

    embed.set_footer(text=f"Requested by {member}", icon_url=member.avatar_url)
    return embed


if __name__ == '__main__':
    pass
