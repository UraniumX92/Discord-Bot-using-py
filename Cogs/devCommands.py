import discord
import botFuncs
import botData
import mongodbUtils
import os
import dotenv
from discord.ext import commands
from asyncUtils import log_and_raise

dotenv.load_dotenv('../.env')

class DevCommands(commands.Cog):
    def __init__(self,client):
        self.client : commands.Bot = client
        self.owner_id = botData.owner_id
        self.db = mongodbUtils.db


    # ------------------------------------------- Developer -- command group -------------------------------------------- #
    # display, add or remove a user from bot-dev list
    @commands.group(invoke_without_command=True, aliases=['dev', 'devs'])
    @commands.check(mongodbUtils.is_dev)
    async def developers(self, ctx):
        bot_devs_collection = self.db["bot_devs"]
        dev_docs = bot_devs_collection.find({},{"_id":0})

        embed = discord.Embed(title="List of Bot Developers", color=discord.Colour.dark_gold())
        for i,doc in enumerate(dev_docs):
            try:
                doc["dummy_doc"]
            except:
                user_tag = doc["user_tag"]
                user_id = doc["user_id"]
                added_on = doc["added_on"]
                devStr = f"**{i}.  `{user_tag}` -- `{user_id}`\n Added on: `[{added_on}]`**\n\n"
                embed.add_field(name=f"Developer {i}:",value=devStr,inline=False)

        embed.set_thumbnail(url=self.client.user.avatar_url)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed, reference=ctx.message, mention_author=False)

    @developers.command(aliases=['+'])
    @commands.check(botFuncs.is_owner)
    async def add(self, ctx, user: discord.User):
        """
        Add the mentioned user as bot dev in Data Base
        """
        
        if user.id == self.owner_id and ctx.author.id != self.owner_id:
            return await ctx.send(f"Haha nice try {ctx.author.name}, I am loyal to my owner, i won't do that",
                                  reference=ctx.message,
                                  mention_author=True)
        elif user.id == self.owner_id and ctx.author.id == self.owner_id:
            return await ctx.send("Your Position is fixed in devs list, can't add or remove you 🙂",
                                  reference=ctx.message,
                                  mention_author=False)

        bot_devs_collection = self.db["bot_devs"]
        dev_found = bot_devs_collection.find_one(filter={"user_id" :  (user.id)})
        if dev_found:
            return await ctx.send(f"`{user}` is already in Bot-devs list!",
                                  reference=ctx.message,
                                  mention_author=False)
        else:
            mongodbUtils.add_dev(user)
            return await ctx.send(f"`{user}` Successfully added to Bot-Devs list!", reference=ctx.message, mention_author=False)

    @developers.command(aliases=['-'])
    @commands.check(botFuncs.is_owner)
    async def remove(self, ctx, user: discord.User):
        """
        Remove the mentioned user from bot devs in Data Base
        """
        
        if user.id == self.owner_id and ctx.author.id != self.owner_id:
            await ctx.message.add_reaction("😂")
            return await ctx.send(f"Haha nice try {ctx.author.name}, I am loyal to my Owner, I won't do that!",
                                  reference=ctx.message,
                                  mention_author=True)
        elif user.id == self.owner_id and ctx.author.id == self.owner_id:
            return await ctx.send("Your Position is fixed in devs list, can't add or remove you 🙂",
                                  reference=ctx.message,
                                  mention_author=False)

        bot_devs_collection = self.db["bot_devs"]
        dev_found = bot_devs_collection.find_one(filter={"user_id": (user.id)})
        if dev_found:
            mongodbUtils.remove_dev(user)
            return await ctx.send(f"`{user}` was successfully removed from Bot-devs list!",
                                  reference=ctx.message,
                                  mention_author=False)
        else:
            return await ctx.send(f"`{user}` was not found in Bot-devs list!", reference=ctx.message, mention_author=False)

    @developers.command(name="+id")
    @commands.check(botFuncs.is_owner)
    async def add_id(self, ctx, user_id:int):
        """
        Add user as bot dev in Data Base, only requires the user.id
        """
        try:
            user = await self.client.fetch_user(user_id=user_id)
        except discord.NotFound:
            return await ctx.send(f"No user found with id : `{user_id}` ",
                                  reference=ctx.message,
                                  mention_author=False)

        if user.id == self.owner_id and ctx.author.id != self.owner_id:
            return await ctx.send(f"Haha nice try {ctx.author.name}, I am loyal to my owner, i won't do that",
                                  reference=ctx.message,
                                  mention_author=True)
        elif user.id == self.owner_id and ctx.author.id == self.owner_id:
            return await ctx.send("Your Position is fixed in devs list, can't add or remove you 🙂",
                                  reference=ctx.message,
                                  mention_author=False)

        bot_devs_collection = self.db["bot_devs"]
        dev_found = bot_devs_collection.find_one(filter={"user_id" : (user.id)})
        if dev_found:
            return await ctx.send(f"`{user}` is already in Bot-devs list!",
                                  reference=ctx.message,
                                  mention_author=False)
        else:
            mongodbUtils.add_dev(user)
            return await ctx.send(f"`{user}` Successfully added to Bot-Devs list!", reference=ctx.message, mention_author=False)

    @developers.command(name="-id")
    @commands.check(botFuncs.is_owner)
    async def remove_id(self, ctx, user_id:int):
        """
        Remove user from bot devs in Data Base, only requires the user.id
        """
        try:
            user = await self.client.fetch_user(user_id=user_id)
        except discord.NotFound:
            return await ctx.send(f"No user found with id : `{user_id}` ",
                                  reference=ctx.message,
                                  mention_author=False)

        if user.id == self.owner_id and ctx.author.id != self.owner_id:
            await ctx.message.add_reaction("😂")
            return await ctx.send(f"Haha nice try {ctx.author.name}, I am loyal to my Owner, I won't do that!",
                                  reference=ctx.message,
                                  mention_author=True)
        elif user.id == self.owner_id and ctx.author.id == self.owner_id:
            return await ctx.send("Your Position is fixed in devs list, can't add or remove you 🙂",
                                  reference=ctx.message,
                                  mention_author=False)

        bot_devs_collection = self.db["bot_devs"]
        dev_found = bot_devs_collection.find_one(filter={"user_id": (user.id)})
        if dev_found:
            mongodbUtils.remove_dev(user)
            return await ctx.send(f"`{user}` was successfully removed from Bot-devs list!",
                                  reference=ctx.message,
                                  mention_author=False)
        else:
            return await ctx.send(f"`{user}` was not found in Bot-devs list!", reference=ctx.message, mention_author=False)


    #   ----------------------------------------- END of Developer command group -------------------------------------------------- #
    
    #   --------------------------------------------------- Logs command group ---------------------------------------------------- #
    @commands.group(invoke_without_command=True,aliases=['log'])
    @commands.check(mongodbUtils.is_dev)
    async def logs(self, ctx):
        # Sends the errorLogs.txt file as a discord.File
        fileName = "errorLogs.txt"
        logfile = discord.File(botData.errorsLogFile, fileName)
        await ctx.send(content=f"`{fileName}` Requested by `{ctx.author}`\nFetched at time: `{botFuncs.getDateTime()}`",
                       file=logfile,
                       reference=ctx.message,
                       mention_author=False)

    @logs.command(aliases=['msg', 'message'])
    @commands.check(mongodbUtils.is_dev)
    async def messages(self, ctx):
        # Sends the errorMessages.txt file as discord.File
        fileName = "errorMessages.txt"
        msglogfile = discord.File(botData.errMessageLogFile, fileName)
        return await ctx.send(content=f"`{fileName}` Requested by `{ctx.author}`\nFetched at time : `{botFuncs.getDateTime()}`",
                              file=msglogfile,
                              reference=ctx.message,
                              mention_author=False)

    @logs.command(aliases=['clear'])
    @commands.check(mongodbUtils.is_dev)
    async def clear_logs(self,ctx,*,file = None):
        errLogs_aliases = ['errorlogs','logs','errors','errorLogs.txt']
        errMessage_aliases = ['msglogs','messagelogs','errormessages','errorMessages.txt']

        if file in errLogs_aliases:
            with open(botData.errorsLogFile,"w") as f:
                f.write(f"Error Logs Cleared at [{botFuncs.getDateTime()}]\n")
            f.close()
            return await ctx.send("Cleared `errorLogs.txt`",
                           reference=ctx.message,
                           mention_author=False)
        elif file in errMessage_aliases:
            with open(botData.errMessageLogFile,"w") as f:
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

    #   -------------------------------------------------- END of Logs command group ------------------------------------------------ #

    #   -------------------------------------------------- get files command -------------------------------------------------- #
    @commands.command(name='getfile',aliases=['getf'])
    @commands.check(mongodbUtils.is_dev)
    async def get_files(self, ctx, *, path=None):
        to_deny = [
            'pyDiscBot.code-workspace',
            '__pycache__',
            'poetry.lock',
            'pyproject.toml',
            'mongotesting.py',
            '.env'
        ]

        if not path:
            listdir = os.listdir('./')

            listdir = [x for x in listdir if x[0] != "." and x not in to_deny]

            fileStr = ""
            for item in listdir:
                fileStr += f"**`{item}`**\n"

            cogStr = ""
            cogslist = os.listdir("./Cogs")
            cogs_listdir = [x for x in cogslist if x not in to_deny]
            for cog in cogs_listdir:
                cogStr += f"**`{cog}`**\n"

            dataStr = ""
            dataFiles_listdir = os.listdir("./Data Files")
            for dfile in dataFiles_listdir:
                dataStr += f"**`{dfile}`**\n"

            eventLogStr = ""
            eventLog_listdir = os.listdir("./Bot Event Logs")
            for evLogFile in eventLog_listdir:
                eventLogStr += f"**`{evLogFile}`**\n"

            errStr = ""
            errLogs_listdir = os.listdir("./Err Logs")
            for errFile in errLogs_listdir:
                errStr += f"**`{errFile}`**\n"

            embed = discord.Embed(title="List of files in Bot's Source Code Repository", color=discord.Colour.dark_gold())
            embed.add_field(name="Main Directory:", value=fileStr, inline=False)
            embed.add_field(name="/Cogs/ :", value=cogStr, inline=False)
            embed.add_field(name="/Data Files/ :", value=dataStr, inline=False)
            embed.add_field(name="/Bot Event Logs/ :", value=eventLogStr, inline=False)
            embed.add_field(name="/Err Logs/ :", value=errStr, inline=False)
            return await ctx.send(embed=embed,
                                  reference=ctx.message,
                                  mention_author=False)
        else:
            try:
                if any(file in path for file in to_deny):
                    raise PermissionError

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

    @commands.command(name='guilds',aliases=['glds','gld','server','servers'])
    @commands.check(mongodbUtils.is_dev)
    async def show_guilds_info(self,ctx):
        guilds = self.client.guilds
        str = ''
        for guild in guilds:
            str+=f"`id: {guild.id}, name: {guild.name}`\n"
        return await ctx.send(str,
                              reference=ctx.message,
                              mention_author=False)

    @commands.command(name="getbotnumber",aliases=['getbotnum','getbnum','getb#','get#'])
    @commands.check(mongodbUtils.is_dev)
    async def get_bot_number(self,ctx):
        owner = self.client.get_user(self.client.owner_id)
        bot_num = int(os.environ['BOT_NUMBER'])
        description = [f"{owner}'s machine","primary repl"]
        return await ctx.send(f"Current bot number : `{bot_num}`, **Running on {description[bot_num]}**",reference=ctx.message,mention_author=False)

    async def cog_command_error(self, ctx, error):
        """
        Command error handler for this cog class
        """
        if isinstance(error, commands.CommandInvokeError):
            error = error.original

        prefix = mongodbUtils.get_local_prefix(ctx.message)
        author = ctx.author
        del_after = 10
        if isinstance(error, commands.CheckFailure):
            await ctx.send(f"{author.mention} you aren't eligible to use this command! Only Bot devs can use this command.", delete_after=del_after,
                           reference=ctx.message,mention_author=False)
        elif isinstance(error, commands.MissingPermissions):
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
    client.add_cog(DevCommands(client))