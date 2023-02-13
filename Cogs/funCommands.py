import discord
import botFuncs
import botData
import mongodbUtils
import random
from discord.ext import commands
from asyncUtils import log_and_raise


class FunCommands(commands.Cog):
    def __init__(self, client: discord.Client):
        self.client = client

    @commands.command(aliases=['fax'])
    async def funfax(self, ctx, thing, *, quality):
        await ctx.message.add_reaction("👀")
        await ctx.send(f'{thing} is {botFuncs.genRand()}% {quality}!',
                       reference=ctx.message,
                       mention_author=False)

    @commands.command(aliases=['say'])
    @commands.guild_only()
    async def sneak(self, ctx, *, messageTosay):
        await ctx.message.delete()
        await ctx.send(messageTosay)

    @commands.command(aliases=['sus', 'amoggus'])
    async def suspicious(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member

        susStr = random.choice(botData.susList)
        await ctx.message.add_reaction("🤨")
        await ctx.send(f'{member.mention} {susStr}',
                       reference=ctx.message,
                       mention_author=False)

    @commands.command(aliases=['platform','status'])
    async def device(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member

        is_offline = str(member.raw_status) == 'offline'

        if is_offline:
            return await ctx.send(f"Apparently, {member.name} seems to be offline right now, Real question is... Are they really offline though?? better find out yourself",
                           reference=ctx.message,
                           mention_author=False)

        on_desktop = str(member.desktop_status) != 'offline'
        on_mobile = str(member.mobile_status) != 'offline'
        on_web = str(member.web_status) != 'offline'
        on_all_platfoms = on_desktop and on_mobile and on_web
        is_offline = str(member.raw_status) == 'offline'

        if member.bot and not is_offline:
            return await ctx.send(f"{member.name} is using Discord on Web, uhh we Bots are always on web :slight_frown:",
                                  reference=ctx.message,
                                  mention_author=False)

        if on_all_platfoms:
            await ctx.message.add_reaction("🤔")
            await ctx.send(f"Yoo {member.name}, Why you using discord on Desktop and Web and on cringe Mobile, idk about others, but STOP using that cringe Mobile 💀",
                           reference=ctx.message,
                           mention_author=False)
        elif on_desktop and on_mobile:
            await ctx.message.add_reaction("🤡")
            await ctx.send(f"{member.name} is using both Desktop and Mobile, i hate the mobile part tho 🤡",
                           reference=ctx.message,
                           mention_author=False)
        elif on_desktop and on_web:
            await ctx.message.add_reaction("🤔")
            await ctx.send(f"Huh?? {member.name} is using Desktop Discord as well as web Discord, Confusing times... atleast they're not using cringe Mobile :joy:",
                           reference=ctx.message,
                           mention_author=False)
        elif on_mobile and on_web:
            await ctx.message.add_reaction("💀")
            await ctx.send(f"BRUH {member.name}, STOP using that cringe mobile , and why using web Discord, use the Desktop Discord and become a Chad! 💀 ",
                           reference=ctx.message,
                           mention_author=False)
        elif on_mobile:
            await ctx.send(f'{member.name} is a Cringe mobile user lol.',
                           reference=ctx.message,
                           mention_author=False)
            for reaxn in botData.reactionsList:
                await ctx.message.add_reaction(reaxn)
        elif on_desktop:
            await ctx.message.add_reaction("🙌")
            await ctx.send(f'{member.name} is a Chad PCMR member , **HUGE RESPECT!!**',
                           reference=ctx.message,
                           mention_author=False)
        elif on_web:
            await ctx.message.add_reaction("😑")
            await ctx.send(f"{member.name} is using Discord on Web, BRUH who uses the web Discord except Bots these days?? 😑\n"
                           f"bruh {member.name} is such a Bot LMAO :joy:",
                           reference=ctx.message,
                           mention_author=False)

    @commands.command(aliases=["dm"])
    async def direct_anonymous(self, ctx, member: discord.Member, *, message):
        try:
            await member.send(message)
            await ctx.send("Successfully sent.",
                           reference=ctx.message,
                           mention_author=False)
        except Exception as error:
            if isinstance(error,AttributeError):
                if "'ClientUser' object has no attribute 'create_dm'" in str(error.args):
                    try:
                        await ctx.author.send("I cannot send DM messages to Myself")
                    except:
                        await ctx.send("I cannot send DM messages to Myself",
                                       delete_after=5)
                else:
                    raise error
            elif "Cannot send messages to this user" in str(error.args):
                try:
                    await ctx.author.send(f"User `{member}` has their DM's disabled, or I cannot access to their DM's, either way... you can't send them message using me :slight_frown:")
                except:
                    await ctx.send(f"User `{member}` has their DM's disabled, or I cannot access to their DM's, either way... you can't send them message using me :slight_frown:",
                                   delete_after=5)
            else:
                raise error

    @commands.command(aliases=['dmid'])
    async def dm_withID(self, ctx, userID: int, *, message):
        member = await self.client.fetch_user(userID)
        try:
            await member.send(message)
            await ctx.send("Successfully sent.",
                           reference=ctx.message,
                           mention_author=False)
        except Exception as error:
            if isinstance(error,AttributeError):
                if "'ClientUser' object has no attribute 'create_dm'" in str(error.args):
                    try:
                        await ctx.author.send("I cannot send DM messages to Myself")
                    except:
                        await ctx.send("I cannot send DM messages to Myself",
                                       delete_after=5)
                else:
                    raise error
            elif "Cannot send messages to this user" in str(error.args):
                try:
                    await ctx.author.send(f"User `{member}` has their DM's disabled, or I cannot access to their DM's, either way... you can't send them message using me :slight_frown:")
                except:
                    await ctx.send(f"User `{member}` has their DM's disabled, or I cannot access to their DM's, either way... you can't send them message using me :slight_frown:",
                                   delete_after=5)
            else:
                raise error

    @commands.command(name="getquote",aliases=['quote','gq'])
    async def getquote(self,ctx:commands.Context):
        qdict = random.choice(botFuncs.loadJson(botData.quotesFile))
        quote = qdict['text']
        author = qdict['author'] if qdict['author'] else "Unknown"
        return await ctx.send(f"***{quote}***\n"
                              f"-{author}",reference=ctx.message,mention_author=False)

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
            await ctx.send(f"{author.mention}, Either you, or Bot is Missing Permission to perform the task.", delete_after=del_after)
        elif isinstance(error,commands.NoPrivateMessage):
            await ctx.send(f"{author.mention}, You are not allowed to use this command in Direct Messages, use this command only in Servers!",delete_after=del_after)
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send(f"{author.mention}, You are supposed to mention a valid Discord user.", delete_after=del_after)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"{author.mention}, Please provide all the arguments Required for the command.\n", delete_after=del_after)
        elif isinstance(error, commands.RoleNotFound):
            await ctx.send(f"Can't find a Role with name : `{error.argument}`")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"Incorrect usage of the command! check what your command does by using `{prefix}help`", delete_after=del_after)
        else:
            await log_and_raise(client=self.client, ctx=ctx, error=error)


def setup(client):
    client.add_cog(FunCommands(client))
