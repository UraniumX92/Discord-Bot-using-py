import discord
from discord.ext import commands
import asyncio
import botFuncs
import botData
import mongodbUtils


async def log_and_raise(client:commands.Bot,ctx:commands.Context,error):
    """
    util command to log the un-handled error and raise it, while sending basic error info to users as message
    """
    bot_prefix = mongodbUtils.get_local_prefix(ctx.message)
    author = ctx.author
    channel_name = ctx.channel
    logTime = botFuncs.getDateTime()
    deleteAfter = 2 * 60  # time in seconds
    owner = client.get_user(client.owner_id)

    await ctx.message.add_reaction("❗")
    try:
        guild_name = ctx.guild.name

        with open(botData.errorsLogFile, "a") as erf:
            erf.write(f"[{logTime}] --> {error} -- In Guild : \"{guild_name}\" -- Command User : {author}\n")
        with open(botData.errMessageLogFile, "a") as erMsg:
            erMsg.write(f"[{logTime}] --> {author}: {ctx.message.content} --Guild : \"{guild_name}\" -- Channel: #{channel_name}\n")

        await ctx.send(f"{author.mention}, Either bot doesn't have permission to do the task or you used the command incorrectly\n"
                       f"an error has occurred, Please contact the Bot Dev `{owner}` with this info :\n ```[{logTime}] --> Error occured in command process, in guild: {guild_name} -- channel : #{ctx.message.channel}``` \n"
                       f"This message will be Deleted automatically after **{int(deleteAfter / 60)} minutes**, make sure you copy the error info before this gets deleted", delete_after=deleteAfter)
    except AttributeError:
        # If the error is raised in DM's, it will raise AttributeError, so we handle it here
        with open(botData.errorsLogFile, "a") as erf:
            erf.write(f"[{logTime}] --> {error} -- In Channel : {channel_name} -- Command User : {author}\n")
        with open(botData.errMessageLogFile, "a") as erMsg:
            erMsg.write(f"[{logTime}] --> {author}: {ctx.message.content}  -- Channel: #{channel_name} --Command User : {author}\n")

        await ctx.send(f"{author.mention}, Either bot doesn't have permission to do the task or you used the command incorrectly\n"
                       f"an error has occurred, Please contact the Bot Dev `{owner}` with this info :\n ```[{logTime}] --> Error occured in command process, in channel #{ctx.message.channel}``` \n"
                       f"This message will be Deleted automatically after **{int(deleteAfter / 60)} minutes**, make sure you copy the error info before this gets deleted", delete_after=deleteAfter)
    raise error


async def user_commands_listener(message:discord.Message):
    """
    Custom Command listener which checks if the message has user exclusive command,
    returns a bool, True if command found and response was given , False otherwise
    """
    prefix = mongodbUtils.get_local_prefix(message)
    first_word = message.content.split(" ")[0]

    opted , user_doc = mongodbUtils.is_user_custom_opted(message.author)
    if not opted:
        # if user is not opted in, we return
        return False
    else:
        custom_commands = user_doc['custom_commands']
        if len(custom_commands) == 0:
            # if user is opted in, but haven't made any command yet, we return
            return False

        flag = False
        for dictx in custom_commands:
            if dictx['command'] in first_word:
                command = dictx['command']
                response = dictx['response']
                need_prefix = dictx['need_prefix']
                flag = True
                break

        if not flag:
            # if command not found in user's commands, we return
            return False

        """
        At this point we have found a command in user's commands, now we need to check the prefix condition
        we check if the prefix is in the first word (possible command word) and if prefix is there, we check if it matches with `need_prefix` condition,
        also the whole message must only be command, we check these conditions first,
        if this condition is True , then we respond with `response` or else we return
        """
        prefix_condition = (first_word.startswith(prefix)) == (need_prefix)

        if prefix_condition:
            if need_prefix and message.content == f"{prefix}{command}":
                await message.channel.send(content=response,
                                           reference=message,
                                           mention_author=False)
                return True

            elif (not need_prefix) and message.content == command:
                await message.channel.send(content=response,
                                           reference=message,
                                           mention_author=False)
                return True
            else:
                return False
        else:
            return False


async def guild_command_listener(message:discord.Message):
    """
    Custom Command listener which checks if the message has guild custom command
    returns a bool, True if command found and response was given, False otherwise
    """
    prefix = mongodbUtils.get_local_prefix(message)
    first_word = message.content.split(" ")[0]
    guild : discord.Guild = message.guild

    if not guild:
        # If message is not sent in a server, we return
        return False

    guild_cmd_coll = mongodbUtils.db['guild_custom_commands']
    guild_doc = guild_cmd_coll.find_one({"guild_id": guild.id})
    custom_commands = guild_doc['custom_commands']
    if len(custom_commands) == 0:
        # If the server is not having any custom commands yet, we return
        return False

    flag = False
    for dictx in custom_commands:
        if dictx['command'] in first_word:
            command = dictx['command']
            response = dictx['response']
            need_prefix = dictx['need_prefix']
            flag = True
            break

    if not flag:
        # If command not found in guild's custom commands, we return
        return False
    else:
        """
        At this point we have found a command in guild's custom commands, now we need to check the prefix condition
        we check if the prefix is in the first word (possible command word) and if prefix is there, we check if it matches with `need_prefix` condition,
        also the whole message must only be command, we check these conditions first,
        if these condition are True , then we respond with `response` or else we return
        """
        prefix_condition = (first_word.startswith(prefix)) == (need_prefix)

        if prefix_condition:
            if need_prefix and message.content == f"{prefix}{command}":
                await message.channel.send(content=response,
                                           reference=message,
                                           mention_author=False)
                return True

            elif (not need_prefix) and message.content == command:
                await message.channel.send(content=response,
                                           reference=message,
                                           mention_author=False)
                return True
            else:
                return False
        else:
            return False


async def custcmd_length_check(ctx:commands.Context,command,response):
    """
    to check if the custom commands getting added are in the limits or not, if they're out of limits, this func responds accordingly
    returns True if command and response is in limit, otherwise False
    """
    cmd_len = 150
    resp_len = 1600
    check = False

    if len(command) > cmd_len:
        await ctx.send(f"Custom Command name cannot have more than `{cmd_len}` characters!\n"
                       f"Number of characters in your given command name : `{len(command)}`",
                       reference=ctx.message,
                       mention_author=False)
        return check
    elif len(response) > resp_len:
        await ctx.send(f"Custom Command response cannot have more than `{resp_len}` characters!\n"
                       f"Number of characters in your given command response : `{len(response)}`",
                       reference=ctx.message,
                       mention_author=False)
        return check
    else:
        check = True
        return check


async def change_presence(client:commands.Bot):
    """
    Background Task for bot, keeps changing Bot's presence every set amount of time
    """
    wait_time = 4*60
    await client.wait_until_ready()
    no_of_guilds = len(client.guilds)
    while not client.is_closed():
        await asyncio.sleep(wait_time)
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing,name=" with 0s and 1s in Cloud"))
        await asyncio.sleep(wait_time)
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,name=f" {no_of_guilds} servers! | Mention to know Server prefix"))
        await asyncio.sleep(wait_time)
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening,name=" your Commands 🙂"))
        await asyncio.sleep(wait_time)
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,name=" some YT and chilling in Cloud"))
