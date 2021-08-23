import os
import pymongo
import discord
from discord.ext import commands
from dotenv import load_dotenv
import botFuncs
import botData

# -------------------- #
load_dotenv()
# -------------------- #
mongo_user = os.environ['MONGO_USER']
mongo_password = os.environ['MONGO_PASSWORD']

mongo_client = pymongo.MongoClient(f"mongodb+srv://{mongo_user}:{mongo_password}@cluster0.xro3b.mongodb.net/PythonicDB?retryWrites=true&w=majority")
db = mongo_client['PythonicDB']


#todo-false : Whole structure of Data Base is at bottom of this file


def get_prefix(client, message:discord.Message):
    try:
        prefix_collection = db['guild_prefixes']
        doc = prefix_collection.find_one({"guild_id": message.guild.id})
        local_prefix = doc['prefix']
        return local_prefix
    except AttributeError:
        """If commands are used in dm , only default bot prefix can be used"""
        return botData.default_bot_prefix


def get_local_prefix(message:discord.Message):
    return get_prefix(client="x",message=message)


def add_dev(user:discord.User):
    dev_dict = {
        "user_id" : user.id,
        "user_tag" : str(user),
        "added_on" : botFuncs.getDateTime()
    }
    bot_devs_collection = db["bot_devs"]
    bot_devs_collection.insert_one(document=dev_dict)
    botFuncs.log_func(log_string=f"[{botFuncs.getDateTime()}] --> Added [{user}] in bot_devs collection in Data Base.",
                      file_name=botData.devs_update_EventLogFile,
                      newlines=1)


def remove_dev(user:discord.User):
    bot_devs_collection = db["bot_devs"]
    bot_devs_collection.delete_one(filter={"user_id" : user.id})
    botFuncs.log_func(log_string=f"[{botFuncs.getDateTime()}] --> Removed [{user}] from bot_devs collection in Data Base.",
                      file_name=botData.devs_update_EventLogFile,
                      newlines=1)


def is_dev(ctx:commands.Context):
    bot_devs_collection = db["bot_devs"]
    find_dev = bot_devs_collection.find_one(filter={"user_id": ctx.author.id})
    return False if not find_dev else True


def is_custom_command_opted(ctx:commands.Context):
    """This function is to be used as 'check' in commands.check()"""
    user_cmd_coll = db['user_custom_commands']
    user_doc = user_cmd_coll.find_one(filter={"user_id":ctx.author.id})
    return False if not user_doc else True


def is_user_custom_opted(user:discord.User):
    """
    This function is to be used anywhere in code where we want to check if the user is opted in for user custom commands
    DO NOT USE THIS FUNCTION IN `commands.check()`
    """
    user_cmd_coll = db['user_custom_commands']
    user_doc = user_cmd_coll.find_one(filter={"user_id":user.id})
    opted =  False if not user_doc else True
    return (opted,user_doc)


def init_guild_join_settings(guild:discord.Guild):
    """
    This function will be used in on_guild_join(guild) event ,
    this will create documents in data base collections which are server specific
    data is later used in commands and other events like, on_raw_reaction_add , on_message_edit , on_message_delete etc..
    """
    # Initialising default prefix dump in data base for the guild
    prefix_collection = db['guild_prefixes']
    prefix_dict = {
        "guild_id" : guild.id,
        "guild_name" : str(guild.name),
        "prefix" : botData.default_bot_prefix
    }
    prefix_collection.replace_one(filter={"guild_id": guild.id},
                                 replacement=prefix_dict,
                                 upsert=True
                                 )

    # Initialising default switches data dump in data base for the guild
    switches_collection = db['guild_switches']
    switches_dict = botFuncs.loadJson(botData.switchesFile)
    switches_dict.update({
        "guild_id": guild.id,
        "guild_name": str(guild.name)
    })
    switches_collection.replace_one(filter={"guild_id": guild.id},
                                    replacement=switches_dict,
                                    upsert=True
                                    )

    # Initializing default banned words data dump in data base for the guild
    banword_collection = db['guild_bannedwords']
    banword_list = botFuncs.loadJson(botData.banWordFile)
    banword_dict = {
        "guild_id" : guild.id,
        "guild_name": str(guild.name),
        "banned_words" : banword_list
    }
    banword_collection.replace_one(filter={"guild_id": guild.id},
                                   replacement=banword_dict,
                                   upsert=True
                                   )

    # Initializing Custom commands Doc for guild in 'guild_custom_commands'
    guild_cmd_coll = db['guild_custom_commands']
    custom_commands = []
    cmd_doc_dict = {
        "guild_id" : guild.id,
        "guild_name" : guild.name,
        "custom_commands" : custom_commands
    }
    guild_cmd_coll.replace_one(filter={"guild_id":guild.id},
                               replacement=cmd_doc_dict,
                               upsert=True
                               )

    # Logging the info
    log_string = (f"[{botFuncs.getDateTime()}] --> Joined guild : {guild.name} , ID : {guild.id}\n\t"
                  f"Initialized all the default settings - Initialized the Data on Data Base")
    botFuncs.log_func(log_string=log_string,
                      file_name=botData.guild_joined_EventLogFile)


