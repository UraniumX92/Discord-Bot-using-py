import discord
import asyncio
import os
from discord.ext import commands
from datetime import datetime
#-------------------------------------------------- My Files - Imports --------------------------------------------------#
import mongodbUtils
from mongodbUtils import get_prefix
import botFuncs
import botData
import asyncUtils
from asyncUtils import change_presence
#---------------------------------------- To get ENVIRONMENT variables from .env ----------------------------------------#
import dotenv
dotenv.load_dotenv()
#------------------------------------------------------------------------------------------------------------------------#
default_bot_prefix = "$"
operatorList = ["+","-","*"] # --> List of operators used in different commands to add , remove and show respectively
#------------------------------------------------------------------------------------------------------------------------#

owner_id = int(os.environ['MY_DISCORD_USER_ID'])

client_activity = discord.Activity(
    type=discord.ActivityType.listening,
    name=" your Commands 🙂",
    start=datetime.utcnow()
)

client = commands.Bot(
    command_prefix=get_prefix,
    help_command=None,
    activity=client_activity,
    owner_id=owner_id,
    intents=discord.Intents.all(),
    case_insensitive=True
)

botFuncs.load_cogs(client)

#  -------------------------------------------------- On Ready - Event -------------------------------------------------- #
@client.event
async def on_ready():
    global owner_id
    owner = client.get_user(owner_id)
    bot_devs_collection = mongodbUtils.db['bot_devs']
    owner_added = bot_devs_collection.find_one(filter={"user_id" : (owner_id)})
    if not owner_added:
        dev_dict = {
            "user_id" : (owner_id),
            "user_tag" : str(owner),
            "added_on" : botFuncs.getDateTime()
        }
        bot_devs_collection.insert_one(document=dev_dict)
        print(f"Added {owner} in Data Base")
        botFuncs.log_func(log_string=f"[{botFuncs.getDateTime()}] --> Added {owner} in bot_devs collection in Data Base.",
                          file_name=botData.devs_update_EventLogFile)
    else:
        print(f"Bot owner : {owner}  is Present in DataBase 'bot_devs'")

    print(f'{client.user} is online on discord.py version : {discord.__version__}')
    print(f"Bot went online on : [{botFuncs.getDateTime()}]")


#  -------------------------------------------------- On Guild Join and Leave - Events -------------------------------------------------- #
@client.event
async def on_guild_join(guild:discord.Guild):
    mongodbUtils.init_guild_join_settings(guild)

@client.event
async def on_guild_remove(guild:discord.Guild):
    mongodbUtils.init_guild_remove_settings(guild)

#  -------------------------------------------------- On Message Delete - Event -------------------------------------------------- #
@client.event
async def on_message_delete(message):
    bot_prefix = mongodbUtils.get_local_prefix(message)
    def check(msg:discord.Message):
        return msg.channel.id == message.channel.id
    try:
        switches_collection = mongodbUtils.db["guild_switches"]
        local_switches = switches_collection.find_one({"guild_id": (message.guild.id)}, {"_id": 0, "guild_id": 0, "guild_name": 0})
        delSwitch = local_switches['del_snipe_switch']
    except AttributeError:
        return

    try:
        respMsg = await client.wait_for(event='message',check=check,timeout=60)
    except asyncio.TimeoutError:
        pass
    else:
        if respMsg.content == f"{bot_prefix}snipe" and delSwitch:
            del_msg_author = message.author
            embed = discord.Embed(title=f"{del_msg_author}'s Message Delete Snipe",description=f"{del_msg_author}: {message.content}",color=discord.Colour.dark_gold())
            return await respMsg.channel.send(embed=embed,
                                              reference=respMsg,
                                              mention_author=False)


#  -------------------------------------------------- On Message Edit - Event -------------------------------------------------- #
@client.event
async def on_message_edit(before,after):
    bot_prefix = mongodbUtils.get_local_prefix(after)
    def check(msg:discord.Message):
        return msg.channel.id == after.channel.id
    try:
        switches_collection = mongodbUtils.db["guild_switches"]
        local_switches = switches_collection.find_one({"guild_id": (after.guild.id)}, {"_id": 0, "guild_id": 0, "guild_name": 0})
        editSwitch = local_switches['edit_snipe_switch']
    except AttributeError:
        return

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
            return await respMsg.channel.send(embed=embed,
                                              reference=respMsg,
                                              mention_author=False)


