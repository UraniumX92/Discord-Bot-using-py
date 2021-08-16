import discord
import botFuncs
import botData
from discord.ext import commands
import os


class DevCommands(commands.Cog):
    def __init__(self,client):
        self.client = client
        self.owner_id = botData.owner_id


    # todo-false ------------------------------------------- Developer -- command group -------------------------------------------- #
    # display, add or remove a user from bot-dev list
    @commands.group(invoke_without_command=True, aliases=['dev', 'devs'])
    @commands.check(botFuncs.is_dev)
    async def developers(self, ctx):
        devsList = botData.devsList
        devStr = ""
        i = 1
        for id, discTag in devsList.items():
            devStr += f"**{i}.  `{discTag}` -- `{id}`**\n"
            i += 1
        embed = discord.Embed(title="List of Bot Developers", description=devStr, color=discord.Colour.dark_gold())
        embed.set_thumbnail(url=self.client.user.avatar_url)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed, reference=ctx.message, mention_author=False)

    @developers.command(aliases=['+'])
    @commands.check(botFuncs.is_dev)
    async def add(self, ctx, member: discord.Member):
        
        if member.id == self.owner_id and ctx.author.id != self.owner_id:
            return await ctx.send(f"Haha nice try {ctx.author.name}, I am loyal to my owner, i won't do that",
                                  reference=ctx.message,
                                  mention_author=True)
        elif member.id == self.owner_id and ctx.author.id == self.owner_id:
            return await ctx.send("Your Position is fixed in devs list, can't add or remove you 🙂",
                                  reference=ctx.message,
                                  mention_author=False)

        devsList = botData.devsList
        if str(member.id) in devsList.keys():
            return await ctx.send(f"`{member}` is already in Bot-devs list!",
                                  reference=ctx.message,
                                  mention_author=False)
        else:
            devsList[str(member.id)] = str(member)
            botFuncs.dumpJson(devsList, botFuncs.devsListFile)
            return await ctx.send(f"`{member}` Successfully added to Bot-Devs list!", reference=ctx.message, mention_author=False)

    @developers.command(aliases=['-'])
    @commands.check(botFuncs.is_dev)
    async def remove(self, ctx, member: discord.Member):
        
        if member.id == self.owner_id and ctx.author.id != self.owner_id:
            await ctx.message.add_reaction("😂")
            return await ctx.send(f"Haha nice try {ctx.author.name}, I am loyal to my Owner, I won't do that!",
                                  reference=ctx.message,
                                  mention_author=True)
        elif member.id == self.owner_id and ctx.author.id == self.owner_id:
            return await ctx.send("Your Position is fixed in devs list, can't add or remove you 🙂",
                                  reference=ctx.message,
                                  mention_author=False)

        devsList = botData.devsList
        if str(member.id) in devsList.keys():
            devsList.pop(str(member.id))
            botFuncs.dumpJson(devsList, botFuncs.devsListFile)
            return await ctx.send(f"`{member}` was successfully removed from Bot-devs list!",
                                  reference=ctx.message,
                                  mention_author=False)
        else:
            return await ctx.send(f"`{member}` was not found in Bot-devs list!", reference=ctx.message, mention_author=False)

    # todo-false ----------------------------------------- END of Developer command group -------------------------------------------------- #
    
    # todo-false --------------------------------------------------- Logs command group ---------------------------------------------------- #
    @commands.group(invoke_without_command=True)
    @commands.check(botFuncs.is_dev)
    async def logs(self, ctx):
        # Sends the errorLogs.txt file as a discord.File
        fileName = "errorLogs.txt"
        logfile = discord.File(botFuncs.errorsLogFile, fileName)
        await ctx.send(content=f"`{fileName}` Requested by `{ctx.author}`\nFetched at time: `{botFuncs.getDateTime()}`",
                       file=logfile,
                       reference=ctx.message,
                       mention_author=False)

    @logs.command(aliases=['msg', 'message'])
    @commands.check(botFuncs.is_dev)
    async def messages(self, ctx):
        # Sends the errorMessages.txt file as discord.File
        fileName = "errorMessages.txt"
        msglogfile = discord.File(botFuncs.errMessageLogFile, fileName)
        return await ctx.send(content=f"`{fileName}` Requested by `{ctx.author}`\nFetched at time : `{botFuncs.getDateTime()}`",
                              file=msglogfile,
                              reference=ctx.message,
                              mention_author=False)

    @logs.command(aliases=['clear'])
    @commands.check(botFuncs.is_dev)
    async def clear_logs(self,ctx,*,file):
        errLogs_aliases = ['errorlogs','logs','errors','errorLogs.txt']
        errMessage_aliases = ['msglogs','messagelogs','errormessages','errorMessages.txt']

        if file in errLogs_aliases:
            with open(botFuncs.errorsLogFile,"w") as f:
                f.write(f"Error Logs Cleared at [{botFuncs.getDateTime()}]\n")
            f.close()
            return await ctx.send("Cleared `errorLogs.txt`",
                           reference=ctx.message,
                           mention_author=False)
        elif file in errMessage_aliases:
            with open(botFuncs.errMessageLogFile,"w") as f:
                f.write(f"Error Message Logs Cleared at [{botFuncs.getDateTime()}]\n")
            f.close()
            return await ctx.send("Cleared `errorMessages.txt`",
                                  reference=ctx.message,
                                  mention_author=False)
        else:
            return await ctx.send("Wrong file name/alias\n"
                                  f"```py\n"
                                  f"errLogs_aliases = {errLogs_aliases}\n"
                                  f"errMessage_aliases = {errMessage_aliases}\n"
                                  f"```")

    # todo-false -------------------------------------------------- END of Logs command group ------------------------------------------------ #

    # todo-false -------------------------------------------------- get files command -------------------------------------------------- #
    @commands.command(name='getfile',aliases=['getf'])
    @commands.check(botFuncs.is_dev)
    async def get_files(self, ctx, *, path=None):

        if not path:
            listdir = os.listdir('./')
            to_remove = ['pyDiscBot.code-workspace', '__pycache__','poetry.lock','pyproject.toml']
            listdir = [x for x in listdir if x[0] != "." and x not in to_remove]

            fileStr = ""
            for item in listdir:
                fileStr += f"**`{item}`**\n"

            cogStr = ""
            cogslist = os.listdir("./Cogs")
            cogs_listdir = [x for x in cogslist if x not in to_remove]
            for cog in cogs_listdir:
                cogStr += f"**`{cog}`**\n"

            dataStr = ""
            dataFiles_listdir = os.listdir("./Data Files")
            for dfile in dataFiles_listdir:
                dataStr += f"**`{dfile}`**\n"

            errStr = ""
            errLogs_listdir = os.listdir("./Err Logs")
            for errFile in errLogs_listdir:
                errStr += f"**`{errFile}`**\n"

            embed = discord.Embed(title="List of files in Bot's Source Code Repository", color=discord.Colour.dark_gold())
            embed.add_field(name="Main Directory:", value=fileStr, inline=False)
            embed.add_field(name="/Cogs/ :", value=cogStr, inline=False)
            embed.add_field(name="/Data Files/ :", value=dataStr, inline=False)
            embed.add_field(name="/Err Logs/ :", value=errStr, inline=False)
            return await ctx.send(embed=embed,
                                  reference=ctx.message,
                                  mention_author=False)
        else:
            try:
                file_path = f"./{path}"
                file_to_send = discord.File(file_path)

                if not file_to_send:
                    raise FileNotFoundError

                return await ctx.send(file=file_to_send,
                                      reference=ctx.message,
                                      mention_author=False)
            except Exception as error:
                if isinstance(error, FileNotFoundError):
                    return await ctx.send(f"No such file or directory: `{path}`",
                                          reference=ctx.message,
                                          mention_author=False)
                elif isinstance(error, PermissionError):
                    return await ctx.send(f"Permission Denied by system, can't send that file, if requested a directory, can't send the directory as `discord.File`.",
                                          reference=ctx.message,
                                          mention_author=False)
                else:
                    raise error


def setup(client):
    client.add_cog(DevCommands(client))