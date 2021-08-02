import discord
import random
import asyncio
import os
import re
from discord.ext import commands
from datetime import datetime
#-------------------------------------------------- My Files - Imports --------------------------------------------------#
import botFuncs
import botData
#---------------------------------------- To get ENVIRONMENT variables from .env ----------------------------------------#
import dotenv
dotenv.load_dotenv()
#------------------------------------------------------------------------------------------------------------------------#
cwd = os.getcwd()
banWordFile = (cwd+"/Data Files/bannedWords.json")
prefixFile = (cwd+"/Data Files/prefix.json")
switchesFile = (cwd+"/Data Files/switches&data.json")
#------------------------------------------------ Error Logging Files ---------------------------------------------------#
errorsLogFile = (cwd+"/Err Logs/errorLogs.txt")
errMessageLogFile = (cwd+"/Err Logs/errorMessages.txt")
#------------------------------------------------------------------------------------------------------------------------#
botFuncs.createFiles()
bot_prefix = "$"
operatorList = ["+","-","*"] # --> List of operators used in different commands to add , remove and show respectively
#------------------------------------------------------------------------------------------------------------------------#
owner_id = int(os.environ['MY_DISCORD_USER_ID'])

activity = discord.Activity(type=discord.ActivityType.listening,
                            name=" your Commands 🙂",
                            start=datetime.now(),
                            )

client = commands.Bot(command_prefix=bot_prefix,
                      help_command=None,
                      activity=activity,
                      owner_id=owner_id,
                      intents=discord.Intents.all()
                      )


@client.event
async def on_ready():
    print(f'{client.user} is online and ready to go.')
    print(f'Current Bot prefix is : {bot_prefix}')
    print(f"Bot went online on : [{botFuncs.getDateTime()}]")


@client.event
async def on_message_delete(message):
    def check(msg:discord.Message):
        return msg.channel.id == message.channel.id

    delSwitch = botFuncs.loadJson(switchesFile)['del_snipe_switch']

    try:
        respMsg = await client.wait_for(event='message',check=check,timeout=60)
    except asyncio.TimeoutError:
        pass
    else:
        if respMsg.content == f"{bot_prefix}snipe" and delSwitch:
            del_msg_author = message.author
            embed = discord.Embed(title=f"{del_msg_author}'s Message Delete Snipe",description=f"{del_msg_author}: {message.content}",color=discord.Colour.dark_gold())
            return await respMsg.channel.send(embed=embed)


@client.event
async def on_message_edit(before,after):
    def check(msg:discord.Message):
        return msg.channel.id == before.channel.id

    editSwitch = botFuncs.loadJson(switchesFile)['edit_snipe_switch']

    pinned_or_unPinned = before.pinned != after.pinned
    """
    pinning and un-pinning the message will also count as message edit and will trigger this event, 
    so, in order to avoid the command triggering if the message got pinned or un-pinned, we make this condition `pinned_or_unPinned`
    it checks if message got pinned or unpinned
    """
    if not pinned_or_unPinned:
        """
        Client will process the edited message for commands, this is for ease of use for commands which are having more text, 
        just editing and adjusting the command right way will be enough to use command instead of writing same command again
        """
        await client.process_commands(after)

    try:
        respMsg = await client.wait_for(event='message',check=check,timeout=60)
    except asyncio.TimeoutError:
        pass
    else:
        if respMsg.content == f"{bot_prefix}snipe" and editSwitch:
            edit_msg_author = after.author
            embed = discord.Embed(title=f"{edit_msg_author}'s Message edit Snipe",color=discord.Colour.dark_gold())
            embed.add_field(name="Previous:",value=f"{before.content}",inline=False)
            embed.add_field(name="Edited:",value=f"{after.content}",inline=False)
            return await respMsg.channel.send(embed=embed)


