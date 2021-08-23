import discord
from discord.ext import commands
import botFuncs
import botData
import mongodbUtils
from asyncUtils import log_and_raise
import asyncio
import os
import re
import random
from datetime import datetime


class UtilityCommands(commands.Cog):
    def __init__(self,client):
        self.client = client
        self.owner_id = botData.owner_id

    @commands.command(aliases=['regf'])
    async def regfind(self, ctx, emailORdisctag, operator, *, text):
        prefix = mongodbUtils.get_local_prefix(ctx.message)
        toFind = emailORdisctag.lower()
        operator_present = operator == "--"
        find_in = text
        command_ok = toFind == "email" or toFind == "disctag"
        try:
            if command_ok and operator_present:
                if toFind == "email":
                    matches = re.findall(r'[\w%./-]+@[a-zA-Z]+[-]*[a-zA-Z]*\.com', find_in)
                    toFind = "Email"
                elif toFind == "disctag":
                    matches = re.findall(r'[\w%!.&*-]+#\d{4}', find_in)
                    toFind = "Discord Tag"

                regResponseStr = (f'```\n{len(matches)} Possible {toFind} matches were extracted from the given text.\n')
                i = 1
                for match in matches:
                    regResponseStr += f'{toFind}-{i} : {match}\n'
                    i += 1
                regResponseStr += '```'
            else:
                raise ValueError
            await ctx.send(regResponseStr,
                           reference=ctx.message,
                           mention_author=False)
        except:
            regResponseStr = ('Incorrect usage of command `regfind`\n'
                              f'{ctx.author.name}, correct usage is:\n'
                              f'```\n'
                              f'{prefix}regfind {{email | disctag}} -- {{Your text here}}\n'
                              f'\nUsage:\n'
                              f'| --> or\n'
                              '{} exclude the brackets\n'
                              '```')
            await ctx.send(regResponseStr,
                           reference=ctx.message,
                           mention_author=False)

    @commands.command(aliases=['gif'])
    async def tenorgif(self, ctx, *, category):
        """
        Gets a Random GIF from tenor, in a requested Category
        """
        gifsList = botFuncs.getTenorList(category)
        if not gifsList:
            return await ctx.send(f"There was some problem with connecting Bot client to Tenor GIF services, Please try again.",
                                  reference=ctx.message,
                                  mention_author=False)

        embed = discord.Embed(title=f"Random GIF from '{category.title()}' Category.", color=discord.Colour.gold())
        via_tenor_URL = 'https://www.gstatic.com/tenor/web/attribution/PB_tenor_logo_blue_vertical.png'
        embed.set_image(url=random.choice(gifsList))
        embed.set_thumbnail(url=via_tenor_URL)
        author_name = str(ctx.author)
        embed.set_footer(text=f'Requested by {author_name}.', icon_url=ctx.author.avatar_url)
        return await ctx.send(embed=embed,
                              reference=ctx.message,
                              mention_author=False)

    @commands.command(aliases=['pfp', 'pic'])
    async def avatar(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member

        author_tag = str(ctx.author)
        embed = discord.Embed(description=f'**{member.mention}\'s Avatar**', color=discord.Colour.dark_gold())
        embed.set_image(url=member.avatar_url)
        embed.set_footer(text=f'Requested by {author_tag}.', icon_url=ctx.author.avatar_url)

        await ctx.send(embed=embed,
                       reference=ctx.message,
                       mention_author=False)

    @commands.command()
    async def code(self, ctx, format, *, code):
        randStr = f"{botFuncs.genRand()}{botFuncs.genRand()}"
        tempFileName = f'tempfile{randStr}code.txt'
        with open(tempFileName, "w") as f:
            f.write(code)

        with open(tempFileName, "rb") as ft:
            codeFile = discord.File(ft, f'{ctx.author.name}Code.{format}')
            await ctx.send(file=codeFile,
                           reference=ctx.message,
                           mention_author=False)
        os.remove(os.path.join(os.getcwd(), tempFileName))

    @commands.command(aliases=['r'])
    async def react(self, ctx, emoji):
        try:
            ref_message_id = ctx.message.reference.message_id
            ref_msg = await ctx.channel.fetch_message(ref_message_id)
        except AttributeError:
            return await ctx.send(f"{ctx.author.name}, You were supposed to reference a message (reply) with this command!",
                                  reference=ctx.message,
                                  mention_author=False)

        try:  # For default Emojis (Unicode characters) and Guild image emojis
            await ref_msg.add_reaction(emoji)
            await ctx.message.add_reaction("✅")
        except:  # For Guild Emojis which are Animated
            for g_emoji in ctx.guild.emojis:
                if g_emoji.name.lower() == emoji.lower():
                    r_emoji = g_emoji
                    await ref_msg.add_reaction(r_emoji)
                    return await ctx.message.add_reaction("✅")
            await ctx.send("Emoji Not Found.")

        await asyncio.sleep(4)
        await ctx.message.delete()

    @commands.command(aliases=['activ'])
    async def activity(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member
        activities = member.activities
        activity_menu_shown = False
        if len(activities) > 1:
            activity_menu_shown = True
            embed = discord.Embed(title=f'List of {member.name}\'s activities', color=discord.Colour.dark_gold())
            actStr = ""
            i = 1
            for activity in activities:
                actStr += f"**{i}. {activity.name}**\n"
                i += 1
            embed.add_field(name='Activities:', value=actStr, inline=False)
            embed.add_field(name='\u200b', value="**Enter the number corresponding to Activity to show the activity**", inline=False)
            embed.set_thumbnail(url=member.avatar_url)
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
            act_message = await ctx.send(embed=embed,
                                         reference=ctx.message,
                                         mention_author=False)
            try:
                def check(msg: discord.Message):
                    return msg.channel.id == ctx.channel.id and msg.author.id == ctx.message.author.id and str(msg.content).isnumeric()

                waitMsg = await self.client.wait_for(event='message', check=check, timeout=120)
            except asyncio.TimeoutError:
                timeout_message = await ctx.send(f"No activity was selected, Event timed out. use the command again to select activity",
                                                 reference=act_message,
                                                 mention_author=False)
                await asyncio.sleep(5)
                for i in reversed(range(0, 6)):
                    if i == 0:
                        await timeout_message.edit(content="Deleting Now!!")
                    else:
                        await timeout_message.edit(content=f"Deleting the embed in {i} seconds!")
                    await asyncio.sleep(1)

                await timeout_message.delete()
                await act_message.delete()
                return await ctx.message.delete()
            else:
                try:
                    selected_activity = activities[int(waitMsg.content) - 1]
                    await waitMsg.delete()
                except IndexError:
                    return await ctx.send(f"{ctx.author.name}, You were supposed to enter a number in range (1,{len(activities)})",
                                          reference=ctx.message,
                                          mention_author=False)
        else:
            selected_activity = member.activity
        try:
            activity = selected_activity
            if str(activity.name) == "Spotify":
                spotify = selected_activity

                started_song_at = str(spotify.created_at.strftime("%d-%m-%Y %H:%M:%S"))
                song_name = spotify.title
                song_total_duration = str(spotify.duration)[:-3]
                artistsList = spotify.artists
                artists = ", ".join(artistsList)
                album = spotify.album
                song_id = spotify.track_id
                song_duration = str(datetime.utcnow() - spotify.created_at).split(".")[0]
                album_url = spotify.album_cover_url

                embed = discord.Embed(title=f"{member.name}'s Spotify Session", color=discord.Colour.dark_gold())
                embed.add_field(name="Song Name", value=song_name, inline=True)
                embed.add_field(name="Song Duration", value=song_total_duration, inline=True)
                embed.add_field(name="Song Artist(s)", value=artists, inline=False)
                embed.add_field(name="Album Name", value=album, inline=False)
                embed.add_field(name="Song ID on Spotify", value=song_id, inline=False)
                embed.set_thumbnail(url=album_url)

                author_name = str(ctx.author)
                embed.set_footer(text=f'Requested by {author_name}.', icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed,
                               reference=ctx.message,
                               mention_author=False)
            else:
                activity_type = botFuncs.capFistChar(str(activity.type).split('.')[1])
                activity_application = botFuncs.capFistChar(activity.name)
                activity_duration = str(datetime.utcnow() - activity.created_at).split(".")[0]

                embed = discord.Embed(title=f"{member.name}'s Activity:", color=discord.Colour.dark_gold())
                try:
                    acttivT_url = activity.large_image_url
                    if acttivT_url is None:
                        raise ValueError
                    embed.set_thumbnail(url=acttivT_url)
                except:
                    embed.set_thumbnail(url=member.avatar_url)

                embed.add_field(name="Activity Type", value=f"{activity_type}", inline=False)
                embed.add_field(name="Application", value=f"{activity_application}", inline=False)
                embed.add_field(name="Duration", value=activity_duration, inline=False)
                try:
                    activity_details = botFuncs.capFistChar(str(activity.details))
                    if activity_details:
                        embed.add_field(name="Details", value=f"{activity_details}", inline=False)
                except:
                    pass
                embed.set_footer(text=f'Requested by {ctx.author}.', icon_url=ctx.author.avatar_url)
                return await ctx.send(embed=embed,
                                      reference=ctx.message,
                                      mention_author=False)

        except Exception as act_error:
            if isinstance(act_error, TypeError):
                if activity_menu_shown:
                    return await ctx.send(f"Can't Display details of `{selected_activity.name}` Actvity",
                                          reference=ctx.message,
                                          mention_author=False)
                else:
                    return await ctx.send(f"Apparently, {member.name} is not doing any activity right now.",
                                          reference=ctx.message,
                                          mention_author=False)
            elif isinstance(act_error,AttributeError):
                return await ctx.send(f"Apparently, {member.name} is not doing any activity right now.",
                                          reference=ctx.message,
                                          mention_author=False)
            else:
                raise act_error

    @commands.command(aliases=['nick'])
    @commands.has_permissions(change_nickname=True)
    async def set_nick(self, ctx, member: discord.Member, *, newNick=None):
        try:
            await member.edit(nick=newNick)
            await ctx.message.add_reaction("✅")
        except Exception as error:
            if "Missing Permissions" in f"{error.args}":
                raise commands.MissingPermissions("Missing Permissions")
            if "Must be 32 or fewer" in f"{error.args}":
                await ctx.send("Max character limit for nickname is 32!")
            else:
                raise error

    @commands.command(name='invite',aliases=['inv','link'])
    async def get_invite_link(self,ctx):
        bot_name = self.client.user.name
        invite_link = os.environ['BOT_INVITE_LINK']
        embed = discord.Embed(title=f"Invite link for {bot_name} Bot :",
                              description=f"[Click here to invite {bot_name} Bot to your server]({invite_link} \"Click to Invite 🙂\")",
                              color=discord.Colour.dark_gold()
                              )
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed,
                       reference=ctx.message,
                       mention_author=False)


    @commands.command(name='ping')
    async def latency_check(self,ctx):
        latency = self.client.latency
        latency_in_ms = latency*1000
        await ctx.send(f"Pong! Time taken : `{int(latency_in_ms)} ms`",
                       reference=ctx.message,
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

        if isinstance(error, commands.MissingPermissions):
            await ctx.send(f"{ctx.author.mention}, Either you, or Bot is Missing Permission to perform the task.", delete_after=del_after)
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
    client.add_cog(UtilityCommands(client))