def init_guild_remove_settings(guild:discord.Guild):
    """
    This function is used in on_guild_remove(guild) event,
    this will clear the data associated with the guild - from Data Base , because we don't want to store cached data
    main pupose is to save memory on Data base
    """
    overall_del_count = []
    # Clearing from collection - guild_prefixes
    prefixes_collection = db['guild_prefixes']
    pfx_del = prefixes_collection.delete_one(filter={"guild_id": guild.id})
    overall_del_count.append(pfx_del.deleted_count)

    # Clearing from collection - guild_switches
    switches_collection = db['guild_switches']
    switch_del = switches_collection.delete_one(filter={"guild_id": guild.id})
    overall_del_count.append(switch_del.deleted_count)

    # Clearing from collection - guild_bannedwords
    bannedwords_collection = db['guild_bannedwords']
    banw_del = bannedwords_collection.delete_one(filter={"guild_id": guild.id})
    overall_del_count.append(banw_del.deleted_count)

    # Clearing from collection = guild_custom_commands
    guild_cmd_coll = db['guild_custom_commands']
    custom_cmd_del = guild_cmd_coll.delete_one(filter={"guild_id": guild.id})
    overall_del_count.append(custom_cmd_del.deleted_count)

    total_del_count = 0
    for each_count in overall_del_count:
        total_del_count += each_count

    successfully_deleted : bool = total_del_count == len(overall_del_count)
    # Logging the info
    if successfully_deleted:
        log_string = (f"[{botFuncs.getDateTime()}] --> Left guild : {guild.name} , ID : {guild.id}\n\t"
                      f"Deleted all the Guild's cache from Data Base")
        botFuncs.log_func(log_string=log_string,
                          file_name=botData.guild_removed_EventLogFile)
    else:
        botFuncs.log_func(log_string=f"[{botFuncs.getDateTime()}] --> Left guild : {guild.name} , ID : {guild.id} \n\t"
                                     f"There was something Unusual when clearing cache from Data Base",
                          file_name=botData.guild_removed_EventLogFile)


"""
my MongoDB Data Base Structure:
    db : PythonicDB

        collections:
            bot_devs,
            guild_prefixes,
            guild_switches,
            guild_bannedwords,
            guild_custom_commands,
            user_custom_commands
            
        ** Each Dictionary below represents a single document for each collection in Data Base **

        bot_devs:
        {
            '_id': ObjectId('611e473c927fcd303a681c8d'),
            'added_on': '19-08-2021 11:57:48',
            'user_id': 259708868144136202,
            'user_tag': 'Uranium#4939'
        }

        guild_prefixes:
        {
            '_id': ObjectId('611e09b40c50cda36da35124'),
            'guild_id': 733370530039857232,
            'guild_name': 'STRUGGLES OF NOOB',
            'prefix': '>'
        }

        guild_switches:
        {   
            '_id': ObjectId('611e09b50c50cda36da35140'),
            'del_snipe_switch': True,
            'diffReactLimit': 3,
            'edit_snipe_switch': True,
            'filterSwitch': False,
            'guild_id': 733370530039857232,
            'guild_name': 'STRUGGLES OF NOOB',
            'pinSwitch': True,
            'reactLimit': 7
        }

        guild_bannedwords:
        {
            '_id': ObjectId('611e09b50c50cda36da3515f'),
            'banned_words': [
                                'some',
                                'banned',
                                'words',
                                'here'
                            ],
            'guild_id': 733370530039857232,
            'guild_name': 'STRUGGLES OF NOOB'}
        }

        guild_custom_commands :
        {
            '_id': ObjectId('611e473c927fcd303a681c8d'),
            'guild_id' : 00000000000000000,
            'guild_name' : 'guild name',
            'custom_commands' : [
                                    {
                                        user_id : u0000000000,
                                        user_tag : <discord tag of user who made command>,
                                        command : <name of command>,
                                        response : <response string to send for the command>,
                                        need_prefix : true,
                                        time_stamp : <time at which command was added>
                                    },
                                    {
                                        user_id : u0000000111,
                                        user_tag : <discord tag of user who made command>,
                                        command : <name of command2>,
                                        response : <response string to send for the command2>,
                                        need_prefix : false,
                                        time_stamp : <time at which command2 was added>
                                    }
                                ]
        }

        user_custom_commands:
        {
            '_id': ObjectId('611e473c927fcd303a681c8d'),
            'user_id' : 000000000000001,
            'user_tag' : <discord tag of user who made command>,
            'custom_commands' : [
                                    {
                                        command : <name of command>,
                                        response : <response string to send for the command>,
                                        need_prefix : true,
                                        time_stamp : <time at which command was added>
                                    },
                                    {
                                        command : <name of command>,
                                        response : <response string to send for the command>,
                                        need_prefix : false,
                                        time_stamp : <time at which command was added>
                                    }
                                ]
        }

"""