@client.event
async def on_raw_reaction_add(payload):
    """
    if `number_of_reactions` reaches `react_limit_toPin`, and `number_of_diff_reactions` reaches `diff_reaction_limit`,
    then the message on which reaction was added, will get pinned.
    i.e : with some n different reactions, and some m number of total users reacted on all emojis combined , the message will get pinned
    Functionality of number_of_reactions:
        iterates through all the different reactions on a reacted message, counts and adds number of users reacted on all emojis reacted
        (users can repeat in different reactions, it is intentionally designed to count repeated users)
        reactions won't count if 1 user react with 'n' reactions,
        for any emoji reacted, if users reacted > 1 for that emoji, only then reactions will count towards pinning the message.
        if there are any bot reactions, we will not count them at all

    Functionality of 'Pin message on Reactions' feature :
        doesn't pin if Bot's reaction triggered the condition for pinning,
        pins only if pinSwitch is `True` ,
        number_of_reactions >= react_limit_to_pin
        number_of_diff_reactions >= diff_reaction_limit

        All three attributes `pinSwitch` , `react_limit_to_pin` and `diff_reaction_limit` are extracted from file 'switches&data.json' in '/Data Files/'
        and all of them can be controlled using their respective commands.
    """
    react_limit_to_pin = botFuncs.loadJson(switchesFile)['reactLimit']
    pinSwitch = botFuncs.loadJson(switchesFile)['pinSwitch']
    diff_reaction_limit = botFuncs.loadJson(switchesFile)['diffReactLimit']

    react_channel = client.get_channel(payload.channel_id)
    react_message = await react_channel.fetch_message(payload.message_id)
    number_of_reactions = 0
    number_of_diff_reacions = len(react_message.reactions)

    for reaction in react_message.reactions:
        reaxn_users = await reaction.users().flatten()
        reaxn_users = [user for user in reaxn_users if not user.bot]
        if len(reaxn_users) > 1:
            number_of_reactions += len(reaxn_users)

    # This Condition is explained in docstring of this event function above
    pin_condition = number_of_reactions >= react_limit_to_pin and number_of_diff_reacions >= diff_reaction_limit

    if (not payload.member.bot) and pinSwitch:
    # If reaction is added by a bot, it won't pin the message.
        if pin_condition:
            await react_message.pin(reason=f'Pinned on {payload.member.name}\'s reaction')
            await react_message.add_reaction("📌")


#TODO-false -------------------------------------------------- On Message - Event -------------------------------------------------- #
@client.event
async def on_message(message):
    global bot_prefix
    filterSwitch = botFuncs.loadJson(switchesFile)['filterSwitch']

    # Data to extract from each message
    user = message.author
    fUserName = str(message.author)
    userName = fUserName.split("#")[0]
    fullMsgList = str(message.content).split(" ")
    lowerMsgList = [word.lower() for word in fullMsgList]
    channelName = str(message.channel)

    if message.author == client.user:
        return


    #TODO-false------------------------------------------------ Banned Words Warning -------------------------------------------------#
    banword_aliases = [f'{bot_prefix}banword', f'{bot_prefix}bw']
    if (not fullMsgList[0] in banword_aliases) and filterSwitch:
        # If user is using banword command or filterSwitch is False, then this code won't execute.

        if any(bnword in lowerMsgList for bnword in botData.bannedWords):
            await message.add_reaction("❗")
            await message.channel.send(f"{userName} Watch your language!")


    #TODO-false------- Only Bot-Mods can use these Commands -- Users who are in "/Data Files/modsList.data"
    if fUserName in botData.modsList:

        # Sends the errorsLogFile as discord.File in response
        if fullMsgList[0] == f"{bot_prefix}show-logs":
            fileName = "errorLogs.txt"
            logfile = discord.File(errorsLogFile,fileName)
            await message.channel.send(content=f"`{fileName}` Requested by `{fUserName}`\nFetched at time: `{botFuncs.getDateTime()}`",
                                       file=logfile)
            return
        # Sends errMessageLogFile as discord.File in response
        elif fullMsgList[0] == f"{bot_prefix}show-msglogs":
            fileName = "errorMessages.txt"
            msglogfile = discord.File(errMessageLogFile,fileName)
            await message.channel.send(content =f"`{fileName}` Requested by `{fUserName}`\nFetched at time : `{botFuncs.getDateTime()}`",
                                       file=msglogfile)
            return

    bot_mentions = [
        f"<@!{client.user.id}>", # Mention on PC
        f"<@{client.user.id}>"   # Mention on Mobile
    ]

    if any(mention in fullMsgList for mention in bot_mentions):
        await message.add_reaction("👍")
        await message.channel.send(f"Yes {message.author.mention}, Im up and running!, type `{bot_prefix}help` to know more 🙂")
        return

    # TODO-false------------------------------------------------ Bot-MOD COMMAND >> 'mod' command to add or remove Bot-Moderators ------------------------------------------------#
    # can add , remove Mod to/from modsList | can show the list of Mods
    if fullMsgList[0] == (f'{bot_prefix}mod'):
        if fUserName not in botData.modsList:
            return
        modToAdd = " ".join(fullMsgList[2:])
        try:
            operator_mod = fullMsgList[1]
            if modToAdd.isnumeric():
                try:
                    newBotMod = await client.fetch_user(modToAdd)
                    nameToAdd = str(newBotMod)
                except:
                    await message.channel.send("Can't find any user with given ID.")
                    return
            elif botFuncs.isDiscTag(modToAdd)[0]:
                nameToAdd = botFuncs.isDiscTag(modToAdd)[1]
            elif modToAdd == 'show':
                nameToAdd = fullMsgList[2]
            else:
                raise ValueError

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
                botFuncs.dumpJson(botData.modsList, botFuncs.modListFile)
                modStr = (f'Successfully added `{nameToAdd}` in bot\'s Mod list.')
                await message.add_reaction("✅")

            elif operator_mod == "-" and botFuncs.isDiscTag(nameToAdd):
                if nameToAdd not in botData.modsList:
                    await message.channel.send('Cant remove something which doesn\'nt exist.')
                    return
                botData.modsList.remove(nameToAdd)
                botFuncs.dumpJson(botData.modsList, botFuncs.modListFile)
                modStr = (f'Successfully removed `{nameToAdd}` from bot\'s Mod list.')
                await message.add_reaction("✅")

            await message.channel.send(modStr)
            return

        except:
            modStr = (f'{user.mention}, That\'s not the way to use this command\n'
                      f'correct usage:\n'
                      f'```\n'
                      f'{bot_prefix}mod {{operator}} {{`user#1234`}} | {{user_id}}\n'
                      f'operators:\n'
                      f'+ = add\n- = remove\n'
                      f'to show list of mods, type this:\n'
                      f'{bot_prefix}mod * show\n'
                      f'```')
            await message.channel.send(modStr)
            return

    await client.process_commands(message=message)


