import discord
import botFuncs
import botData
import mongodbUtils
import asyncio
import pymongo
from discord.ext import commands
from asyncUtils import log_and_raise


class ModCommands(commands.Cog):
    def __init__(self,client):
        self.client = client
        self.owner_id = botData.owner_id
        self.db = mongodbUtils.db


    # ----------------------------------------- Banwords command group ------------------------------------------- #
    @commands.group(invoke_without_command=True, aliases=["bw", "banword"])
    @commands.has_permissions(manage_guild=True)
    async def banwords(self, ctx):
        banwStr = ""
        banned_words_collection = self.db["guild_bannedwords"]
        bWords_dict = banned_words_collection.find_one({"guild_id": (ctx.guild.id)},{"_id":0,"banned_words":1})
        bannedWords = bWords_dict['banned_words']

        for word in bannedWords:
            banwStr += f"**{word}**\n"

        embed = discord.Embed(title="List of Prohibited words", description=banwStr, color=discord.Colour.dark_gold())
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        return await ctx.send(embed=embed,
                              reference=ctx.message,
                              mention_author=False)

    @banwords.command(aliases=['+'])
    @commands.has_permissions(manage_guild=True)
    async def add(ctx, *, banword):
        word = banword.lower()
        banned_words_collection = mongodbUtils.db["guild_bannedwords"]
        bWords_dict = banned_words_collection.find_one({"guild_id": (ctx.guild.id)}, {"_id": 0, "banned_words": 1})
        bannedWords = bWords_dict['banned_words']

        if word in bannedWords:
            return await ctx.send(f"`{word}` is already in list of banned words",
                                  reference=ctx.message,
                                  mention_author=False)
        else:
            bannedWords.append(word)
            banned_words_collection.update_one(filter={"guild_id":(ctx.guild.id)},
                                               update={"$set":{"banned_words":bannedWords}})
            return await ctx.send(f"Successfully added `{word}` to list of banned words",
                                  reference=ctx.message,
                                  mention_author=False)

    @banwords.command(aliases=['-'])
    @commands.has_permissions(manage_guild=True)
    async def remove(ctx, *, banword):
        word = banword.lower()
        banned_words_collection = mongodbUtils.db["guild_bannedwords"]
        bWords_dict = banned_words_collection.find_one({"guild_id": (ctx.guild.id)}, {"_id": 0, "banned_words": 1})
        bannedWords = bWords_dict['banned_words']
        if word in bannedWords:
            bannedWords.remove(word)
            banned_words_collection.update_one(filter={"guild_id":(ctx.guild.id)},
                                               update={"$set":{"banned_words":bannedWords}})
            return await ctx.send(f"Successfully removed `{word}` from list of banned words",
                                  reference=ctx.message,
                                  mention_author=False)
        else:
            return await ctx.send(f"`{word}` was not found in list of banned words!",
                                  reference=ctx.message,
                                  mention_author=False)

    # ------------------------------------------ END of banwords command group ----------------------------------- #

    @commands.command(aliases=['pfx'])
    @commands.has_permissions(manage_guild=True)
    async def prefix(self, ctx, prefix):
        try:
            if len(prefix) > 3 or not prefix.isascii() or prefix == '```':
                raise ValueError

            prefix_collection = self.db['guild_prefixes']
            prefix_collection.update_one(filter={"guild_id": (ctx.guild.id)},
                                         update={"$set":{"prefix": (prefix)}})
            await ctx.send(f"Successfully set `{prefix}` as prefix for this guild!",
                           reference=ctx.message,
                           mention_author=False)
        except ValueError:
            responseStr = (f"Maximum length of prefix should be 3 characters! No special characters allowed except ASCII characters\n"
                           f"if you dont know what ASCII characters are, please Google it.")
            await ctx.send(responseStr,
                           reference=ctx.message,
                           mention_author=False)

    # ---------------------------------------------------------- Switches Group Commands -----------------------------------------------------------------#

    @commands.group(invoke_without_command=True, aliases=['switches', 'swt'])
    @commands.has_permissions(manage_guild=True)
    async def switch(self, ctx):
        switches_collection = self.db["guild_switches"]
        local_switches = switches_collection.find_one({"guild_id":(ctx.guild.id)},{"_id":0,"guild_id":0,"guild_name":0})

        embed = discord.Embed(title="Displaying Switches and data".title(), color=discord.Colour.dark_gold())
        for key, value in local_switches.items():
            embed.add_field(name=f"{key}", value=f"{value}", inline=False)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        return await ctx.send(embed=embed,
                              reference=ctx.message,
                              mention_author=False)

    @switch.command(aliases=['filter', 'fswitch'])
    @commands.has_permissions(manage_guild=True)
    async def filter_switch(self, ctx, operator):
        switches_collection = self.db["guild_switches"]
        local_switches = switches_collection.find_one({"guild_id": (ctx.guild.id)}, {"_id": 0, "guild_id": 0, "guild_name": 0})

        if operator == '+':
            local_switches['filterSwitch'] = True
            switches_collection.update_one(filter={"guild_id":(ctx.guild.id)},
                                           update={"$set":local_switches})
            await ctx.send(f'Message scanning for filtered words is Activated!', delete_after=6,
                           reference=ctx.message,
                           mention_author=False)
            await asyncio.sleep(5)
            await ctx.message.delete()
        elif operator == '-':
            local_switches['filterSwitch'] = False
            switches_collection.update_one(filter={"guild_id":(ctx.guild.id)},
                                           update={"$set":local_switches})
            await ctx.send(f'Message scanning for filtered words is turned off.', delete_after=6,
                           reference=ctx.message,
                           mention_author=False)
            await asyncio.sleep(5)
            await ctx.message.delete()

    @switch.command(aliases=['pswitch', 'psw'])
    @commands.has_permissions(manage_guild=True)
    async def p_switch(self, ctx, operator):
        switches_collection = self.db["guild_switches"]
        local_switches = switches_collection.find_one({"guild_id": (ctx.guild.id)}, {"_id": 0, "guild_id": 0, "guild_name": 0})

        if operator == '+':
            local_switches['pinSwitch'] = True
            switches_collection.update_one(filter={"guild_id":(ctx.guild.id)},
                                           update={"$set":local_switches})
            await ctx.send(f"Bot feature 'Pin on Reactions' Activated!", delete_after=6,
                           reference=ctx.message,
                           mention_author=False)
        elif operator == '-':
            local_switches['pinSwitch'] = False
            switches_collection.update_one(filter={"guild_id":(ctx.guild.id)},
                                           update={"$set":local_switches})
            await ctx.send(f"Bot feature 'Pin on Reactions' Deactivated!", delete_after=6,
                           reference=ctx.message,
                           mention_author=False)

    @switch.command(aliases=['delsnipe', 'dsnipe'])
    @commands.has_permissions(manage_guild=True)
    async def del_snipe_switch(self, ctx, operator):
        switches_collection = self.db["guild_switches"]
        local_switches = switches_collection.find_one({"guild_id": (ctx.guild.id)}, {"_id": 0, "guild_id": 0, "guild_name": 0})

        if operator == '+':
            local_switches['del_snipe_switch'] = True
            switches_collection.update_one(filter={"guild_id":(ctx.guild.id)},
                                           update={"$set":local_switches})
            await ctx.send(f"Bot feature 'Snipe Deleted Message' Activated!", delete_after=6,
                           reference=ctx.message,
                           mention_author=False)
        elif operator == '-':
            local_switches['del_snipe_switch'] = False
            switches_collection.update_one(filter={"guild_id":(ctx.guild.id)},
                                           update={"$set":local_switches})
            await ctx.send(f"Bot feature 'Snipe Deleted Message' Deactivated!", delete_after=6,
                           reference=ctx.message,
                           mention_author=False)

    @switch.command(aliases=['editsnipe', 'esnipe'])
    @commands.has_permissions(manage_guild=True)
    async def edit_snipe_switch(self, ctx, operator):
        switches_collection = self.db["guild_switches"]
        local_switches = switches_collection.find_one({"guild_id": (ctx.guild.id)}, {"_id": 0, "guild_id": 0, "guild_name": 0})

        if operator == '+':
            local_switches['edit_snipe_switch'] = True
            switches_collection.update_one(filter={"guild_id":(ctx.guild.id)},
                                           update={"$set":local_switches})
            await ctx.send(f"Bot feature 'Snipe Edited Message' Activated!", delete_after=6,
                           reference=ctx.message,
                           mention_author=False)
        elif operator == '-':
            local_switches['edit_snipe_switch'] = False
            switches_collection.update_one(filter={"guild_id":(ctx.guild.id)},
                                           update={"$set":local_switches})
            await ctx.send(f"Bot feature 'Snipe Edited Message' Deactivated!", delete_after=6,
                           reference=ctx.message,
                           mention_author=False)

    @switch.command(aliases=['reactlimit', 'rlimit'])
    @commands.has_permissions(manage_guild=True)
    async def reactionsLimit_setter(self, ctx, limit: int):
        if limit < 4:
            return await ctx.send("Total reactions limit cannot be less than 4",
                                  reference=ctx.message,
                                  mention_author=False)

        switches_collection = self.db["guild_switches"]
        local_switches = switches_collection.find_one({"guild_id": (ctx.guild.id)}, {"_id": 0, "guild_id": 0, "guild_name": 0})

        local_switches['reactLimit'] = limit
        switches_collection.update_one(filter={"guild_id":(ctx.guild.id)},
                                       update={"$set":local_switches})
        await ctx.send(f"Pin on Reactions : Reaction Limit changed to `{limit} reactions`",
                       reference=ctx.message,
                       mention_author=False)

    @switch.command(aliases=['drlimit', 'diffreact', 'difflimit'])
    @commands.has_permissions(manage_guild=True)
    async def diffReactionsLimit_setter(self, ctx, limit: int):
        if limit < 2:
            return await ctx.send("Different reaction limit cannot be less than 2",
                                  reference=ctx.message,
                                  mention_author=False)

        switches_collection = self.db["guild_switches"]
        local_switches = switches_collection.find_one({"guild_id": (ctx.guild.id)}, {"_id": 0, "guild_id": 0, "guild_name": 0})

        local_switches['diffReactLimit'] = limit
        switches_collection.update_one(filter={"guild_id":(ctx.guild.id)},
                                       update={"$set":local_switches})
        await ctx.send(f"Pin on Reactions : Number of different reactions limit changed to `{limit} Different reactions`",
                       reference=ctx.message,
                       mention_author=False)

    # -------------------------------------------------------- END of Switches Group Commands ---------------------------------------------------------------#

    @commands.command(aliases=["clear", "p"])
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int = 1):
        if amount < 0:
            await ctx.message.add_reaction("❓")
            await ctx.send("Can't delete negative number of messages!", delete_after=2.5)
        else:
            await ctx.message.delete()
            await ctx.channel.purge(limit=amount)
            await ctx.send(f'Deleted `{amount}` messages', delete_after=2.5)


    @commands.command(aliases=["m"])
    @commands.has_permissions(manage_channels=True)
    async def mute(self, ctx, member: discord.Member):
        try:
            listOfGuildRoles = ctx.guild.roles
            listMemberRoles = member.roles

            # Getting the position of highest role of -user to be muted-
            highestMemberRole_pos = listMemberRoles[len(listMemberRoles) - 1].position

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
                await muted_role.edit(position=highestMemberRole_pos)
                await ctx.send("Moved Muted role.",
                               reference=ctx.message,
                               mention_author=False)

            await member.add_roles(muted_role)
            await ctx.message.add_reaction("✅")
            await ctx.send(f'{member.mention} was Muted!',
                           reference=ctx.message,
                           mention_author=False)
        except:
            """
            If command raises a CommandInvokeError : Forbidden/HTTP : Missing Permissions
            we are converting the error to commands.MissingPermissions
            """
            raise commands.MissingPermissions('Missing Permission')


    @commands.command(aliases=["unm"])
    @commands.has_permissions(manage_channels=True)
    async def unmute(self, ctx, member: discord.Member):
        try:
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
            await ctx.send(f'{member.mention} was Unmuted!',
                           reference=ctx.message,
                           mention_author=False)
        except:
            """
            If command raises a CommandInvokeError : Forbidden/HTTP : Missing Permissions
            we are converting the error to commands.MissingPermissions
            """
            raise commands.MissingPermissions('Missing Permission')


    @commands.command(aliases=["k"])
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No Reason Provided"):
        try:
            await member.kick(reason=reason)
            await ctx.message.add_reaction("✅")
            await ctx.send(f'`{member}` was Kicked from this server, `Reason = {reason}.`',
                           reference=ctx.message,
                           mention_author=False)
        except:
            """
            If command raises a CommandInvokeError : Forbidden/HTTP : Missing Permissions
            we are converting the error to commands.MissingPermissions
            """
            raise commands.MissingPermissions('Missing Permission')


    @commands.command(aliases=["b"])
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No Reason Provided"):
        try:
            member_tag = str(member)
            await member.ban(reason=reason)
            await ctx.message.add_reaction("✅")
            await ctx.send(f'`{member_tag}` was banned from this server, `Reason = {reason}.`',
                           reference=ctx.message,
                           mention_author=False)
        except:
            """
            If command raises a CommandInvokeError : Forbidden/HTTP : Missing Permissions
            we are converting the error to commands.MissingPermissions
            """
            raise commands.MissingPermissions('Missing Permission')


    @commands.command(aliases=["unb"])
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        member_name, member_disc = member.split("#")
        ban_entriesList = await ctx.guild.bans()

        for ban_entry in ban_entriesList:
            user = ban_entry.user
            if (user.name, user.discriminator) == (member_name, member_disc):
                await ctx.guild.unban(user)
                await ctx.message.add_reaction("✅")
                return await ctx.send(f'`{user}` was Unbanned!',
                                      reference=ctx.message,
                                      mention_author=False)

        await ctx.message.add_reaction("❌")
        return await ctx.send(f'{member} not found in this guild\'s banned list.',
                              reference=ctx.message,
                              mention_author=False)


    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def pin(self, ctx):
        try:
            ref_message_id = ctx.message.reference.message_id
            ref_msg = await ctx.channel.fetch_message(ref_message_id)
        except AttributeError:
            return await ctx.send(f"{ctx.author.name}, You were supposed to reference a message (reply) with this command!",
                                  reference=ctx.message,
                                  mention_author=False)

        if ref_msg.pinned:
            return await ctx.send("Referenced Message is already Pinned!", delete_after=5)
        await ref_msg.pin()
        await ref_msg.add_reaction("📌")
        await ctx.message.add_reaction("✅")


    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def unpin(self, ctx):
        try:
            ref_message_id = ctx.message.reference.message_id
            ref_msg = await ctx.channel.fetch_message(ref_message_id)
        except AttributeError:
            return await ctx.send(f"{ctx.author.name}, You were supposed to reference a message (reply) with this command!",
                                  reference=ctx.message,
                                  mention_author=False)

        if ref_msg.pinned:
            await ref_msg.unpin()
        else:
            await ctx.send("Referenced Message is not Pinned.", delete_after=5)
            return
        await ref_msg.remove_reaction("📌", self.client.user)
        await ctx.message.add_reaction("✅")


    @commands.command(aliases=['vc', 'changevc'])
    @commands.has_permissions(manage_guild=True)
    async def change_voice_channel(self, ctx, member: discord.Member, *, vcName=None):
        guild_VC_list = ctx.guild.voice_channels
        bot_owner = self.client.get_user(self.owner_id)

        if member == bot_owner and ctx.author != bot_owner:
            return await ctx.send(f"HAHA Nice try {ctx.author.name}, I am Loyal to my Owner, i won't do that to him. Better Luck next time :wink:",
                                  reference=ctx.message,
                                  mention_author=False)

        try:
            joined_vc = member.voice.channel
        except:
            return await ctx.send(f"{member.name} is currently not in any VC.",
                                  reference=ctx.message,
                                  mention_author=False)

        if not vcName:
            await member.edit(voice_channel=vcName)
            return await ctx.send(f"{member.name} was Disconnected from `{joined_vc.name}` ",
                                  reference=ctx.message,
                                  mention_author=False)

        for vc in guild_VC_list:
            if vc.name.lower() == vcName.lower():
                voice_channel = vc
                await member.edit(voice_channel=voice_channel)
                return await ctx.send(f"{member.name} was moved from `{joined_vc.name}` to `{voice_channel.name}`",
                                      reference=ctx.message,
                                      mention_author=False)

        return await ctx.send(f"Voice Channel with name `{vcName}` Not found.",
                              reference=ctx.message,
                              mention_author=False)


    # ----------------------------------------------- Role Command Group -----------------------------------------------------------#

    @commands.group(invoke_without_command=True, aliases=['roles'])
    @commands.has_permissions(manage_roles=True)
    async def role(self, ctx):
        prefix = mongodbUtils.get_local_prefix(ctx.message)
        await ctx.send("Command Usage:\n"
                       f"`{prefix}role (add|remove) (user) (role)`",
                       reference=ctx.message,
                       mention_author=False)

    @role.command(aliases=['+'])
    @commands.has_permissions(manage_roles=True)
    async def add(self, ctx, member: discord.Member, *, grole: discord.Role):
        try:
            await member.add_roles(grole)
            await ctx.send(f"Given `{grole.name}` Role to `{member}`",
                           reference=ctx.message,
                           mention_author=False)
        except:
            raise commands.MissingPermissions("Missing Permissions")

    @role.command(aliases=['-'])
    @commands.has_permissions(manage_roles=True)
    async def remove(self, ctx, member: discord.Member, *, trole: discord.Role):
        try:
            await member.remove_roles(trole)
            await ctx.send(f"Taken `{trole.name}` Role from `{member}`",
                           reference=ctx.message,
                           mention_author=False)
        except:
            raise commands.MissingPermissions("Missing Permissions")

    @role.command(aliases=['*'])
    @commands.has_permissions(manage_roles=True)
    async def show(self, ctx, member: discord.Member):

        embed = discord.Embed(title=f"{member.name} Roles List", color=discord.Colour.dark_gold())
        embed.set_thumbnail(url=member.avatar_url)
        mentionable_roles = []
        nonMentionable_roles = []

        for role in member.roles:
            if role.name == "@everyone":
                embed.add_field(name="Default Role", value=f"{role.name}")
            elif role.mentionable:
                mentionable_roles.append(f"{role.mention}")
            else:
                nonMentionable_roles.append(f"{role.mention}")

        if len(mentionable_roles) > 0:
            mentionable_roles = mentionable_roles[::-1]
            mentioables = "\n".join(mentionable_roles)
            embed.add_field(name="Mentionable Roles:", value=mentioables, inline=False)
        if len(nonMentionable_roles) > 0:
            nonMentionable_roles = nonMentionable_roles[::-1]
            non_mentionables = "\n".join(nonMentionable_roles)
            embed.add_field(name="Non-Mentionable Roles:", value=non_mentionables, inline=False)

        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed,
                       reference=ctx.message,
                       mention_author=False)
    # --------------------------------------------- END of Role Command Group ------------------------------------------------------#


    @commands.command(name="removecmd",aliases=['cmd-'])
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def remove_custom_cmd(self,ctx,command_name):
        prefix = mongodbUtils.get_local_prefix(ctx.message)
        guild_cmd_coll = self.db['guild_custom_commands']
        guild_doc = guild_cmd_coll.find_one({"guild_id": ctx.guild.id})
        custom_commands = guild_doc['custom_commands']
        if len(custom_commands) == 0:
            return await ctx.send(f"There are no custom commands added for this guild, use `{prefix}custom-help` to know how to add custom commands.",
                                  reference=ctx.message,
                                  mention_author=False)

        flag = False
        for dictx in custom_commands:
            if dictx['command'] == command_name:
                flag = True
                break

        if not flag:
            # Command not found
            return await ctx.send(f"There is no such command in custom commands for this server, check your spellings and try again",
                                  reference=ctx.message,
                                  mention_author=False)
        else:
            # Command found
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
                    guild_cmd_coll.update_one(filter={"guild_id": ctx.guild.id},
                                              update={"$set": guild_doc})
                    return await ctx.send(f"Succesfully Deleted the command from this server's commands list",
                                          reference=waitMsg,
                                          mention_author=False)
                else:
                    return await ctx.send("Alright, Cool.. so we are keeping the command then",
                                          reference=waitMsg,
                                          mention_author=False)


    async def cog_command_error(self, ctx, error):
        """
        Command error handler for this cog class
        """
        if isinstance(error,commands.CommandInvokeError):
            error = error.original

        prefix = mongodbUtils.get_local_prefix(ctx.message)
        author = ctx.author
        del_after = 10

        if isinstance(error, commands.MissingPermissions):
            await ctx.send(f"{ctx.author.mention}, Either you, or Bot is Missing Permission to perform the task.", delete_after=del_after)
        elif isinstance(error,commands.NoPrivateMessage):
            return await ctx.send(f"{author.name}, This command cannot be used in Direct Messages, use this command only in servers!")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send(f"{author.mention}, You are supposed to mention a valid Discord user.", delete_after=del_after)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"{author.mention}, Please provide all the arguments Required for the command.\n", delete_after=del_after)
        elif isinstance(error, commands.RoleNotFound):
            await ctx.send(f"Can't find a Role with name : `{error.argument}`")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"Incorrect usage of the command! check what your command does by using `{prefix}help`", delete_after=del_after)
        else:
            await log_and_raise(client=self.client,ctx=ctx,error=error)

    
def setup(client):
    client.add_cog(ModCommands(client))