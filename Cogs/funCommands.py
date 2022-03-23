import discord
import botFuncs
import botData
import mongodbUtils
import random
import asyncio
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

    @commands.command(name="hangman", aliases=["hm"])
    async def hangman(self, ctx: commands.Context):
        timeout = 90
        word_list = None
        with open(botData.wordsFile, 'r') as f:
            word_list = botFuncs.loadJson(botData.wordsFile)

        word = random.choice(word_list)
        tempword = word.lower()
        blanks = "_" * len(word)
        spacedstr = lambda string: " ".join(list(string))
        chances = 7
        alphabets = "".join([chr(x) for x in range(97, 123)])
        yolo = ''
        while type(yolo) != int:
            try:
                await ctx.send("```\n"
                               "Note: Respond to each message within 90 seconds or else your message will not be counted towards input\n\n"
                               "1. Play classic hangman where you enter only 1 character at a time with 7 lives.\n"
                               "2. YOLO : Enter Full word but you have only 1 life, point of no return.\n"
                               "Select 1 or 2: ```")

                def check1(msg: discord.Message):
                    if not msg.content.isnumeric():
                        return False
                    usercheck = ctx.author.id == msg.author.id and ctx.channel.id == msg.channel.id
                    inpcheck = msg.content.isnumeric() and int(msg.content) in range(1, 3)
                    return usercheck and inpcheck

                try:
                    yolomsg = await self.client.wait_for(event='message',check=check1,timeout=timeout)
                except asyncio.TimeoutError:
                    pass
                else:
                    yolo = int(yolomsg.content)
            except ValueError:
                return await ctx.send("Invalid response, Game terminated.")

        if yolo == 1:
            msgstr = (f"```\n{spacedstr(blanks)}\n```\n"
                      f"```\nRemaining Alphabets: {spacedstr(alphabets)}\n```\n"
                      f"*{chances} chances remaining.*")
            await ctx.send(msgstr)
            while chances != 0:
                await ctx.send("Enter a character:")

                def check2(msg: discord.Message):
                    usercheck = ctx.author.id == msg.author.id and ctx.channel.id == msg.channel.id
                    inpcheck = msg.content.isalpha() and len(msg.content) == 1
                    return usercheck and inpcheck

                try:
                    guessMsg = await self.client.wait_for(event='message',check=check2,timeout=timeout)
                except asyncio.TimeoutError:
                    pass
                else:
                    guess = guessMsg.content.lower()
                    indx = alphabets.find(guess)
                    if indx >= 0:
                        alphabets = list(alphabets)
                        alphabets[indx] = ""
                        alphabets = "".join(alphabets)
                    else:
                        await ctx.send("you have already entered that alphabet before, try again.")
                        continue

                    count = 0
                    intx = tempword.find(guess.lower())
                    while intx >= 0:
                        if count == 0:
                            chances += 1
                            count += 1
                        tempword = list(tempword)
                        blanks = list(blanks)
                        blanks[intx] = word[intx]
                        tempword[intx] = "_"
                        tempword = "".join(tempword)
                        blanks = "".join(blanks)
                        intx = tempword.find(guess.lower())

                    msgstr2 = f"```\n{spacedstr(blanks)}\n```\n"
                    if blanks == word:
                        await ctx.send(msgstr2)
                        break

                    chances -= 1
                    msgstr2 += (f"```\nRemaining Alphabets: {spacedstr(alphabets)}\n```\n"
                                f"*{chances} chances remaining.*")
                    await ctx.send(msgstr2)

            if chances == 0:
                await ctx.send(f"You lost, the word was `{word}`.")
            else:
                await ctx.send(f"Congratulations you guessed it, the word is `{word}`.")

        else:
            inta = random.randint(0, len(word) - 1)
            intb = random.randint(0, len(word) - 1)
            while intb == inta:
                intb = random.randint(0, len(word) - 1)
            tempword = list(tempword)
            blanks = list(blanks)
            tempword[inta], tempword[intb] = "_", "_"
            blanks[inta], blanks[intb] = word[inta], word[intb]
            tempword = "".join(tempword)
            blanks = "".join(blanks)

            msgstr = f"```{spacedstr(blanks)}```\n"
            msgstr += "Enter the full word, Don't worry about capitalization: "
            await ctx.send(msgstr)

            def yCheck(msg: discord.Message):
                return ctx.author.id == msg.author.id and ctx.channel.id == msg.channel.id

            try:
                fullwordmsg = await self.client.wait_for(event='message',check=yCheck,timeout=timeout)
            except asyncio.TimeoutError:
                pass
            else:
                inpword = fullwordmsg.content
            if inpword.lower() == word.lower():
                await ctx.send(f"Congratulations you guessed it in YOLO mode, the word is `{word}`.")
            else:
                await ctx.send(f"Better luck next time, +1 respect for YOLO attempt, the word was `{word}`.")

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
            await log_and_raise(client=self.client, ctx=ctx, error=error)


def setup(client):
    client.add_cog(FunCommands(client))