#TODO-false ------------------------------- Exception Handling for commands ------------------------------- #
@client.event
async def on_command_error(ctx,error):
    author = ctx.author
    del_after = 10

    if isinstance(error,commands.MissingPermissions):
        await ctx.send(f"{author.mention}, You don't have permissions to use that command!", delete_after=del_after)
    elif isinstance(error,commands.CommandNotFound):
        pseudo_commands = [f"{bot_prefix}snipe"]
        """
        Pseudo Commands , these are command like messages used in `on_message_edit()` and `on_message_delete()` events,
        so if any user uses this pseudo command, then this error handler should ignore it
        """
        if not any(command in ctx.message.content for command in pseudo_commands):
            await ctx.send((f"{author.mention}, There is no such command!\n"
                            f"though you can edit the message and bot will execute if it is a valid command"),
                           delete_after=del_after)
    elif isinstance(error,commands.MemberNotFound):
        await ctx.send(f"{author.mention}, You are supposed to mention a valid Discord user.",delete_after=del_after)
    elif isinstance(error,commands.MissingRequiredArgument):
        await ctx.send(f"{author.mention}, Please provide all the arguments Required for the command.\n", delete_afte=del_after)
    elif isinstance(error,commands.RoleNotFound):
        await ctx.send(f"Can't find a Role with name : `{error.argument}`")
    else:
        channel_name = ctx.channel
        logTime = botFuncs.getDateTime()
        deleteAfter = 2*60 # time in seconds
        owner = client.get_user(client.owner_id)
        await ctx.message.add_reaction("❗")
        try:
            guild_name = ctx.guild.name

            with open(errorsLogFile,"a") as erf:
                erf.write(f"{logTime} --> {error} -- In Guild : \"{guild_name}\" -- Command User : {author}\n")
            with open(errMessageLogFile,"a") as erMsg:
                erMsg.write(f"{logTime} --> {author}: {ctx.message.content} --Guild : \"{guild_name}\" -- Channel: #{channel_name}\n")

            await ctx.send(f"{author.mention}, Either bot doesn't have permission to do the task or you used the command incorrectly\n"
                           f"an error has occurred, Please contact the Bot Dev `{owner}` with this info :\n ```{logTime} --> {error}``` \n"
                           f"This message will be Deleted automatically after {deleteAfter/60} minutes, make sure you copy the error info before this gets deleted", delete_after=deleteAfter)
        except Exception as error_in_handling :
            with open(errorsLogFile, "a") as erf:
                erf.write(f"{logTime} --> {error} -- In Channel : {channel_name} -- Command User : {author}\n")
            with open(errMessageLogFile, "a") as erMsg:
                erMsg.write(f"{logTime} --> {author}: {ctx.message.content}  -- Channel: #{channel_name} --Command User : {author}\n")

            await ctx.send(f"{author.mention}, Either bot doesn't have permission to do the task or you used the command incorrectly\n"
                           f"an error has occurred, Please contact the Bot Dev `{owner}` with this info :\n ```{logTime} --> {error_in_handling}``` \n"
                           f"This message will be Deleted automatically after {deleteAfter/60} minutes, make sure you copy the error info before this gets deleted", delete_after=deleteAfter)
        raise error


