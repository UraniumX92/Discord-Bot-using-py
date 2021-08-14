import discord
from discord.ext import commands
import botFuncs
import botData
import asyncio


class ModCommands(commands.Cog):
    def __init__(self,client):
        self.client = client
        self.owner_id = botData.owner_id

    # todo-false ----------------------------------------- Banwords command group ------------------------------------------- #
    @commands.group(invoke_without_command=True, aliases=["bw", "banword"])
    @commands.has_permissions(manage_guild=True)
    async def banwords(self, ctx):
        banwStr = ""
        for word in botData.bannedWords:
            banwStr += f"**{word}**\n"

        embed = discord.Embed(title="List of Prohibited words", description=banwStr, color=discord.Colour.dark_gold())
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        return await ctx.send(embed=embed,
                              reference=ctx.message,
                              mention_author=False)

    @banwords.command(aliases=['+'])
    @commands.has_permissions(manage_guild=True)
    async def add(ctx, *, word):
        if word in botData.bannedWords:
            return await ctx.send(f"`{word}` is already in list of banned words",
                                  reference=ctx.message,
                                  mention_author=False)
        else:
            botData.bannedWords.append(word)
            botFuncs.dumpJson(botData.bannedWords, botFuncs.banWordFile)
            return await ctx.send(f"Successfully added `{word}` to list of banned words",
                                  reference=ctx.message,
                                  mention_author=False)

    @banwords.command(aliases=['-'])
    @commands.has_permissions(manage_guild=True)
    async def remove(ctx, *, word):
        if word in botData.bannedWords:
            botData.bannedWords.remove(word)
            botFuncs.dumpJson(botData.bannedWords, botFuncs.banWordFile)
            return await ctx.send(f"Successfully removed `{word}` from list of banned words",
                                  reference=ctx.message,
                                  mention_author=False)
        else:
            return await ctx.send(f"`{word}` was not found in list of banned words!",
                                  reference=ctx.message,
                                  mention_author=False)

    # todo-false ------------------------------------------ END of banwords command group ----------------------------------- #

    @commands.command(aliases=['pfx'])
    @commands.has_permissions(manage_guild=True)
    async def prefix(self, ctx, prefix):
        try:
            if len(prefix) > 3 or not prefix.isascii() or prefix == '```':
                raise ValueError

            prefixes = botFuncs.loadJson(botFuncs.prefixesFile)
            prefixes[str(ctx.guild.id)] = prefix
            botFuncs.dumpJson(prefixes, botFuncs.prefixesFile)
            await ctx.send(f"Successfully set `{prefix}` as prefix for this guild!",
                           reference=ctx.message,
                           mention_author=False)
        except ValueError:
            responseStr = (f"Maximum length of prefix should be 3 characters! No special characters allowed except ASCII characters\n"
                           f"if you dont know what ASCII characters are, please Google it.")
            await ctx.send(responseStr,
                           reference=ctx.message,
                           mention_author=False)

    # TODO-false ---------------------------------------------------------- Switches Group Commands -----------------------------------------------------------------#

    @commands.group(invoke_without_command=True, aliases=['switches', 'swt'])
    @commands.has_permissions(manage_guild=True)
    async def switch(self, ctx):
        fullDict = botFuncs.loadJson(botFuncs.switchesFile)
        embed = discord.Embed(title="Displaying Switches and data".title(), color=discord.Colour.dark_gold())
        for key, value in fullDict.items():
            embed.add_field(name=f"{key}", value=f"{value}", inline=False)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        return await ctx.send(embed=embed,
                              reference=ctx.message,
                              mention_author=False)

    @switch.command(aliases=['filter', 'fswitch'])
    @commands.has_permissions(manage_guild=True)
    async def filter_switch(self, ctx, operator):
        fullDict = botFuncs.loadJson(botFuncs.switchesFile)
        if operator == '+':
            fullDict['filterSwitch'] = True
            botFuncs.dumpJson(fullDict, botFuncs.switchesFile)
            await ctx.send(f'Message scanning for filtered words is Activated!', delete_after=6,
                           reference=ctx.message,
                           mention_author=False)
            await asyncio.sleep(5)
            await ctx.message.delete()
        elif operator == '-':
            fullDict['filterSwitch'] = False
            botFuncs.dumpJson(fullDict, botFuncs.switchesFile)
            await ctx.send(f'Message scanning for filtered words is turned off.', delete_after=6,
                           reference=ctx.message,
                           mention_author=False)
            await asyncio.sleep(5)
            await ctx.message.delete()

    @switch.command(aliases=['pswitch', 'psw'])
    @commands.has_permissions(manage_guild=True)
    async def p_switch(self, ctx, operator):
        fullDict = botFuncs.loadJson(botFuncs.switchesFile)
        if operator == '+':
            fullDict['pinSwitch'] = True
            botFuncs.dumpJson(fullDict, botFuncs.switchesFile)
            await ctx.send(f"Bot feature 'Pin on Reactions' Activated!", delete_after=6,
                           reference=ctx.message,
                           mention_author=False)
        elif operator == '-':
            fullDict['pinSwitch'] = False
            botFuncs.dumpJson(fullDict, botFuncs.switchesFile)
            await ctx.send(f"Bot feature 'Pin on Reactions' Deactivated!", delete_after=6,
                           reference=ctx.message,
                           mention_author=False)

    @switch.command(aliases=['delsnipe', 'dsnipe'])
    @commands.has_permissions(manage_guild=True)
    async def del_snipe_switch(self, ctx, operator):
        fullDict = botFuncs.loadJson(botFuncs.switchesFile)
        if operator == '+':
            fullDict['del_snipe_switch'] = True
            botFuncs.dumpJson(fullDict, botFuncs.switchesFile)
            await ctx.send(f"Bot feature 'Snipe Deleted Message' Activated!", delete_after=6,
                           reference=ctx.message,
                           mention_author=False)
        elif operator == '-':
            fullDict['del_snipe_switch'] = False
            botFuncs.dumpJson(fullDict, botFuncs.switchesFile)
            await ctx.send(f"Bot feature 'Snipe Deleted Message' Deactivated!", delete_after=6,
                           reference=ctx.message,
                           mention_author=False)

    @switch.command(aliases=['editsnipe', 'esnipe'])
    @commands.has_permissions(manage_guild=True)
    async def edit_snipe_switch(self, ctx, operator):
        fullDict = botFuncs.loadJson(botFuncs.switchesFile)
        if operator == '+':
            fullDict['edit_snipe_switch'] = True
            botFuncs.dumpJson(fullDict, botFuncs.switchesFile)
            await ctx.send(f"Bot feature 'Snipe Edited Message' Activated!", delete_after=6,
                           reference=ctx.message,
                           mention_author=False)
        elif operator == '-':
            fullDict['edit_snipe_switch'] = False
            botFuncs.dumpJson(fullDict, botFuncs.switchesFile)
            await ctx.send(f"Bot feature 'Snipe Edited Message' Deactivated!", delete_after=6,
                           reference=ctx.message,
                           mention_author=False)

    @switch.command(aliases=['reactlimit', 'rlimit'])
    @commands.has_permissions(manage_guild=True)
    async def reactionsLimit_setter(self, ctx, limit: int):
        fullDict = botFuncs.loadJson(botFuncs.switchesFile)
        fullDict['reactLimit'] = limit
        botFuncs.dumpJson(fullDict, botFuncs.switchesFile)
        await ctx.send(f"Pin on Reactions : Reaction Limit changed to `{limit} reactions`",
                       reference=ctx.message,
                       mention_author=False)

    @switch.command(aliases=['drlimit', 'diffreact', 'difflimit'])
    @commands.has_permissions(manage_guild=True)
    async def diffReactionsLimit_setter(self, ctx, limit: int):
        fullDict = botFuncs.loadJson(botFuncs.switchesFile)
        fullDict['diffReactLimit'] = limit
        botFuncs.dumpJson(fullDict, botFuncs.switchesFile)
        await ctx.send(f"Pin on Reactions : Number of different reactions limit changed to `{limit} Different reactions`",
                       reference=ctx.message,
                       mention_author=False)

    # Todo-false-------------------------------------------------------- END of Switches Group Commands ---------------------------------------------------------------#

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
            await ctx.send(f'`{member.name}` was Kicked from `{ctx.guild.name}`, `Reason = {reason}.`',
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
            await ctx.send(f'`{member_tag}` was banned from `{ctx.guild.name}`, `Reason = {reason}.`',
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


    # todo-false ----------------------------------------------- Role Command Group -----------------------------------------------------------#

    @commands.group(invoke_without_command=True, aliases=['roles'])
    @commands.has_permissions(manage_roles=True)
    async def role(self, ctx):
        bot_prefix = botFuncs.get_local_prefix(ctx.message)
        await ctx.send("Command Usage:\n"
                       f"`{bot_prefix}role (add|remove) (user) (role)`",
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

    # todo-false --------------------------------------------- END of Role Command Group ------------------------------------------------------#
    
    
def setup(client):
    client.add_cog(ModCommands(client))