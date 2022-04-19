import discord
import botFuncs
import botData
import time
import mongodbUtils
import random
import asyncio
import tttgame
import numpy as np
from datetime import datetime
from discord.ext import commands
from asyncUtils import log_and_raise


class GameCommands(commands.Cog):
    def __init__(self,client:discord.Client):
        self.client = client


    @commands.command(name="hangman", aliases=["hm"])
    async def hangman(self, ctx: commands.Context):
        timeout = 90
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
                    return await ctx.send("Timeout reached, Game terminated.")
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

    @commands.group(name="tictactoe",aliases=['ttt'],invoke_without_command=True)
    async def tictactoe(self,ctx:commands.Context,difficulty='medium'):
        prefix = mongodbUtils.get_local_prefix(ctx.message)
        timeout = 120
        difficulty = difficulty.lower()
        difficulties = [('e','ez','easy'),('m','mid','medium'),('h','hrd','hard')]
        dlevel = None
        for i,diff in enumerate(difficulties):
             if difficulty in diff:
                 dlevel = i

        if dlevel is None:
            return await ctx.send("Game Terminated.\n"
                                  "Invalid argument for difficulty level. Difficulties are `{easy|medium|hard}` or `{e|m|h}`.\n"
                                  f"use command `{prefix}tictactoe help` to know more")

        bot_name = str(self.client.user).split('#')[0]
        plays = 0
        matrix = np.array([[0] * 3 for _i in range(3)])
        sides = [(0, 1), (1, 2), (2, 1), (1, 0)]
        corners = [(0, 0), (0, 2), (2, 2), (2, 0)]
        middle = (1, 1)
        user = 2
        comp = 1
        won = False
        draw = False
        symbols = [":black_large_square:",":o:",":x:"]
        available_slots = []

        ref_msg = await ctx.send(f":o: `{bot_name}`\n"
                                 f"v/s\n"
                                 f":x: `{ctx.author.display_name}`\n"
                                 f"Difficulty : `{difficulties[dlevel][2].capitalize()}`")


        def matrixToStr(matrix):
            st = ''
            for i in range(3):
                for j in range(3):
                    st += symbols[matrix[i,j]]
                st += '\n'
            return st

        # Opposite corners for given side
        opp_corners = {
            sides[0]: ((2, 0), (2, 2)),
            sides[1]: ((0, 0), (2, 0)),
            sides[2]: ((0, 0), (0, 2)),
            sides[3]: ((0, 2), (2, 2))
        }

        # Opposite corner for given corner
        c2c_opp = {
            corners[0]: corners[2],
            corners[2]: corners[0],
            corners[1]: corners[3],
            corners[3]: corners[1]
        }

        for i in range(3):
            for j in range(3):
                available_slots.append(tuple((i, j)))

        turn = random.randint(0,1)

        while (not won) and (not draw):
            if len(available_slots)==9:
                await ctx.send(matrixToStr(matrix))

            userind = None
            if turn % 2 == 1:
                inptext = f"Enter co-ordinates (use `{prefix}tictactoe help` if you don't know how the coordinates work): "
                if plays>2:
                    inptext = "Enter co-ordinates: "
                await ctx.send(inptext)
                try:
                    def check(msg:discord.Message):
                        c1 = ctx.author.id == msg.author.id and ctx.channel.id == msg.channel.id
                        if not c1:
                            return False
                        if msg.content.lower() == "quit":
                            raise ValueError
                        c2 = msg.content.isnumeric() and len(msg.content)<3
                        if c2:
                            if int(msg.content) in range(33+1):
                                l = list(msg.content)
                                return tuple((int(l[0])-1,int(l[1])-1)) in available_slots
                            else:
                                return False
                        else:
                            return False
                    inpmsg:discord.Message = await self.client.wait_for(event='message',check=check,timeout=timeout)
                except Exception as err:
                    if isinstance(err,asyncio.TimeoutError):
                        return await ctx.send("Timeout reached, Game terminated",reference=ref_msg)
                    if isinstance(err,ValueError):
                        return await ctx.send(f"{ctx.author.display_name} left the game, Game Terminated.",reference=ref_msg)
                else:
                    inpList = list(inpmsg.content)
                    userind = tuple((int(inpList[0])-1,int(inpList[1])-1))

                matrix[userind] = user
                plays += 1
                available_slots.remove(userind)
                won = tttgame.winner(matrix, user)
                if won:
                    await ctx.send(matrixToStr(matrix))
                    await ctx.send("You WON! :tada:")
                    continue
                if len(available_slots) == 0:
                    await ctx.send(matrixToStr(matrix))
                    await ctx.send("It's a Draw")
                    draw = True
                    continue
            else:
                await ctx.send(f"{bot_name}'s turn")
                if dlevel == 0:
                    compind = random.choice(available_slots)
                elif dlevel == 1:
                    compind = tttgame.onestepaway(matrix,comp)
                    if not compind:
                        compind = tttgame.onestepaway(matrix,user)
                    if not compind:
                        compind = random.choice(available_slots)
                else:
                    if plays == 0:
                        compind = random.choice(corners)
                    else:
                        compind = tttgame.onestepaway(matrix, comp)
                        if not compind:
                            compind = tttgame.onestepaway(matrix, user)
                        if not compind:
                            # play on middle when more than 3 plays are done and middle is still empty
                            if middle in available_slots or plays == 0:
                                compind = middle
                            else:
                                two_corners = None
                                for corner in corners:
                                    if matrix[c2c_opp[corner]] == user and matrix[corner] == user and matrix[middle] == comp:
                                        two_corners = (corner, c2c_opp[corner])
                                if two_corners:
                                    filtered_sides = list(filter(lambda x: x in available_slots, sides))
                                    compind = random.choice(filtered_sides)
                                else:
                                    if userind in corners:
                                        if c2c_opp[userind] in available_slots:
                                            compind = c2c_opp[userind]
                                        else:
                                            if middle in available_slots:
                                                compind = middle
                                            else:
                                                compind = random.choice(available_slots)
                                    else:
                                        if userind in sides:
                                            compind = random.choice(opp_corners[userind])
                                            if compind not in available_slots:
                                                if middle in available_slots:
                                                    compind = middle
                                                else:
                                                    compind = random.choice(available_slots)
                                        else:
                                            filetered_corners = list(filter(lambda x: x in available_slots, corners))
                                            compind = random.choice(filetered_corners) if len(
                                                filetered_corners) > 0 else None
                                            if compind not in available_slots or not compind:
                                                if middle in available_slots:
                                                    compind = middle
                                                else:
                                                    compind = random.choice(available_slots)

                matrix[compind] = comp
                plays += 1
                available_slots.remove(compind)
                await ctx.send(matrixToStr(matrix))
                won = tttgame.winner(matrix, comp)
                if won:
                    await ctx.send("You lost :frowning:")
                    continue
                if len(available_slots) == 0:
                    await ctx.send("It's a Draw")
                    draw = True
                    continue
            turn += 1

    @tictactoe.command(name="2p")
    @commands.guild_only()
    async def t3_2p(self,ctx:commands.Context,member:discord.Member):
        p1:discord.Member = ctx.author
        p2 = member
        ref_msg = await ctx.send(f":o: `{p1.display_name}`\n"
                                 f"v/s\n"
                                 f":x: `{p2.display_name}`")

        prefix = mongodbUtils.get_local_prefix(ctx.message)
        timeout = 120
        matrix = np.array([[0]*3 for _i in range(3)])
        n1 = 1
        n2 = 2
        won = False
        draw = False
        symbols = [":black_large_square:", ":o:", ":x:"]
        available_slots = []

        def matrixToStr(matrix):
            st = ''
            for i in range(3):
                for j in range(3):
                    st += symbols[matrix[i, j]]
                st += '\n'
            return st

        for i in range(3):
            for j in range(3):
                available_slots.append(tuple((i, j)))

        turn = random.randint(0,1)
        pleft:discord.Member = None
        while (not won) and (not draw):
            await ctx.send(matrixToStr(matrix))
            inptext = f"Enter co-ordinates (use `{prefix}tictactoe help` if you don't know how the coordinates work): "
            if len(available_slots) < 8:
                inptext = "Enter co-ordinates: "
            p1ind = None
            p2ind = None
            plays = 0
            if turn % 2 == 0:
                await ctx.send(f"{p1.display_name}'s Turn")
                await ctx.send(inptext)
                try:
                    def check1(msg: discord.Message):
                        if not ctx.channel.id==msg.channel.id:
                            return False
                        if msg.content.lower() == "quit" and (msg.author.id==p1.id or msg.author.id == p2.id):
                            if msg.author.id == p1.id:
                                raise ValueError(p1.display_name)
                            else:
                                raise ValueError(p2.display_name)
                        c1 = msg.author.id == p1.id
                        if not c1:
                            return False
                        c2 = msg.content.isnumeric() and len(msg.content) < 3
                        if c2:
                            if int(msg.content) in range(33 + 1):
                                l = list(msg.content)
                                return tuple((int(l[0]) - 1, int(l[1]) - 1)) in available_slots
                            else:
                                return False
                        else:
                            return False

                    inpmsg: discord.Message = await self.client.wait_for(event='message', check=check1, timeout=timeout)
                except Exception as err:
                    if isinstance(err,asyncio.TimeoutError):
                        return await ctx.send("Timeout reached, Game terminated",reference=ref_msg)
                    if isinstance(err,ValueError):
                        return await ctx.send(f"{err.args[0]} left the game, Game Terminated.",reference=ref_msg)
                else:
                    inpList = list(inpmsg.content)
                    p1ind = tuple((int(inpList[0]) - 1, int(inpList[1]) - 1))

                matrix[p1ind] = n1
                plays += 1
                available_slots.remove(p1ind)
                won = tttgame.winner(matrix, n1)
                if won:
                    await ctx.send(matrixToStr(matrix))
                    await ctx.send(f"{p1.display_name} WON! :tada:")
                    continue
                if len(available_slots) == 0:
                    await ctx.send(matrixToStr(matrix))
                    await ctx.send("It's a Draw")
                    draw = True
                    continue
            else:
                await ctx.send(f"{p2.display_name}'s Turn")
                await ctx.send(inptext)

                try:
                    def check2(msg: discord.Message):
                        if not ctx.channel.id==msg.channel.id:
                            return False
                        if msg.content.lower() == "quit" and (msg.author.id==p1.id or msg.author.id == p2.id):
                            if msg.author.id == p1.id:
                                raise ValueError(p1.display_name)
                            else:
                                raise ValueError(p2.display_name)
                        c1 = msg.author.id == p2.id
                        if not c1:
                            return False
                        c2 = msg.content.isnumeric() and len(msg.content) < 3
                        if c2:
                            if int(msg.content) in range(33 + 1):
                                l = list(msg.content)
                                return tuple((int(l[0]) - 1, int(l[1]) - 1)) in available_slots
                            else:
                                return False
                        else:
                            return False

                    inpmsg: discord.Message = await self.client.wait_for(event='message', check=check2, timeout=timeout)
                except Exception as err:
                    if isinstance(err,asyncio.TimeoutError):
                        return await ctx.send("Timeout reached, Game terminated",reference=ref_msg)
                    if isinstance(err,ValueError):
                        return await ctx.send(f"{err.args[0]} left the game, Game Terminated.",reference=ref_msg)
                else:
                    inpList = list(inpmsg.content)
                    p2ind = tuple((int(inpList[0]) - 1, int(inpList[1]) - 1))

                matrix[p2ind] = n2
                plays += 1
                available_slots.remove(p2ind)
                won = tttgame.winner(matrix, n2)
                if won:
                    await ctx.send(matrixToStr(matrix))
                    await ctx.send(f"{p2.display_name} WON! :tada:")
                    continue
                if len(available_slots) == 0:
                    await ctx.send(matrixToStr(matrix))
                    await ctx.send("It's a Draw")
                    draw = True
                    continue
            turn += 1

    @tictactoe.command(name="help")
    async def t3help(self,ctx):
        prefix = mongodbUtils.get_local_prefix(ctx.message)
        textstr = ("```\n"
                   "Commands:\n"
                   f"  {prefix}tictactoe {{easy|meduim|hard}} -> play Tictactoe against Bot with easy/medium/hard difficulties (default mode is medium)\n"
                   f"  {prefix}tictactoe 2p {{@user}} -> play Tictactoe with a friend\n"
                   f"  {prefix}tictactoe help -> get some help SMH\n"
                   f"  quit -> while game is going on, enter this to end/leave the game\n\n"
                   "Co-ordinate system of Tictactoe game:\n"
                   "1,1   1,2   1,3\n"
                   "2,1   2,2   2,3\n"
                   "3,1   3,2   3,3\n\n"
                   "Note: \n"
                   "> While entering coordinates just enter the numbers without comma ','\n"
                   " eg: Instead of entering \"2,3\", just enter \"23\".\n"
                   "> you can write 'ttt' as alternative for 'tictactoe'\n"
                   "> you can write 'e','m','h' as alternatives for 'easy','medium','hard' respectively.\n"
                   "> exclude the {} brackets."
                   "```")
        return await ctx.send(textstr)

    @commands.group(name='typing',aliases=["type"],invoke_without_command=True)
    async def typing_test(self,ctx:commands.Context,numWords=25,topwords=100):
        if topwords not in [100,1000]:
            topwords = 100
        if numWords < 10:
            numWords = 10
        elif numWords > 50:
            numWords = 50

        timeout = 60
        wordsList = botFuncs.loadJson(f"./Data Files/topwords{topwords}.json")
        words = [random.choice(wordsList) for _ in range(numWords)]
        typing_str = " ".join(words)
        main_msg = await ctx.send(f"```\n"
                                    f"Mode            : Random words\n"
                                    f"Number of words : {numWords}\n"
                                    f"Words chosen from top {topwords} used words in English\n\n"
                                    f"Text to type:\n"
                                    f"{typing_str}\n"
                                    f"```")

        def check_typing(channel:discord.TextChannel,user:discord.User,when:datetime):
            if channel.id == ctx.channel.id and user.id == ctx.author.id:
                return True
            else:
                return False
        try:
            ch,usr,ts1 = await self.client.wait_for(event="typing",check=check_typing,timeout=timeout)
        except asyncio.TimeoutError:
            return await ctx.send("Timeout reached, Typing game terminated.", reference=main_msg)
        else:
            ts1:datetime = ts1.timestamp()
            await main_msg.add_reaction("🕰️")

        def check_result(msg:discord.Message):
            if msg.channel.id == ctx.channel.id and ctx.author.id == msg.author.id:
                if msg.content.lower() == "quit":
                    raise ValueError
                return True
            else:
                return False

        try:
            res_msg = await self.client.wait_for(event="message",check=check_result,timeout=timeout*3)
        except Exception as err:
            if isinstance(err,asyncio.TimeoutError):
                await main_msg.clear_reaction("🕰️")
                return await ctx.send("Typing result was not submitted within 3 minutes. Game terminated", reference=main_msg)
            if isinstance(err,ValueError):
                return await ctx.send(f"Game terminated.", reference=main_msg)
        else:
            ts2 = datetime.utcnow().timestamp()
            await main_msg.clear_reaction("🕰️")

        total_time = ts2-ts1
        res_words = res_msg.content.split(" ")
        res_str = res_msg.content
        accuracy = 0
        addstr = ""
        for i in range(min(len(typing_str), len(res_str))):
            if res_str[i] == typing_str[i]:
                accuracy += 1
        if len(res_str) < len(typing_str):
            addstr = "Typing Incomplete, results are only calculated for the part which you typed\n"

        accuracy = (accuracy/len(typing_str))*100
        xfactor = 60/total_time
        wpm = len(res_words)*xfactor
        cpm = len(res_str) * xfactor

        return await ctx.send(f"```\n{addstr}"
                              f"Accuracy   : {int(accuracy)}%\n"
                              f"Time Taken : {total_time:.2f} seconds\n"
                              f"wpm        : {wpm:.2f}\n"
                              f"cpm        : {cpm:.2f}\n"
                              f"```",reference=res_msg,mention_author=False)

    @typing_test.command(name="quotes",aliases=["quote","q"])
    async def quotes_typing(self,ctx:commands.Context,lower_case='default'):
        timeout = 60
        qlist = botFuncs.loadJson(botData.quotesFile)
        qdict = random.choice(qlist)
        if lower_case.lower() in ['lower', 'low', 'l']:
            qdict['text'] = qdict['text'].lower()
        typing_str = qdict['text']
        q_author = qdict['author'] if qdict['author'] else "Unknown"
        main_msg = await ctx.send("```\n"
                                  f"Mode : Quotes {'(lowercase)' if lower_case.lower() in ['lower','low','l'] else ''}\n"
                                  f"Quote author : {q_author}\n\n"
                                  f"Quote to type:\n"
                                  f"{typing_str}\n"
                                  f"```")

        def check_typing(channel:discord.TextChannel,user:discord.User,when:datetime):
            if channel.id == ctx.channel.id and user.id == ctx.author.id:
                return True
            else:
                return False
        try:
            ch,usr,ts1 = await self.client.wait_for(event="typing",check=check_typing,timeout=timeout)
        except asyncio.TimeoutError:
            return await ctx.send("Timeout reached, Typing game terminated.", reference=main_msg)
        else:
            ts1:datetime = ts1.timestamp()
            await main_msg.add_reaction("🕰️")

        def check_result(msg:discord.Message):
            if msg.channel.id == ctx.channel.id and ctx.author.id == msg.author.id:
                if msg.content.lower() == "quit":
                    raise ValueError
                return True
            else:
                return False

        try:
            res_msg = await self.client.wait_for(event="message",check=check_result,timeout=timeout*3)
        except Exception as err:
            if isinstance(err,asyncio.TimeoutError):
                await main_msg.clear_reaction("🕰️")
                return await ctx.send("Typing result was not submitted within 3 minutes. Game terminated", reference=main_msg)
            if isinstance(err,ValueError):
                return await ctx.send(f"Game terminated.", reference=main_msg)
        else:
            ts2 = datetime.utcnow().timestamp()
            await main_msg.clear_reaction("🕰️")

        total_time = ts2-ts1
        res_words = res_msg.content.split(" ")
        res_str = res_msg.content
        accuracy = 0
        addstr = ""
        for i in range(min(len(typing_str), len(res_str))):
            if res_str[i] == typing_str[i]:
                accuracy += 1
        if len(res_str) < len(typing_str):
            addstr = "Typing Incomplete, results are only calculated for the part which you typed\n"

        accuracy = (accuracy/len(typing_str))*100
        xfactor = 60/total_time
        wpm = len(res_words)*xfactor
        cpm = len(res_str) * xfactor

        return await ctx.send(f"```\n{addstr}"
                              f"Accuracy   : {int(accuracy)}%\n"
                              f"Time Taken : {total_time:.2f} seconds\n"
                              f"wpm        : {wpm:.2f}\n"
                              f"cpm        : {cpm:.2f}\n"
                              f"```",reference=res_msg,mention_author=False)

    @typing_test.command(name="help")
    async def typing_help(self,ctx:commands.Context):
        prefix = mongodbUtils.get_local_prefix(ctx.message)
        return await ctx.send(f"```\n"
                              f"Typing practice commands:\n"
                              f"{prefix}typing {{n}} {{tn}} -> Gives you text to type for 'n' number of words for top 'tn' number of words used in English.\n"
                              f"{prefix}typing (quotes|quote|q) -> Gives a random quote to type.\n"
                              f"{prefix}typing help -> this command....\n\n"
                              f"Note:\n"
                              f"\t * You can enter 'type' instead of 'typing'\n"
                              f"\t * {{}} -> optional values\n"
                              f"\t * () -> required values\n"
                              f"\t * default values for 'n' and 'tn' are 25,100 respectively"
                              f"\t * 'n' can be in range of 10-50\n"
                              f"\t * 'tn' should be either 100 or 1000\n"
                              f"```",reference=ctx.message,mention_author=False)

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
    client.add_cog(GameCommands(client))