#TODO-false ---------------------------------------- Help Commands ---------------------------------------- #
@client.command()
async def help(ctx):
    help_Embed = botData.helpPromt_func(ctx.author,client)
    await ctx.send(embed=help_Embed)


@client.command(aliases = ["mh"])
@commands.has_permissions(manage_guild = True)
async def mod_help(ctx):
    modHelp_Embed = botData.modHlelpPromt_func(ctx.author,client)
    await ctx.send(embed=modHelp_Embed)

#TODO-false ----------------------------------------- MOD COMMANDS -----------------------------------------#

@client.command(aliases = ["bw"])
@commands.has_permissions(manage_guild = True)
async def banword(ctx,*args):
    try:
        operator = args[0]
        banWord = args[1].lower()
        cmdWord = args[1].lower()

        if operator not in operatorList:
            raise ValueError

        if operator == "+":
            if banWord not in botData.bannedWords:
                botData.bannedWords.append(banWord.lower())
                botFuncs.dumpJson(botData.bannedWords, banWordFile)
                banwStr = f'Added {banWord} to banned list.'
                await ctx.message.add_reaction("✅")
            else:
                banwStr = f'{banWord} is already in banned words list.'
        elif operator == "-":
            if banWord in botData.bannedWords:
                botData.bannedWords.remove(banWord)
                botFuncs.dumpJson(botData.bannedWords, banWordFile)
                banwStr = f'Removed {banWord} from the banned words list.'
                await ctx.message.add_reaction("✅")
            else:
                banwStr = f"can't delete something which is not in banned words' list."
        elif operator == "*" and cmdWord == "show":
            banwStr = '```\nList of Banned words:\n'
            i = 1
            for bword in botData.bannedWords:
                banwStr += f'{i}. {bword}\n'
                i += 1
            banwStr += '```'
            await ctx.message.add_reaction("✅")

    except:
        banwStr = (f'{ctx.author.mention}, That\'s not the way to use this command\n'
                   f'correct usage:\n'
                   f'```\n'
                   f'{bot_prefix}banword {{opertaor}} {{word}}\n'
                   f'operator : + , -\n'
                   f'+ to add the word to banned words list\n'
                   f'- to remove the word from banned words list\n'
                   f'Util:\n'
                   f'{bot_prefix}banword * show\n'
                   f'shows all banned words'
                   f'```')
        await ctx.send(banwStr)
        return

    await ctx.send(banwStr)


#TODO-false ---------------------------------------------------------- Switches Group Commands -----------------------------------------------------------------#

@client.group(invoke_without_command=True,aliases=['switches','swt'])
@commands.has_permissions(manage_guild=True)
async def switch(ctx):
    fullDict = botFuncs.loadJson(switchesFile)
    embed = discord.Embed(title="Displaying Switches and data".title(),color=discord.Colour.dark_gold())
    for key,value in fullDict.items():
        embed.add_field(name=f"{key}",value=f"{value}",inline=False)
    embed.set_footer(text=f"Requested by {ctx.author}",icon_url=ctx.author.avatar_url)
    return await ctx.send(embed=embed)

@switch.command(aliases = ['filter','fswitch'])
async def filter_switch(ctx,operator):
    fullDict = botFuncs.loadJson(switchesFile)
    if operator == '+':
        fullDict['filterSwitch'] = True
        botFuncs.dumpJson(fullDict,switchesFile)
        await ctx.send(f'Message scanning for filtered words is Activated!', delete_after = 6)
        await asyncio.sleep(5)
        await ctx.message.delete()
    elif operator == '-':
        fullDict['filterSwitch'] = False
        botFuncs.dumpJson(fullDict,switchesFile)
        await ctx.send(f'Message scanning for filtered words is turned off.', delete_after = 6)
        await asyncio.sleep(5)
        await ctx.message.delete()

@switch.command(aliases = ['pswitch','psw'])
async def p_switch(ctx,operator):
    fullDict = botFuncs.loadJson(switchesFile)
    if operator == '+':
        fullDict['pinSwitch'] = True
        botFuncs.dumpJson(fullDict,switchesFile)
        await ctx.send(f"Bot feature 'Pin on Reactions' Activated!",delete_after = 6)
    elif operator == '-':
        fullDict['pinSwitch'] = False
        botFuncs.dumpJson(fullDict,switchesFile)
        await ctx.send(f"Bot feature 'Pin on Reactions' Deactivated!",delete_after = 6)