#  -------------------------------------------------- On Raw Reaction Add - Event -------------------------------------------------- #
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
    try:
        switches_collection = mongodbUtils.db["guild_switches"]
        local_switches = switches_collection.find_one({"guild_id": payload.guild_id}, {"_id": 0, "guild_id": 0, "guild_name": 0})

        react_limit_to_pin = local_switches['reactLimit']
        pinSwitch = local_switches['pinSwitch']
        diff_reaction_limit = local_switches['diffReactLimit']
    except AttributeError:
        return

    try:
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
                await react_message.pin(reason=f"Pinned on {payload.member.name}'s reaction")
                await react_message.add_reaction("📌")
    except AttributeError:
        """If reaction is added in DM , then there will be no discord.Member attribute and no discord.TextChannel, so we silently handle the error"""
        pass


#  -------------------------------------------------- On Message - Event -------------------------------------------------- #
@client.event
async def on_message(message):
    global default_bot_prefix
    bot_prefix = mongodbUtils.get_local_prefix(message)

    if message.author == client.user:
        return

    try:
        switches_collection = mongodbUtils.db["guild_switches"]
        local_switches = switches_collection.find_one({"guild_id": message.guild.id}, {"_id": 0, "guild_id": 0, "guild_name": 0})
        filterSwitch = local_switches['filterSwitch']
    except AttributeError:
        filterSwitch = False

    # Listening for user exclusive commands
    responded_to_user_command = await asyncUtils.user_commands_listener(message)
    if responded_to_user_command:
        return

    # Listening for guild custom commands
    responded_to_guild_command = await asyncUtils.guild_command_listener(message)
    if responded_to_guild_command:
        return

    # Data to extract from each message
    user = message.author
    fUserName = str(message.author)
    userName = message.author.name
    fullMsgList = str(message.content).split(" ")
    lowerMsgList = [word.lower() for word in fullMsgList]
    channelName = str(message.channel)

    bot_mentions = [
        f"<@!{client.user.id}>", # Mention on PC
        f"<@{client.user.id}>"   # Mention on Mobile
    ]

    #  ------------------------------------- Reset bot prefix for guild ------------------------------------------------ #
    if any(mention in fullMsgList[0] for mention in bot_mentions) and " ".join(fullMsgList[1:]) == "reset prefix":
        prefix_collection = mongodbUtils.db['guild_prefixes']
        prefix_collection.update_one(filter={"guild_id": message.guild.id},
                                     update={"$set": {"prefix": str(default_bot_prefix)}})
        return await message.channel.send(f"Succesfully set `{default_bot_prefix}` as prefix for this guild!",
                                          reference=message,
                                          mention_author=False)

    # ------------------------------------------------ Banned Words Warning -------------------------------------------------#
    banword_aliases = [f'{bot_prefix}banwords', f'{bot_prefix}bw', f'{bot_prefix}banword']
    if (not fullMsgList[0] in banword_aliases) and filterSwitch:
        # If user is using banword command or filterSwitch is False, then this code won't execute.

        if any(bnword in lowerMsgList for bnword in botData.bannedWords):
            await message.add_reaction("❗")
            await message.channel.send(f"{userName} Watch your language!",
                                       reference=message,
                                       mention_author=True)

    if any(mention in fullMsgList[0] for mention in bot_mentions):
        await message.add_reaction("👍")
        return await message.channel.send(f"Hey {userName}, Im up and running! type `{bot_prefix}help` to know my commands 🙂",
                                          reference=message,
                                          mention_author=True)

    await client.process_commands(message=message)


#  ------------------------------- Exception Handler for commands ------------------------------- #
@client.event
async def on_command_error(ctx,error):
    """
    This error handler only handles selected errors,
    Other errors are handled in their respective cog classes in `cog_command_error()` function
    """
    bot_prefix = mongodbUtils.get_local_prefix(ctx.message)
    author = ctx.author
    del_after = 10

    if isinstance(error,commands.CommandNotFound):
        pseudo_commands = [f"{bot_prefix}snipe"]
        """
        Pseudo Commands , these are command like messages used in `on_message_edit()` and `on_message_delete()` events,
        so if any user uses this pseudo command, then this error handler ignores it
        """
        if not any(command in ctx.message.content for command in pseudo_commands):
            await ctx.send((f"{author.mention}, There is no such command!\n"
                            f"though you can edit the message and bot will execute if it is a valid command"),
                           delete_after=del_after)


#-------------------------------------------------------------------------------------------------------------------#
BOT_TOKEN = os.environ['BOT_TOKEN']

client.loop.create_task(change_presence(client=client))
client.run(BOT_TOKEN)