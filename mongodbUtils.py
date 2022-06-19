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
        guild_coll = db['guild_info']
        doc = guild_coll.find_one({"guild_id": message.guild.id})
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
    guild_coll = db['guild_info']
    guild_dict = {
        "guild_id" : guild.id,
        "guild_name" : str(guild.name),
        "prefix" : botData.default_bot_prefix
    }

    # Initialising default switches data dump in data base for the guild
    guild_dict.update(botFuncs.loadJson(botData.switchesFile))


    # Initializing default banned words data dump in data base for the guild
    guild_dict['banned_words'] = botFuncs.loadJson(botData.banWordFile)

    # Initializing Custom commands Doc for guild in 'guild_custom_commands'
    guild_dict['custom_commands'] = []
    guild_coll.replace_one(filter={"guild_id":guild.id},
                           replacement=guild_dict,
                           upsert=True)

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
    # Clearing from collection - guild_prefixes
    guilds_coll = db['guild_info']

    del_count = guilds_coll.delete_one(filter={"guild_id": guild.id})
    # Logging the info
    if del_count!=0:
        log_string = (f"[{botFuncs.getDateTime()}] --> Left guild : {guild.name} , ID : {guild.id}\n\t"
                      f"Deleted all the Guild's data from Data Base")
        botFuncs.log_func(log_string=log_string,
                          file_name=botData.guild_removed_EventLogFile)
    else:
        botFuncs.log_func(log_string=f"[{botFuncs.getDateTime()}] --> Left guild : {guild.name} , ID : {guild.id} \n\t"
                                     f"There was something Unusual when clearing data from Data Base",
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
        
        guild_info:
        {
            '_id': ObjectId('611e473c927fcd303a681c8d'),
            "guild_id": 182374298347298349,
            "banned_words": [
                "some",
                "banned",
                "words",
                "here"
            ],
            "custom_commands": [
                {
                    "user_id": 259723423144136202,
                    "user_tag": "user#0000",
                    "command": "command word here",
                    "response": "command response here",
                    "need_prefix": false,
                    "time_stamp": "23-02-2022 11:42:18"
                },
                {
                    "user_id": 2523423423444136202,
                    "user_tag": "user#0000",
                    "command": "command word here2",
                    "response": "command response here2",
                    "need_prefix": true,
                    "time_stamp": "23-02-2022 11:44:21"
                }
            ],
            "del_snipe_switch": true,
            "diffReactLimit": 3,
            "edit_snipe_switch": true,
            "filterSwitch": true,
            "guild_name": "guild name here",
            "pinSwitch": true,
            "prefix": ">",
            "reactLimit": 7,
            "join-leave": {
                "channel_id": 988062343434720219,
                "join": "Hurray {user} joined {server}",
                "leave": "{user} left {server}"
            }
        }
        
        Note: In above Collection 'guild_info', 'join-leave' is optional from server to server. for some servers it might not exist. if tried to access it might give KeyError.
        
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