@switch.command(aliases=['delsnipe','dsnipe'])
async def del_snipe_switch(ctx,operator):
    fullDict = botFuncs.loadJson(switchesFile)
    if operator == '+':
        fullDict['del_snipe_switch'] = True
        botFuncs.dumpJson(fullDict,switchesFile)
        await ctx.send(f"Bot feature 'Snipe Deleted Message' Activated!",delete_after = 6)
    elif operator == '-':
        fullDict['del_snipe_switch'] = False
        botFuncs.dumpJson(fullDict,switchesFile)
        await ctx.send(f"Bot feature 'Snipe Deleted Message' Deactivated!",delete_after = 6)

@switch.command(aliases=['editsnipe','esnipe'])
async def edit_snipe_switch(ctx,operator):
    fullDict = botFuncs.loadJson(switchesFile)
    if operator == '+':
        fullDict['edit_snipe_switch'] = True
        botFuncs.dumpJson(fullDict,switchesFile)
        await ctx.send(f"Bot feature 'Snipe Edited Message' Activated!",delete_after = 6)
    elif operator == '-':
        fullDict['edit_snipe_switch'] = False
        botFuncs.dumpJson(fullDict,switchesFile)
        await ctx.send(f"Bot feature 'Snipe Edited Message' Deactivated!",delete_after = 6)

@switch.command(aliases = ['reactlimit','rlimit'])
async def reactionsLimit_setter(ctx,limit: int):
    fullDict = botFuncs.loadJson(switchesFile)
    fullDict['reactLimit'] = limit
    botFuncs.dumpJson(fullDict,switchesFile)
    await ctx.send(f"Pin on Reactions : Reaction Limit changed to `{limit} reactions`")

@switch.command(aliases = ['drlimit','diffreact','difflimit'])
async def diffReactionsLimit_setter(ctx,limit:int):
    fullDict = botFuncs.loadJson(switchesFile)
    fullDict['diffReactLimit'] = limit
    botFuncs.dumpJson(fullDict,switchesFile)
    await ctx.send(f"Pin on Reactions : Number of different reactions limit changed to `{limit} Different reactions`")

#Todo-false-------------------------------------------------------- END of Switches Group Commands ---------------------------------------------------------------#

@client.command(aliases = ["p"])
@commands.has_permissions(manage_messages = True)
async def purge(ctx,amount: int = 1 ):
    if amount < 0:
        await ctx.message.add_reaction("❓")
        await ctx.send("Can't delete negative number of messages!", delete_after = 2.5)
    else:
        await ctx.message.delete()
        await ctx.channel.purge(limit=amount)
        await ctx.send(f'Deleted `{amount}` messages',delete_after = 2.5)


@client.command(aliases = ["m"])
@commands.has_permissions(manage_channels = True)
async def mute(ctx,member: discord.Member):
    listOfGuildRoles = ctx.guild.roles
    listMemberRoles = member.roles

    # Getting the position of highest role of -user to be muted-
    highestMemberRole_pos = listMemberRoles[len(listMemberRoles)-1].position

    muted_role = None
    for role in listOfGuildRoles:
        if role.name.lower() == 'muted':
            muted_role = role
            break

    if not muted_role:
        raise commands.RoleNotFound(argument='Muted')

    m_pos = muted_role.position

    # Puts the muted role just above user's highes role , if user's highest role is above muted role
    if m_pos < highestMemberRole_pos:
        await muted_role.edit(position = highestMemberRole_pos)
        await ctx.send("Moved Muted role.")

    await member.add_roles(muted_role)
    await ctx.message.add_reaction("✅")
    await ctx.send(f'{member.mention} was Muted!')


@client.command(aliases = ["unm"])
@commands.has_permissions(manage_channels = True)
async def unmute(ctx,member: discord.Member):
    listOfGuildRoles = ctx.guild.roles

    muted_role = None
    for role in member.roles:
        if role.name.lower() == 'muted':
            muted_role = role
            break

    if not muted_role:
        return await ctx.send(f"{member.name} is not Muted!")

    await member.remove_roles(muted_role)
    await ctx.message.add_reaction("✅")
    await ctx.send(f'{member.mention} was Unmuted!')


@client.command(aliases = ["k"])
@commands.has_permissions(kick_members = True)
async def kick(ctx,member: discord.Member,*,reason = "No Reason Provided"):
    try:
        await member.send(f'You were kicked from `{ctx.guild.name}`, Reason : `{reason}`')
        await member.kick(reason=reason)
        await ctx.send("Sent DM to kicked user", delete_after=5)
    except:
        pass
    await member.kick(reason=reason)
    await ctx.message.add_reaction("✅")
    await ctx.send(f'`{member.name}` was Kicked from `{ctx.guild.name}, Reason = `{reason}`.')


