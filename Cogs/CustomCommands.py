import discord
from discord.ext import commands

import asyncUtils
import botFuncs
import botData
import mongodbUtils
from asyncUtils import log_and_raise
import asyncio
import os
from datetime import datetime
from typing import Union


class CustomGroup(commands.Cog):
    def __init__(self,client):
        self.client:commands.Bot = client
        self.owner_id = botData.owner_id
        self.db = mongodbUtils.db


    @commands.group(name="custom",invoke_without_command=True)
    async def custom_main(self,ctx):
        """
        Shows the ways to use this command, similar to help command
        """
        em_title = "Directions to create custom commands for server and for user".title()
        em_description = ("There are Basically 2 types of custom commands\n"
                          "1. Which Requires bot prefix to be used\n"
                          "2. Which doesn't require bot prefix to be used\n"
                          "And again, there are 2 categories in custom commands\n"
                          "1. Custom commands for server : These can be used by anyone in server\n"
                          "2. User exclusive commands : These can only be used by the user who created the command and can be used in any server where this bot is present\n"
                          
                          "Now let's see how to use some commands to create your desired type of custom command in your desired Category\n"
                          ">>> Notes:\n\t- In below examples we are gonna use bot's default prefix '$' as example , but you have to use your server's prefix while using command.\n"
                          "\t- For user exclusive commands, user must first opt in to create user exclusive commands\n"
                          "\t- Similarly user can opt out from user exclusive commands, but all their commands data will be gone once they opt out.\n")

        optin_optout =  ("`$custom optin` --> *opts in user for user exclusive commands*\n"
                        "`$custom optout` --> *opts user out from user exclusive commands*\n")

        show_cmds = ("`$custom server` --> *shows the list of custom commands which requires prefix for your server*\n"
                     "`$custom server (noprefix | nopre)` --> *shows the list of custom commands which doesn't require prefix for your server*\n"
                     "`$custom self` --> *shows the list of user's exclusive custom commands which requires prefix*\n"
                     "`$custom self (noprefix | nopre)` --> *shows the list of user's exclusive custom commands which doesn't require prefix*\n")

        server_cmds = ("`$custom (add | +) <command_name> <command_response>`\n --> *adds a custom command for your server which requires prefix to be used*\n"
                       "`$custom (add.nopre | +nopre) <command_name> <command_response>`\n --> *adds a custom command for your server which doesn't require prefix to be used*\n"
                       "`$custom (remove | -) <command_name>`\n --> *removes the custom command from server's custom commands, only server mods or command authors can delete these commands*\n")

        user_cmds = ("`$custom (addself | s+) <command_name> <command_response>`\n --> *adds an exclusive custom command for user which requires prefix to be used*\n"
                     "`$custom (addself.nopre | s+nopre) <command_name> <command_response>`\n --> *adds an exclusive custom command for user which doesn't require prefix to be used*\n"
                     "`$custom (removeself | s-) <command_name>`\n --> *removes the command from user's custom command*\n")

        str_imp_note = (">>> -- Exclude the brackets `()`,`<>`\n"
                        "-- `'|'` This means `'or'`, for example (add | +) means , you can either user `add` or `+` , both will trigger the same command\n"
                        "-- Your command name must not contain any spaces, or else bot will take first word as command name and rest of the words as command response\n"
                        "-- If a user and server are having a custom command with same name, then user's command is given priority and server's command is ignored in this case\n"
                        "-- There is no limitation on command response text, except the limitation which discord has ***2000 character limit*** for a message.\n"
                        "-- Make sure your custom command names are not colliding with the actual command names and aliases of bot commands, Be creative and keep unique names for your custom commands :slight_smile:")


        embed = discord.Embed(title=em_title,description=em_description,colour=discord.Colour.dark_gold())
        embed.add_field(name="Commands to show the Custom Commands:",value=show_cmds,inline=False)
        embed.add_field(name="Commands for Server:",value=server_cmds,inline=False)
        embed.add_field(name="Commands to opt in / opt out:",value=optin_optout,inline=False)
        embed.add_field(name="Commands for Users:",value=user_cmds,inline=False)
        embed.add_field(name="\nImportant Note:",value=str_imp_note,inline=False)
        embed.set_footer(text=f"Requested by {ctx.author}",icon_url=ctx.author.avatar_url)
        return await ctx.send(embed=embed,
                              reference=ctx.message,
                              mention_author=False)


    @custom_main.group(invoke_without_command=True,name="server")
    @commands.guild_only()
    async def guild_show(self,ctx):
        """
        Displays the list of guild specific commands which requires Prefix and their repsonses, for the guild in which command was used.
        """
        prefix = mongodbUtils.get_local_prefix(ctx.message)
        guild_cmd_coll = self.db['guild_custom_commands']
        guild_doc = guild_cmd_coll.find_one({"guild_id":ctx.guild.id})
        all_cmds = guild_doc['custom_commands']
        custom_commands = []
        found_atleast_one = False

        if len(all_cmds) == 0:
            """If guild is not having any custom commands added, this will execute"""
            return await ctx.send(f"Your server is not having any custom commands currently, use `{prefix}help custom` command to know about how to add the custom commands.",
                                  reference=ctx.message,
                                  mention_author=False)

        for dictt in all_cmds:
            if dictt['need_prefix']:
                found_atleast_one = True
                custom_commands.append(dictt)

        if not found_atleast_one:
            return await ctx.send("There aren't any commands which requires prefix for this server",
                                  reference=ctx.message,
                                  mention_author=False)

        embed = discord.Embed(title=f"Custom Commands for Server : {ctx.guild.name}",description=f"***Custom Commands Which Requires Prefix***",colour=discord.Colour.dark_gold())
        embed_fields_limit = botData.embed_fields_limit-5
        # Embed fields limit is 25 , we are decreasing it by 5 just for being safe , because total number of characters in an embed should not exceed 6000
        if len(custom_commands) < embed_fields_limit:
            for dictx in custom_commands:
                command = dictx['command']
                temp_response = dictx['response']
                response = botFuncs.slice_cmd_response(command,temp_response)
                command_author = dictx['user_tag']
                time_stamp = dictx['time_stamp']
                if dictx['need_prefix']:
                    str_cmd_data = (f"Response: `{response}`\n"
                                    f"Credit: `{command_author}`\n"
                                    f"Added at Time (UTC) : `[{time_stamp}]`")
                    embed.add_field(name=f"Command : {command}",value=str_cmd_data,inline=False)

            embed.set_thumbnail(url=ctx.guild.icon_url)
            embed.set_footer(text=f"Requested by {ctx.author}",icon_url=ctx.author.avatar_url)

            return await ctx.send(embed=embed,
                                  reference=ctx.message,
                                  mention_author=False)
        else:
            start = 0
            end = embed_fields_limit
            temp_list = []

            while end <= len(custom_commands):
                temp_list.append(custom_commands[start:end])
                start += embed_fields_limit
                end += embed_fields_limit
                if (len(custom_commands) - (end - embed_fields_limit)) % embed_fields_limit == 0 and temp_list[-1][-1] == custom_commands[-1]:
                    break
            if (len(custom_commands) - (end - embed_fields_limit)) % embed_fields_limit != 0:
                temp_list.append(custom_commands[(end - embed_fields_limit):])

            cmd_msg :discord.Message = await ctx.send("Loading Commands... please be patient")
            await asyncio.sleep(1.5)
            react_emojis = ['\U000025C0','\U000025B6'] # [Left Emoji , Right Emoji]
            def check(r:discord.Reaction,u: Union[discord.Member,discord.User]):
                reactions_check = str(r.emoji) in react_emojis
                user_msg_check = u.id == ctx.author.id and r.message.id == cmd_msg.id
                return reactions_check and user_msg_check

            index = 0
            while True:
                embed = discord.Embed(title=f"Custom Commands for Server : {ctx.guild.name}",description=f"***Custom Commands Which Requires Prefix***\n***Page : {index+1}/{len(temp_list)}***",colour=discord.Colour.dark_gold())
                cmd_list = temp_list[index]

                for dictx in cmd_list:
                    command = dictx['command']
                    temp_response = dictx['response']
                    response = botFuncs.slice_cmd_response(command,temp_response)
                    command_author = dictx['user_tag']
                    time_stamp = dictx['time_stamp']
                    if dictx['need_prefix']:
                        str_cmd_data = (f"Response: `{response}`\n"
                                        f"Credit: `{command_author}`\n"
                                        f"Added at Time (UTC) : `[{time_stamp}]`")
                        embed.add_field(name=f"Command : {command}",value=str_cmd_data,inline=False)

                embed.set_thumbnail(url=ctx.guild.icon_url)
                embed.set_footer(text=f"Page : {index+1}/{len(temp_list)} \nRequested by {ctx.author}",icon_url=ctx.author.avatar_url)

                await cmd_msg.edit(embed=embed,
                                   content=None)
                await cmd_msg.add_reaction(react_emojis[0])
                await cmd_msg.add_reaction(react_emojis[1])

                try:
                    reaction,user = await self.client.wait_for(event='reaction_add',check=check,timeout=60)
                except asyncio.TimeoutError:
                    await cmd_msg.clear_reaction(react_emojis[0])
                    await cmd_msg.clear_reaction(react_emojis[1])
                    await cmd_msg.add_reaction("\U0001F512") # Lock Emoji
                    return
                else:
                    await cmd_msg.remove_reaction(reaction,user)
                    if str(reaction.emoji) == react_emojis[1]:
                        index += 1
                    elif str(reaction.emoji) == react_emojis[0]:
                        index -= 1
                # Handling Index out of range while keeping the embed rotation logic working
                if index == -1:
                    index = len(temp_list)-1
                elif index == len(temp_list):
                    index = 0


    @guild_show.command(name="noprefix",aliases=["nopre"])
    @commands.guild_only()
    async def guild_show_no_prefix(self,ctx):
        """
        Displays the list of guild specific commands which doesn't requires Prefix and their repsonses, for the guild in which command was used.
        """
        prefix = mongodbUtils.get_local_prefix(ctx.message)
        guild_cmd_coll = self.db['guild_custom_commands']
        guild_doc = guild_cmd_coll.find_one({"guild_id":ctx.guild.id})
        all_cmds = guild_doc['custom_commands']
        custom_commands = []
        found_atleast_one = False

        if len(all_cmds) == 0:
            """If guild is not having any custom commands added, this will execute"""
            return await ctx.send(f"Your server is not having any custom commands currently, use `{prefix}help custom` command to know about how to add the custom commands.",
                                  reference=ctx.message,
                                  mention_author=False)

        for dictt in all_cmds:
            if not dictt['need_prefix']:
                found_atleast_one = True
                custom_commands.append(dictt)

        if not found_atleast_one:
            return await ctx.send("There aren't any commands which doesn't require prefix for this server",
                                  reference=ctx.message,
                                  mention_author=False)

        embed = discord.Embed(title=f"Custom Commands for Server : {ctx.guild.name}",description=f"***Custom Commands Which Doesn't Require Prefix***",colour=discord.Colour.dark_gold())
        embed_fields_limit = botData.embed_fields_limit-5
        # Embed fields limit is 25 , we are decreasing it by 5 just for being safe , because total number of characters in an embed should not exceed 6000
        if len(custom_commands) < embed_fields_limit:
            for dictx in custom_commands:
                command = dictx['command']
                temp_response = dictx['response']
                response = botFuncs.slice_cmd_response(command,temp_response)
                command_author = dictx['user_tag']
                time_stamp = dictx['time_stamp']
                if not dictx['need_prefix']:
                    str_cmd_data = (f"Response: `{response}`\n"
                                    f"Credit: `{command_author}`\n"
                                    f"Added at Time (UTC) : `[{time_stamp}]`")
                    embed.add_field(name=f"Command : {command}",value=str_cmd_data,inline=False)

            embed.set_thumbnail(url=ctx.guild.icon_url)
            embed.set_footer(text=f"Requested by {ctx.author}",icon_url=ctx.author.avatar_url)

            return await ctx.send(embed=embed,
                                  reference=ctx.message,
                                  mention_author=False)
        else:
            start = 0
            end = embed_fields_limit
            temp_list = []

            while end <= len(custom_commands):
                temp_list.append(custom_commands[start:end])
                start += embed_fields_limit
                end += embed_fields_limit
                if (len(custom_commands) - (end - embed_fields_limit)) % embed_fields_limit == 0 and temp_list[-1][-1] == custom_commands[-1]:
                    break
            if (len(custom_commands) - (end - embed_fields_limit)) % embed_fields_limit != 0:
                temp_list.append(custom_commands[(end - embed_fields_limit):])

            cmd_msg :discord.Message = await ctx.send("Loading Commands... please be patient")
            await asyncio.sleep(1.5)
            react_emojis = ['\U000025C0','\U000025B6'] # [Left Emoji , Right Emoji]
            def check(r:discord.Reaction,u: Union[discord.Member,discord.User]):
                reactions_check = str(r.emoji) in react_emojis
                user_msg_check = u.id == ctx.author.id and r.message.id == cmd_msg.id
                return reactions_check and user_msg_check

            index = 0
            while True:
                embed = discord.Embed(title=f"Custom Commands for Server : {ctx.guild.name}",description=f"***Custom Commands Which Doesn't Requires Prefix***\n***Page : {index+1}/{len(temp_list)}***",colour=discord.Colour.dark_gold())
                cmd_list = temp_list[index]

                for dictx in cmd_list:
                    command = dictx['command']
                    temp_response = dictx['response']
                    response = botFuncs.slice_cmd_response(command,temp_response)
                    command_author = dictx['user_tag']
                    time_stamp = dictx['time_stamp']
                    if not dictx['need_prefix']:
                        str_cmd_data = (f"Response: `{response}`\n"
                                        f"Credit: `{command_author}`\n"
                                        f"Added at Time (UTC) : `[{time_stamp}]`")
                        embed.add_field(name=f"Command : {command}",value=str_cmd_data,inline=False)

                embed.set_thumbnail(url=ctx.guild.icon_url)
                embed.set_footer(text=f"Page : {index+1}/{len(temp_list)} \nRequested by {ctx.author}",icon_url=ctx.author.avatar_url)

                await cmd_msg.edit(embed=embed,
                                   content=None)
                await cmd_msg.add_reaction(react_emojis[0])
                await cmd_msg.add_reaction(react_emojis[1])

                try:
                    reaction,user = await self.client.wait_for(event='reaction_add',check=check,timeout=60)
                except asyncio.TimeoutError:
                    await cmd_msg.clear_reaction(react_emojis[0])
                    await cmd_msg.clear_reaction(react_emojis[1])
                    await cmd_msg.add_reaction("\U0001F512") # Lock Emoji
                    return
                else:
                    await cmd_msg.remove_reaction(reaction,user)
                    if str(reaction.emoji) == react_emojis[1]:
                        index += 1
                    elif str(reaction.emoji) == react_emojis[0]:
                        index -= 1
                # Handling Index out of range while keeping the embed rotation logic working
                if index == -1:
                    index = len(temp_list)-1
                elif index == len(temp_list):
                    index = 0


    @custom_main.group(invoke_without_command=True,name="self", aliases=['mycommands'])
    @commands.check(mongodbUtils.is_custom_command_opted)
    async def self_show(self,ctx):
        """
        Displays the list of user specific commands and their responses, where user is the command author.
        """
        prefix = mongodbUtils.get_local_prefix(ctx.message)
        users_cmd_coll = self.db['user_custom_commands']
        user_doc = users_cmd_coll.find_one({"user_id":ctx.author.id})
        all_cmds = user_doc['custom_commands']
        custom_commands = []
        found_atleast_one = False

        if len(all_cmds) == 0:
            """If guild is not having any custom commands added, this will execute"""
            return await ctx.send(f"Your server is not having any custom commands currently, use `{prefix}help custom` command to know about how to add the custom commands.",
                                  reference=ctx.message,
                                  mention_author=False)

        for dictt in all_cmds:
            if dictt['need_prefix']:
                found_atleast_one = True
                custom_commands.append(dictt)

        if not found_atleast_one:
            return await ctx.send("There aren't any commands which require prefix for this user",
                                  reference=ctx.message,
                                  mention_author=False)

        embed = discord.Embed(title=f"Custom Commands for User : {ctx.author.name}",description=f"***Custom Commands Which Requires Prefix***",colour=discord.Colour.dark_gold())
        embed_fields_limit = botData.embed_fields_limit-5
        # Embed fields limit is 25 , we are decreasing it by 5 just for being safe , because total number of characters in an embed should not exceed 6000
        if len(custom_commands) < embed_fields_limit:
            for dictx in custom_commands:
                command = dictx['command']
                temp_response = dictx['response']
                response = botFuncs.slice_cmd_response(command,temp_response)
                time_stamp = dictx['time_stamp']
                if dictx['need_prefix']:
                    str_cmd_data = (f"Response: `{response}`\n"
                                    f"Added at Time (UTC) : `[{time_stamp}]`")
                    embed.add_field(name=f"Command : {command}",value=str_cmd_data,inline=False)

            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.set_footer(text=f"Requested by {ctx.author}",icon_url=ctx.author.avatar_url)

            return await ctx.send(embed=embed,
                                  reference=ctx.message,
                                  mention_author=False)
        else:
            start = 0
            end = embed_fields_limit
            temp_list = []

            while end <= len(custom_commands):
                temp_list.append(custom_commands[start:end])
                start += embed_fields_limit
                end += embed_fields_limit
                if (len(custom_commands) - (end - embed_fields_limit)) % embed_fields_limit == 0 and temp_list[-1][-1] == custom_commands[-1]:
                    break

            if (len(custom_commands) - (end - embed_fields_limit)) % embed_fields_limit != 0:
                temp_list.append(custom_commands[(end - embed_fields_limit):])

            cmd_msg :discord.Message = await ctx.send("Loading Commands... please be patient")
            await asyncio.sleep(1.5)
            react_emojis = ['\U000025C0','\U000025B6'] # [Left Emoji , Right Emoji]
            def check(r:discord.Reaction,u: Union[discord.Member,discord.User]):
                reactions_check = str(r.emoji) in react_emojis
                user_msg_check = u.id == ctx.author.id and r.message.id == cmd_msg.id
                return reactions_check and user_msg_check

            index = 0
            while True:
                embed = discord.Embed(title=f"Custom Commands for User : {ctx.author.name}",description=f"***Custom Commands Which Requires Prefix***\n***Page : {index+1}/{len(temp_list)}***",colour=discord.Colour.dark_gold())
                cmd_list = temp_list[index]

                for dictx in cmd_list:
                    command = dictx['command']
                    temp_response = dictx['response']
                    response = botFuncs.slice_cmd_response(command,temp_response)
                    time_stamp = dictx['time_stamp']
                    if dictx['need_prefix']:
                        str_cmd_data = (f"Response: `{response}`\n"
                                        f"Added at Time (UTC) : `[{time_stamp}]`")
                        embed.add_field(name=f"Command : {command}",value=str_cmd_data,inline=False)

                embed.set_thumbnail(url=ctx.author.avatar_url)
                embed.set_footer(text=f"Page : {index+1}/{len(temp_list)} \nRequested by {ctx.author}",icon_url=ctx.author.avatar_url)

                await cmd_msg.edit(embed=embed,
                                   content=None)
                await cmd_msg.add_reaction(react_emojis[0])
                await cmd_msg.add_reaction(react_emojis[1])

                try:
                    reaction,user = await self.client.wait_for(event='reaction_add',check=check,timeout=60)
                except asyncio.TimeoutError:
                    await cmd_msg.clear_reaction(react_emojis[0])
                    await cmd_msg.clear_reaction(react_emojis[1])
                    await cmd_msg.add_reaction("\U0001F512") # Lock Emoji
                    return
                else:
                    await cmd_msg.remove_reaction(reaction,user)
                    if str(reaction.emoji) == react_emojis[1]:
                        index += 1
                    elif str(reaction.emoji) == react_emojis[0]:
                        index -= 1
                # Handling Index out of range while keeping the embed rotation logic working
                if index == -1:
                    index = len(temp_list)-1
                elif index == len(temp_list):
                    index = 0


    @self_show.command(name="noprefix",aliases=['nopre'])
    @commands.check(mongodbUtils.is_custom_command_opted)
    async def self_show_no_prefix(self,ctx):
        """
        Displays the list of user specific commands which doesn't require prefix and their responses, where user is the command author.
        """
        prefix = mongodbUtils.get_local_prefix(ctx.message)
        users_cmd_coll = self.db['user_custom_commands']
        user_doc = users_cmd_coll.find_one({"user_id": ctx.author.id})
        all_cmds = user_doc['custom_commands']
        custom_commands = []
        found_atleast_one = False

        if len(all_cmds) == 0:
            """If guild is not having any custom commands added, this will execute"""
            return await ctx.send(f"Your server is not having any custom commands currently, use `{prefix}help custom` command to know about how to add the custom commands.",
                                  reference=ctx.message,
                                  mention_author=False)

        for dictt in all_cmds:
            if not dictt['need_prefix']:
                found_atleast_one = True
                custom_commands.append(dictt)

        if not found_atleast_one:
            return await ctx.send("There aren't any commands which require prefix for this user",
                                  reference=ctx.message,
                                  mention_author=False)

        embed = discord.Embed(title=f"Custom Commands for User : {ctx.author.name}", description=f"***Custom Commands Which Doesn't Require Prefix***", colour=discord.Colour.dark_gold())
        embed_fields_limit = botData.embed_fields_limit-5
        # Embed fields limit is 25 , we are decreasing it by 5 just for being safe , because total number of characters in an embed should not exceed 6000
        if len(custom_commands) < embed_fields_limit:
            for dictx in custom_commands:
                command = dictx['command']
                temp_response = dictx['response']
                response = botFuncs.slice_cmd_response(command,temp_response)
                time_stamp = dictx['time_stamp']
                if not dictx['need_prefix']:
                    str_cmd_data = (f"Response: `{response}`\n"
                                    f"Added at Time (UTC) : `[{time_stamp}]`")
                    embed.add_field(name=f"Command : {command}", value=str_cmd_data, inline=False)

            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)

            return await ctx.send(embed=embed,
                                  reference=ctx.message,
                                  mention_author=False)
        else:
            start = 0
            end = embed_fields_limit
            temp_list = []

            while end <= len(custom_commands):
                temp_list.append(custom_commands[start:end])
                start += embed_fields_limit
                end += embed_fields_limit
                if (len(custom_commands) - (end - embed_fields_limit)) % embed_fields_limit == 0 and temp_list[-1][-1] == custom_commands[-1]:
                    break

            if (len(custom_commands) - (end - embed_fields_limit)) % embed_fields_limit != 0:
                temp_list.append(custom_commands[(end - embed_fields_limit):])

            cmd_msg: discord.Message = await ctx.send("Loading Commands... please be patient")
            await asyncio.sleep(1.5)
            react_emojis = ['\U000025C0', '\U000025B6'] # [Left Emoji , Right Emoji]

            def check(r: discord.Reaction, u: Union[discord.Member, discord.User]):
                reactions_check = str(r.emoji) in react_emojis
                user_msg_check = u.id == ctx.author.id and r.message.id == cmd_msg.id
                return reactions_check and user_msg_check

            index = 0
            while True:
                embed = discord.Embed(title=f"Custom Commands for User : {ctx.author.name}", description=f"***Custom Commands Which Doesn't Require Prefix***\n***Page : {index + 1}/{len(temp_list)}***", colour=discord.Colour.dark_gold())
                cmd_list = temp_list[index]

                for dictx in cmd_list:
                    command = dictx['command']
                    temp_response = dictx['response']
                    response = botFuncs.slice_cmd_response(command,temp_response)
                    time_stamp = dictx['time_stamp']
                    if not dictx['need_prefix']:
                        str_cmd_data = (f"Response: `{response}`\n"
                                        f"Added at Time (UTC) : `[{time_stamp}]`")
                        embed.add_field(name=f"Command : {command}", value=str_cmd_data, inline=False)

                embed.set_thumbnail(url=ctx.author.avatar_url)
                embed.set_footer(text=f"Page : {index + 1}/{len(temp_list)} \nRequested by {ctx.author}", icon_url=ctx.author.avatar_url)

                await cmd_msg.edit(embed=embed,
                                   content=None)
                await cmd_msg.add_reaction(react_emojis[0])
                await cmd_msg.add_reaction(react_emojis[1])

                try:
                    reaction, user = await self.client.wait_for(event='reaction_add', check=check, timeout=60)
                except asyncio.TimeoutError:
                    await cmd_msg.clear_reaction(react_emojis[0])
                    await cmd_msg.clear_reaction(react_emojis[1])
                    await cmd_msg.add_reaction("\U0001F512") # Lock Emoji
                    return
                else:
                    await cmd_msg.remove_reaction(reaction, user)
                    if str(reaction.emoji) == react_emojis[1]:
                        index += 1
                    elif str(reaction.emoji) == react_emojis[0]:
                        index -= 1
                # Handling Index out of range while keeping the embed rotation logic working
                if index == -1:
                    index = len(temp_list) - 1
                elif index == len(temp_list):
                    index = 0



    @custom_main.command(name="add",aliases=['+'])
    @commands.guild_only()
    async def guild_add(self,ctx, command_name , * , command_response):
        """
        Adds a custom command for the guild , with need_prefix = True
        """
        command_checked = await asyncUtils.custcmd_length_check(ctx,command_name,command_response)
        if not command_checked:
            return

        # Creating fields for doc in db
        guild_id = ctx.guild.id
        guild_name = ctx.guild.name
        user_id = ctx.author.id
        user_tag = str(ctx.author)
        need_prefix = True
        time_stamp = botFuncs.getDateTime()
        command = command_name
        response = command_response


        guild_commands_coll = self.db['guild_custom_commands']
        filter_dict = {
            "guild_id" : guild_id
        }
        custom_commands = guild_commands_coll.find_one(filter_dict,{"_id":0})['custom_commands']

        flag = False
        for dictx in custom_commands:
            if dictx['command'] == command:
                flag = True

        if flag:
            return await ctx.send(f"Your command name : `{command}` , is already taken as custom command name in this guild, please choose a different command name",
                           reference=ctx.message,
                           mention_author=False
                           )

        nested_command_dict = {
            "user_id" : user_id,
            "user_tag" : user_tag,
            "command" : command,
            "response" : response,
            "need_prefix" : need_prefix,
            "time_stamp" : time_stamp
        }
        custom_commands.append(nested_command_dict)

        main_doc_dict = {
            "guild_id" : guild_id,
            "guild_name" : guild_name,
            "custom_commands" : custom_commands
        }

        guild_commands_coll.update_one(filter=filter_dict,
                                       update={"$set":main_doc_dict})
        return await ctx.send(f"Added custom command for this server : \n`{command} --> {response}`\n"
                              f"prefix required = `{need_prefix}`",
                              reference=ctx.message,
                              mention_author=False)


    @custom_main.command(name="add.nopre",aliases=["+nopre"])
    @commands.guild_only()
    async def guild_add_no_prefix(self,ctx, command_name,*, command_response):
        """
        Adds a custom command for guild, with need_prefix = False
        """
        command_checked = await asyncUtils.custcmd_length_check(ctx,command_name,command_response)
        if not command_checked:
            return

        # Creating fields for doc in db
        guild_id = ctx.guild.id
        guild_name = ctx.guild.name
        user_id = ctx.author.id
        user_tag = str(ctx.author)
        need_prefix = False
        time_stamp = botFuncs.getDateTime()
        command = command_name
        response = command_response


        guild_commands_coll = self.db['guild_custom_commands']
        filter_dict = {
            "guild_id" : guild_id
        }
        guild_doc = guild_commands_coll.find_one(filter_dict,{"_id":0})
        custom_commands = guild_doc['custom_commands']

        flag = False
        for dictx in custom_commands:
            if dictx['command'] == command:
                flag = True
                break

        if flag:
            return await ctx.send(f"Your command name : `{command}` , is already taken as custom command name in this guild, please choose a different command name",
                           reference=ctx.message,
                           mention_author=False
                           )

        nested_command_dict = {
            "user_id" : user_id,
            "user_tag" : user_tag,
            "command" : command,
            "response" : response,
            "need_prefix" : need_prefix,
            "time_stamp" : time_stamp
        }
        custom_commands.append(nested_command_dict)

        guild_doc.update({"custom_commands":custom_commands})

        guild_commands_coll.update_one(filter=filter_dict,
                                       update={"$set":guild_doc})
        return await ctx.send(f"Added custom command for this server: \n`{command} --> {response}`\n"
                              f"prefix required = `{need_prefix}`",
                              reference=ctx.message,
                              mention_author=False)


    @custom_main.command(name="addself",aliases=['s+'])
    @commands.check(mongodbUtils.is_custom_command_opted)
    async def add_user_command(self,ctx, command_name,*, command_response):
        """
        Adds a custom command for User, with need_prefix = True
        """
        command_checked = await asyncUtils.custcmd_length_check(ctx,command_name,command_response)
        if not command_checked:
            return

        # Creating fields for doc in db
        user_id = ctx.author.id
        user_tag = str(ctx.author)
        command = command_name
        response = command_response
        need_prefix = True
        time_stamp = botFuncs.getDateTime()

        user_cmd_coll = self.db['user_custom_commands']
        user_doc = user_cmd_coll.find_one({"user_id":ctx.author.id})
        custom_commands = user_doc['custom_commands']

        flag = False
        for dict in custom_commands:
            if dict['command'] == command:
                flag = True
                break

        if flag:
            return await ctx.send(f"You are already having a command with same name as this one, please choose another name for this command",
                                  reference=ctx.message,
                                  mention_author=False)

        nested_command_dict = {
            "command" : command,
            "response" : response,
            "need_prefix": need_prefix,
            "time_stamp": time_stamp
        }
        custom_commands.append(nested_command_dict)
        user_doc.update({"custom_commands":custom_commands})

        user_cmd_coll.update_one(filter={"user_id":user_id},
                                 update={"$set":user_doc})
        return await ctx.send(f"Added custom command for user `{ctx.author}`: \n`{command} --> {response}`\n"
                              f"prefix required = `{need_prefix}`",
                              reference=ctx.message,
                              mention_author=False)


    @custom_main.command(name="addself.nopre",aliases=['s+nopre'])
    @commands.check(mongodbUtils.is_custom_command_opted)
    async def add_userCmd_no_prefix(self,ctx, command_name,*, command_response):
        """
        Adds a custom command for User, with need_prefix = False
        """
        command_checked = await asyncUtils.custcmd_length_check(ctx,command_name,command_response)
        if not command_checked:
            return

        # Creating fields for doc in db
        user_id = ctx.author.id
        user_tag = str(ctx.author)
        command = command_name
        response = command_response
        need_prefix = False
        time_stamp = botFuncs.getDateTime()

        user_cmd_coll = self.db['user_custom_commands']
        user_doc = user_cmd_coll.find_one({"user_id": ctx.author.id})
        custom_commands = user_doc['custom_commands']

        flag = False
        for dict in custom_commands:
            if dict['command'] == command:
                flag = True
                break

        if flag:
            return await ctx.send(f"You are already having a command with same name as this one, please choose another name for this command",
                                  reference=ctx.message,
                                  mention_author=False)

        nested_command_dict = {
            "command": command,
            "response": response,
            "need_prefix": need_prefix,
            "time_stamp": time_stamp
        }
        custom_commands.append(nested_command_dict)
        user_doc.update({"custom_commands": custom_commands})

        user_cmd_coll.update_one(filter={"user_id": user_id},
                                 update={"$set": user_doc})
        return await ctx.send(f"Added custom command for user `{ctx.author}` : \n`{command} --> {response}`\n"
                              f"prefix required = `{need_prefix}`",
                              reference=ctx.message,
                              mention_author=False)


    @custom_main.command(name="removeself",aliases=['s-'])
    @commands.check(mongodbUtils.is_custom_command_opted)
    async def remove_user_command(self,ctx,command_name):
        user_command_coll = self.db['user_custom_commands']
        user_doc = user_command_coll.find_one({"user_id":ctx.author.id})
        custom_commands = user_doc['custom_commands']

        flag = False
        for dictx in custom_commands:
            if dictx['command'] == command_name:
                response = dictx['response']
                need_prefix = dictx['need_prefix']
                flag = True
                break

        if not flag:
            return await ctx.send(f"{ctx.author.mention}, There is no such command in your custom commands, please check your spelling and try again",
                                  reference=ctx.message,
                                  mention_author=False
                                  )
        else:
            resp_msg = await ctx.send(f"Command Name: `{command_name}`,\n"
                                      f"\nResponse: `{response}`\n"
                                      f"Prefix required = `{need_prefix}`\n"
                                      f"{ctx.author.mention}, Are you sure you want to delete this command?\n"
                                      f"[reply with **y** or **n** within 1 minute]")

            def check(msg:discord.Message):
                response_from_author = msg.author.id == ctx.author.id and msg.channel.id == ctx.message.channel.id
                response_as_expected = msg.content.lower() == 'y' or msg.content.lower() == 'n'
                return response_as_expected and response_from_author

            try:
                waitMsg = await self.client.wait_for(event='message',check=check,timeout=60)
            except asyncio.TimeoutError:
                return await ctx.send(f"No response was given from {ctx.author.name} for this message, command still active, use the command again if you want to delete",
                                      reference=resp_msg,
                                      mention_author=False)
            else:
                if waitMsg.content.lower() == 'y':
                    custom_commands = [dct for dct in custom_commands if dct['command'] != command_name]
                    user_doc.update({'custom_commands':custom_commands})
                    user_command_coll.update_one(filter={"user_id":ctx.author.id},
                                                 update={"$set":user_doc})
                    return await ctx.send(f"Succesfully deleted the command",
                                          reference=waitMsg,
                                          mention_author=False)
                elif waitMsg.content.lower() == 'n':
                    return await ctx.send("Alright, Cool.. so we are keeping the command then",
                                          reference=waitMsg,
                                          mention_author=False)


    @custom_main.command(name="remove",aliases=['-'])
    @commands.guild_only()
    async def guild_remove(self,ctx,command_name):
        prefix = mongodbUtils.get_local_prefix(ctx.message)
        guild_cmd_coll = self.db['guild_custom_commands']
        guild_doc = guild_cmd_coll.find_one({"guild_id":ctx.guild.id})
        custom_commands = guild_doc['custom_commands']
        if len(custom_commands) == 0:
            return await ctx.send(f"There are no custom commands added for this guild, use `{prefix}help custom` to know how to add custom commands.",
                                  reference=ctx.message,
                                  mention_author=False)

        flag = False
        user_is_author = False
        for dictx in custom_commands:
            if dictx['command'] == command_name:
                flag = True
                if (dictx['user_id'] == ctx.author.id):
                    user_is_author = True
                break

        if not flag:
            # Command not found
            return await ctx.send(f"There is no such command in custom commands for this server, check your spellings and try again",
                                  reference=ctx.message,
                                  mention_author=False)
        if flag and (not user_is_author):
            # command found but user is not the author of custom command
            return await ctx.send("You are not the author of this command, only the command author or server mod can delete these commands",
                                  reference=ctx.message,
                                  mention_author=False)
        if flag and user_is_author:
            # command found and user is the author of the custom command
            response = dictx['response']
            need_prefix = dictx['need_prefix']
            resp_msg = await ctx.send(f"Command Name: `{command_name}`, Response: `{response}`\n"
                                      f"Prefix required = `{need_prefix}`\n"
                                      f"{ctx.author.mention}, Are you sure you want to delete this command?\n"
                                      f"[reply with **y** or **n** within 1 minute]")

            def check(msg: discord.Message):
                response_from_author = msg.author.id == ctx.author.id and msg.channel.id == ctx.message.channel.id
                response_as_expected = msg.content.lower() == 'y' or msg.content.lower() == 'n'
                return response_as_expected and response_from_author

            try:
                waitMsg = await self.client.wait_for(event='message', check=check, timeout=60)
            except asyncio.TimeoutError:
                return await ctx.send(f"No response was given from {ctx.author.name} for this message, command still active, use the command again if you want to delete",
                                      reference=resp_msg,
                                      mention_author=False)
            else:
                if waitMsg.content.lower() == 'y':
                    custom_commands = [dct for dct in custom_commands if dct['command'] != command_name]
                    guild_doc.update({'custom_commands': custom_commands})
                    guild_cmd_coll.update_one(filter={"guild_id":ctx.guild.id},
                                              update={"$set":guild_doc})
                    return await ctx.send(f"Succesfully Deleted the command from this server's commands list",
                                          reference=waitMsg,
                                          mention_author=False)
                else:
                    return await ctx.send("Alright, Cool.. so we are keeping the command then",
                                          reference=waitMsg,
                                          mention_author=False)


    @custom_main.command(name="optin")
    async def user_optin(self, ctx):
        prefix = mongodbUtils.get_local_prefix(ctx.message)
        user_cmd_coll = self.db['user_custom_commands']
        user_doc = user_cmd_coll.find_one(filter={"user_id": ctx.author.id})
        if not user_doc:
            user_id = ctx.author.id
            user_tag = str(ctx.author)
            custom_commands = []
            doc_dict = {
                "user_id": user_id,
                "user_tag": user_tag,
                "custom_commands": custom_commands
            }

            user_cmd_coll.insert_one(doc_dict)
            log_string = f"[{botFuncs.getDateTime()}] --> {ctx.author} Opted In for user Custom Commands"
            botFuncs.log_func(log_string=log_string, file_name=botData.user_optin_EventLogFile, newlines=1)
            return await ctx.send(f"{ctx.author.mention}, You successfully opted in for user exclusive custom commands, go ahead and make some cool commands for yourself :slight_smile:",
                                  reference=ctx.message,
                                  mention_author=False)
        else:
            return await ctx.send(f"{ctx.author.mention}, You are already opted in for user exclusive commands, go ahead and make some cool commands for yourself :slight_smile:\n"
                                  f"if you want to opt out, just use `{prefix}custom optout` command",
                                  reference=ctx.message,
                                  mention_author=False)


    @custom_main.command(name="optout")
    async def user_optout(self, ctx):
        prefix = mongodbUtils.get_local_prefix(ctx.message)
        user_cmd_coll = self.db['user_custom_commands']
        user_doc = user_cmd_coll.find_one(filter={"user_id": ctx.author.id})
        if not user_doc:
            return await ctx.send(f"{ctx.author.mention}, You are not opted in for user exclusive commands\n"
                                  f"if you want to opt in , just use `{prefix}custom optin` command",
                                  reference=ctx.message,
                                  mention_author=False)
        else:
            resp_msg = await ctx.send(f"{ctx.author.mention}, If you opt out of user exclusive commands, all of your commands data will be gone forever, you have to opt in again and make all those commands again if you want them\n"
                                      f"do you still want to opt out and delete all of your exclusive commands? \n[reply with **y** or **n** within 1 minute]",
                                      reference=ctx.message,
                                      mention_author=False)

            def check(msg: discord.Message):
                response_from_author = msg.author.id == ctx.author.id and msg.channel.id == ctx.message.channel.id
                response_as_expected = msg.content.lower() == 'y' or msg.content.lower() == 'n'
                return response_as_expected and response_from_author

            try:
                wait_msg = await self.client.wait_for(event='message', check=check, timeout=60)
            except asyncio.TimeoutError:
                return await ctx.send(f"No Response was given from {ctx.author.name} in given time, user still opted in, use command again and respond to opt out",
                                      reference=resp_msg,
                                      mention_author=False)
            else:
                if wait_msg.content.lower() == 'y':
                    user_cmd_coll.delete_one({"user_id": ctx.author.id})
                    log_string = f"[{botFuncs.getDateTime()}] --> {ctx.author} Opted Out from user Custom Commands"
                    botFuncs.log_func(log_string=log_string, file_name=botData.user_optout_EventLogFile, newlines=1)
                    return await ctx.send(f"{ctx.author.mention}, You successfully opted out of user exclusive commands, all of your commands are now gone\n"
                                          f"though you can still opt in using `{prefix}custom optin` but you'll have to make all commands again",
                                          reference=ctx.message,
                                          mention_author=False)

                elif wait_msg.content.lower() == 'n':
                    return await ctx.send(f"{ctx.author.mention}, Alright so you changed your mind, Cool!!\n"
                                          f"now go ahead use and make some of your exclusive commands, enjoy! :slight_smile:",
                                          reference=wait_msg,
                                          mention_author=False)


    async def cog_command_error(self, ctx, error):
        """
        Command error handler for this cog class
        """
        if isinstance(error, commands.CommandInvokeError):
            error = error.original

        prefix = mongodbUtils.get_local_prefix(ctx.message)
        author = ctx.author
        del_after = 10
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"{author.mention}, Please provide all the arguments Required for the command.\n", delete_after=del_after)
        elif isinstance(error,commands.NoPrivateMessage):
            return await ctx.send(f"{author.name}, This command cannot be used in Direct Messages, use this command only in servers!")
        elif isinstance(error,commands.CheckFailure):
            return await ctx.send(f"{author.mention}, You have not opted in for user exclusive custom commands, to opt in please use this command `{prefix}custom optin`, similarly to opt out , use this command `{prefix}custom optout`",
                                  reference=ctx.message,
                                  mention_author=False)
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(f"{ctx.author.mention}, Either you, or Bot is Missing Permission to perform the task.", delete_after=del_after)
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send(f"{author.mention}, You are supposed to mention a valid Discord user.", delete_after=del_after)
        elif isinstance(error, commands.RoleNotFound):
            await ctx.send(f"Can't find a Role with name : `{error.argument}`")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"Incorrect usage of the command! check what your command does by using `{prefix}help`", delete_after=del_after)
        else:
            await log_and_raise(client=self.client,ctx=ctx,error=error)


def setup(client:commands.Bot):
    client.add_cog(CustomGroup(client))