@client.command(aliases = ["b"])
@commands.has_permissions(ban_members = True)
async def ban(ctx,member: discord.Member,*,reason = "No Reason Provided"):
    try:
        await member.send(f'You were banned from `{ctx.guild.name}`, Reason : `{reason}`')
        await member.ban(reason=reason)
        await ctx.send("Sent DM to banned user",delete_after=5)
    except:
        pass
    await member.ban(reason=reason)
    await ctx.message.add_reaction("✅")
    await ctx.send(f'`{member.mention}` was banned from `{ctx.guild.name}, Reason = `{reason}`.')


@client.command(aliases = ["unb"])
@commands.has_permissions(ban_members = True)
async def unban(ctx,*,member):
    member_name,member_disc = member.split("#")
    ban_entriesList = await ctx.guild.bans()

    for ban_entry in ban_entriesList:
        user = ban_entry.user
        if (user.name,user.discriminator) == (member_name,member_disc):
            await ctx.guild.unban(user)
            await ctx.message.add_reaction("✅")
            await ctx.send(f'{user} was Unbanned!')
            return

    await ctx.message.add_reaction("❌")
    await ctx.send(f'{member} not found in this guild\'s banned list.')
    return


@client.command()
@commands.has_permissions(manage_guild=True)
async def pin(ctx):
    ref_message_id =  ctx.message.reference.message_id
    ref_msg = await ctx.channel.fetch_message(ref_message_id)
    if ref_msg.pinned:
        return await ctx.send("Referenced Message is already Pinned!",delete_after=5)
    await ref_msg.pin()
    await ref_msg.add_reaction("📌")
    await ctx.message.add_reaction("✅")


@client.command()
@commands.has_permissions(manage_guild=True)
async def unpin(ctx):
    ref_message_id =  ctx.message.reference.message_id
    ref_msg = await ctx.channel.fetch_message(ref_message_id)
    if ref_msg.pinned:
        await ref_msg.unpin()
    else:
        await ctx.send("Referenced Message is not Pinned.",delete_after=5)
        return
    await ref_msg.remove_reaction("📌",client.user)
    await ctx.message.add_reaction("✅")


@client.command(aliases=['vc','changevc'])
@commands.has_permissions(manage_guild=True)
async def change_voice_channel(ctx,member:discord.Member,*,vcName=None):
    guild_VC_list = ctx.guild.voice_channels
    bot_owner = client.get_user(client.owner_id)

    if member == bot_owner and ctx.author != bot_owner:
        return await ctx.send(f"HAHA Nice try {ctx.author.name}, I am Loyal to my Owner, i won't do that to him. Better Luck next time :wink:")

    try:
        joined_vc = member.voice.channel
    except:
        return await ctx.send(f"{member.name} is currently not in any VC.")

    if not vcName:
        await member.edit(voice_channel=vcName)
        return await ctx.send(f"{member.name} was Disconnected from `{joined_vc.name}` ")

    for vc in guild_VC_list:
        if vc.name.lower() == vcName.lower():
            voice_channel = vc
            await member.edit(voice_channel=voice_channel)
            return await ctx.send(f"{member.name} was moved from `{joined_vc.name}` to `{voice_channel.name}`")

    return await ctx.send(f"Voice Channel with name `{vcName}` Not found.")

#todo-false ----------------------------------------------- Role Command Group -----------------------------------------------------------#

@client.group(invoke_without_command=True,aliases=['roles'])
@commands.has_permissions(manage_roles=True)
async def role(ctx):
    await ctx.send("Command Usage:\n"
                   f"`{bot_prefix}role (add|remove) (user) (role)`")

@role.command(aliases=['+'])
async def add(ctx,member:discord.Member,*,grole:discord.Role):
    await member.add_roles(grole)
    await ctx.send(f"Given `{grole.name}` Role to `{member}`")

@role.command(aliases=['-'])
async def remove(ctx,member:discord.Member,*,trole:discord.Role):
    await member.remove_roles(trole)
    await ctx.send(f"Taken `{trole.name}` Role from `{member}`")

@role.command(aliases=['*'])
async def show(ctx,member:discord.Member):

    embed = discord.Embed(title=f"{member.name} Roles List",color=discord.Colour.dark_gold())
    embed.set_thumbnail(url=member.avatar_url)
    mentionable_roles = []
    nonMentionable_roles = []

    for role in member.roles:
        if role.name == "@everyone":
            embed.add_field(name="Default Role",value=f"{role.name}")
        elif role.mentionable:
            mentionable_roles.append(f"{role.mention}")
        else:
            nonMentionable_roles.append(f"{role.mention}")

    if len(mentionable_roles)>0:
        mentionable_roles = mentionable_roles[::-1]
        mentioables = "\n".join(mentionable_roles)
        embed.add_field(name="Mentionable Roles:",value=mentioables,inline=False)
    if len(nonMentionable_roles)>0:
        nonMentionable_roles = nonMentionable_roles[::-1]
        non_mentionables = "\n".join(nonMentionable_roles)
        embed.add_field(name="Non-Mentionable Roles:",value=non_mentionables,inline=False)

    embed.set_footer(text=f"Requested by {ctx.author}",icon_url=ctx.author.avatar_url)
    await ctx.send(embed=embed)

#todo-false --------------------------------------------- END of Role Command Group ------------------------------------------------------#

#TODO-false ------------------------------------------- Commands For Users ------------------------------------------------#
#TODO-false ------------------------------------------- Utility Commands --------------------------------------------------#
@client.command(aliases = ['ref'])
async def regfind(ctx,emailORdisctag,operator,*,text):

    toFind = emailORdisctag.lower()
    operator_present = operator == "--"
    find_in = text
    command_ok = toFind == "email" or toFind == "disctag"
    try:
        if command_ok and operator_present:
            if toFind == "email":
                matches = re.findall(r'[\w%./-]+@[a-zA-Z0-9]+[-]*[a-zA-Z0-9]*\.com', find_in)
                toFind = "Email"
            elif toFind == "disctag":
                matches = re.findall(r'[\w%!.&*-]+#\d{4}',find_in)
                toFind = "Discord Tag"

            regResponseStr = (f'```\n{len(matches)} Possible {toFind} matches were extracted from the given text.\n')
            i = 1
            for match in matches:
                regResponseStr += f'{toFind}-{i} : {match}\n'
                i += 1
            regResponseStr += '```'
        else:
            raise ValueError
        await ctx.send(regResponseStr)
    except:
        regResponseStr = ('Incorrect usage of command `regfind`\n'
                          f'{ctx.author.name}, correct usage is:\n'
                          f'```\n'
                          f'{bot_prefix}regfind {{email | disctag}} -- {{Your text here}}\n'
                          f'\nUsage:\n'
                          f'| --> or\n'
                          '{} exclude the brackets\n'
                          '```')


@client.command(aliases = ['gif'])
async def tenorgif(ctx,*,category):
    """
    Gets a Random GIF from tenor, in a requested Category
    """
    gifsList = botFuncs.getTenorList(category)
    embed = discord.Embed(title=f"Random GIF from '{category.title()}' Category.", color= discord.Colour.gold())
    via_tenor_URL = 'https://www.gstatic.com/tenor/web/attribution/PB_tenor_logo_blue_vertical.png'
    embed.set_image(url = random.choice(gifsList))
    embed.set_thumbnail(url = via_tenor_URL)
    author_name = str(ctx.author)
    embed.set_footer(text=f'Requested by {author_name}.', icon_url= ctx.author.avatar_url)
    await ctx.send(embed = embed)


@client.command(aliases = ['pfp','pic'])
async def avatar(ctx,member: discord.Member = None):
    member = ctx.author if not member else member

    author_tag = str(ctx.author)
    embed = discord.Embed(description=f'**{member.mention}\'s Avatar**',color=discord.Colour.dark_gold())
    embed.set_image(url=member.avatar_url)
    embed.set_footer(text=f'Requested by {author_tag}.', icon_url=ctx.author.avatar_url)

    await ctx.send(embed=embed)


@client.command()
async def code(ctx,format,*,code):
    randStr = f"{botFuncs.genRand()}{botFuncs.genRand()}"
    tempFileName = f'tempfile{randStr}code.txt'
    with open(tempFileName,"w") as f:
        f.write(code)

    with open(tempFileName, "rb") as ft:
        codeFile = discord.File(ft,f'{ctx.author.name}Code.{format}')
        await ctx.send(file=codeFile)

    os.remove(os.path.join(os.getcwd(),tempFileName))


@client.command(aliases=['r'])
async def react(ctx,emoji):
    ref_message_id =  ctx.message.reference.message_id
    ref_msg = await ctx.channel.fetch_message(ref_message_id)

    try: # For default Emojis (Unicode characters) and Guild image emojis
        await ref_msg.add_reaction(emoji)
        await ctx.message.add_reaction("✅")
    except: # For Guild Emojis which are Animated
        for g_emoji in ctx.guild.emojis:
            if g_emoji.name.lower() == emoji.lower():
                r_emoji = g_emoji
                await ref_msg.add_reaction(r_emoji)
                await ctx.message.add_reaction("✅")
                return
        await ctx.send("Emoji Not Found.")

    await asyncio.sleep(4)
    await ctx.message.delete()


@client.command(aliases=['activ'])
async def activity(ctx, member: discord.Member = None):
    member = ctx.author if not member else member
    try:
        activT = member.activity
        if str(activT) == "Spotify":
            spotify = member.activity

            started_song_at = str(spotify.created_at.strftime("%d-%m-%Y %H:%M:%S")).split(".")[0]
            song_name = spotify.title
            song_total_duration = str(spotify.duration)[:-3]
            artistsList = spotify.artists
            artists = ", ".join(artistsList)
            album = spotify.album
            song_id = spotify.track_id
            song_duration = str(datetime.now() - spotify.created_at).split(".")[0]
            album_url = spotify.album_cover_url

            embed = discord.Embed(title=f"{member.name}'s Spotify Session", color=discord.Colour.dark_gold())
            embed.add_field(name="Current Song Started at (Time Zone UTC)", value=f"`{started_song_at}`", inline=False)
            embed.add_field(name="Song Time Stamp Now", value=song_duration, inline=False)
            embed.add_field(name="Song Name", value=song_name, inline=True)
            embed.add_field(name="Song Duration", value=song_total_duration, inline=True)
            embed.add_field(name="Song Artist(s)", value=artists, inline=False)
            embed.add_field(name="Album Name", value=album, inline=False)
            embed.add_field(name="Song ID on Spotify", value=song_id, inline=False)
            embed.set_thumbnail(url=album_url)

            author_name = str(ctx.author)
            embed.set_footer(text=f'Requested by {author_name}.', icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
        else:
            activT_type = botFuncs.capFistChar(str(activT.type).split('.')[1])
            activT_application = botFuncs.capFistChar(activT.name)
            activT_duration = str(datetime.now() - activT.created_at).split(".")[0]

            embed = discord.Embed(title=f"{member.name}'s Activity:", color=discord.Colour.dark_gold())
            try:
                acttivT_url = activT.large_image_url
                if acttivT_url:
                    embed.set_thumbnail(url=acttivT_url)
                else:
                    embed.set_thumbnail(url=member.avatar_url)
            except:
                pass
            embed.add_field(name="Activity Type", value=f"{activT_type}", inline=False)
            embed.add_field(name="Application", value=f"{activT_application}", inline=False)
            embed.add_field(name="Duration",value=activT_duration,inline=False)
            try:
                activT_details = botFuncs.capFistChar(str(activT.details))
                if activT_details:
                    embed.add_field(name="Details", value=f"{activT_details}", inline=False)
            except:
                pass
            author_name = str(ctx.author)
            embed.set_footer(text=f'Requested by {author_name}.', icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)

    except:
        await ctx.send(f"Apparently, {member.name} is not doing any activity right now.")


@client.command(aliases=['nick'])
@commands.has_permissions(change_nickname=True)
async def set_nick(ctx,member:discord.Member,*,newNick=None):
    await member.edit(nick=newNick)
    await ctx.message.add_reaction("✅")


#TODO-false ----------------------------------------------- Fun Commands --------------------------------------------------#

@client.command(aliases = ['fax'])
async def funfax(ctx,thing,*,quality):
    await ctx.message.add_reaction("👀")
    await ctx.send(f'{thing} is {botFuncs.genRand()}% {quality}!')


@client.command(aliases = ['say'])
async def sneak(ctx,*,messageTosay):
    await ctx.message.delete()
    await ctx.send(messageTosay)


@client.command(aliases = ['sus', 'amoggus'])
async def suspicious(ctx,member: discord.Member = None):
    member = ctx.author if not member else member

    susStr = random.choice(botData.susList)
    await ctx.message.add_reaction("🤨")
    await ctx.send(f'{member.mention} {susStr}')


@client.command(aliases = ["platform"])
async def device(ctx,member:discord.Member = None):
    member = ctx.author if not member else member

    if member.is_on_mobile():
        await ctx.send(f'{member.mention} is a Cringe mobile user lol.')
        for reaxn in botData.reactionsList:
            await ctx.message.add_reaction(reaxn)
    else:
        await ctx.message.add_reaction("🙌")
        await ctx.send(f'{member.mention} is a Chad PCMR member , **RESPECT!!**')


@client.command(aliases = ["dm"])
async def direct_anonymous(ctx,member:discord.Member,*,message):
    user = member
    await user.send(message)
    await ctx.send("Successfully sent.")


@client.command(aliases = ['dmid'])
async def dm_withID(ctx,memberID:int,*,message):
    user = await client.fetch_user(memberID)
    await user.send(message)
    await ctx.send("Successfully sent.")

#-------------------------------------------------------------------------------------------------------------------#
BOT_TOKEN = os.environ['BOT_TOKEN']

client.run(BOT_TOKEN)
