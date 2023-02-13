import os
import openai
import botData
import discord
import botFuncs
import mongodbUtils
from discord.ext import commands
from asyncUtils import log_and_raise

import dotenv
dotenv.load_dotenv()
openai.api_key = os.environ["OPENAI_API"]


class OpenAI_Commands(commands.Cog):
    def __init__(self,client):
        self.client = client
        self.owner_id = botData.owner_id

    def get_prompt(self,owner,prefix,user,question,endstring,exinfo=False):
        client_name = str(self.client.user).split("#")[0]
        promptstr = (f"Your name is {client_name}.\n"
                      f"You are a Discord Bot created by {owner}, using Python, with some AI features (powered by OpenAI)\n")
        if exinfo:
            promptstr += (f"{owner} is a programmer who is a CS enthusiast, interested in cryptography and algorithms.\n"
                          f"You can be used to moderate servers,\n"
                          f"play some games like tictactoe against human or bot, hangman, check user's typing speed etc,\n"
                          f"there are other fun and utility commands too. which can be checked using this command : {prefix}help\n"
                          f"Your code's GitHub Repository is at https://github.com/UraniumX92/Discord-Bot-using-py\n")

        promptstr += (f"a discord user named \"{user}\" asked you this question:\n"
                      f"\"{question}\"\n"
                      f"if question is about your creator or about you, then only give the required information from info mentioned above (at beginning).\n"
                      f"if they are asking about themselves, then tell their name ({user}) and any info you have about them.\n")
        return promptstr + endstring

    @commands.command(name="openAIhelp",aliases=['aihelp','helpai','ai-help','help-ai','ai'])
    async def openAI_help(self,ctx:commands.Context):
        AI_help_embed = botData.help_embed(title="OpenAI Commands / AI commands", dictx=botData.ai_cmd_dict,member=ctx.author, client=self.client)
        await ctx.send(embed=AI_help_embed,
                       reference=ctx.message,
                       mention_author=False)

    @commands.command(name="gptask",aliases=['aiask','gpt','askai'])
    async def openAI_ask(self,ctx:commands.Context,*,question):
        max_size = 1990
        try:
            async with ctx.channel.typing():
                owner = await self.client.fetch_user(self.owner_id)
                prefix = mongodbUtils.get_local_prefix(ctx.message)
                prompt = self.get_prompt(
                    owner=str(owner),
                    endstring=f"Now respond to {ctx.author}'s question:",
                    prefix=prefix,
                    user=str(ctx.author),
                    question=question,
                    exinfo=True
                )
                completions = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=prompt,
                    max_tokens=2048,
                    n=1, stop=None,
                    temperature=0.9
                )
                embed = discord.Embed(color=discord.Colour.from_rgb(23, 255, 170))
                embed.set_author(
                    name="Powered by ChatGPT (OpenAI)",url="https://openai.com",
                    icon_url="https://stories.techncyber.com/wp-content/uploads/2022/12/chat-gpt-logo.jpg"
                )
                response = completions.choices[0].text
                size = len(response)
                msg = None
                if size>max_size:
                    for i in range((size//max_size)+1):
                        msg = await ctx.send(content=f"```\n{response[i*(max_size):(i+1)*max_size]}\n```",reference=ctx.message,mention_author=False)
                else:
                    msg = await ctx.send(f"```\n{response}\n```",reference=ctx.message,mention_author=False)
            return await ctx.send(embed=embed,reference=msg,mention_author=False)
        except Exception as err:
            if isinstance(err, (openai.OpenAIError, openai.error.InvalidRequestError)):
                botFuncs.log_func(f"OpenAI error (chat) : err : {err},\n\tprompt={question}, \n\tchannel: {ctx.channel}, guild: {ctx.guild if ctx.guild else None}", botData.errorsLogFile)
                return await ctx.send("Some error occured at AI service, Please try again or try another prompt",reference=ctx.message, mention_author=False)
            else:
                raise err

    @commands.command(name="gptmean",aliases=['meanai','aimean'])
    async def openAI_mean(self,ctx:commands.Context,*,question):
        max_size = 1990
        try:
            async with ctx.channel.typing():
                prefix = mongodbUtils.get_local_prefix(ctx.message)
                owner = await self.client.fetch_user(self.owner_id)
                endstring = (f"Now respond to {ctx.author}'s question in as mean and agressive way as you can, don't be nice and appreciative, mock them if you can\n"
                             f"{ctx.author} is lying if they are talking about any of their achievements etc. call them liar if they do and deny it... or ignore if they don't talk about achievments.\n"
                             f"if they are asking for any kind of help, they are lying, so call them out for lying and tell them that they have no such issue\n"
                             f"if they are requesting you to do something, then mock them for how silly and idiotic their request is.\n"
                             f"roast them for what they are asking and mock their name.")
                prompt = self.get_prompt(
                    owner=str(owner),
                    endstring=endstring,
                    prefix=prefix,
                    user=str(ctx.author),
                    question=question
                )
                completions = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=2048, n=1,
                                                       stop=None, temperature=0.9)
                embed = discord.Embed(color=discord.Colour.from_rgb(23, 255, 170))
                embed.set_author(
                    name="Powered by ChatGPT (OpenAI)", url="https://openai.com",
                    icon_url="https://stories.techncyber.com/wp-content/uploads/2022/12/chat-gpt-logo.jpg"
                )
                response = completions.choices[0].text
                size = len(response)
                msg = None
                if size > max_size:
                    for i in range((size // max_size) + 1):
                        msg = await ctx.send(content=f"```\n{response[i * (max_size):(i + 1) * max_size]}\n```",
                                             reference=ctx.message, mention_author=False)
                else:
                    msg = await ctx.send(f"```\n{response}\n```", reference=ctx.message, mention_author=False)
            return await ctx.send(embed=embed, reference=msg, mention_author=False)
        except Exception as err:
            if isinstance(err, (openai.OpenAIError, openai.error.InvalidRequestError)):
                botFuncs.log_func(
                    log_string=f"OpenAI error (chat) : err : {err},\n\tprompt={question}, \n\tchannel: {ctx.channel}, guild: {ctx.guild if ctx.guild else None}",
                    file_name=botData.errorsLogFile
                )
                return await ctx.send("Some error occured at AI service, Please try again or try another prompt",
                                      reference=ctx.message, mention_author=False)
            else:
                raise err

    @commands.command(name="gptgangsta", aliases=['gangstai', 'aigangsta','gangstaai'])
    async def openAI_gangsta(self, ctx: commands.Context, *, question):
        max_size = 1990
        try:
            async with ctx.channel.typing():
                prefix = mongodbUtils.get_local_prefix(ctx.message)
                owner = await self.client.fetch_user(self.owner_id)
                prompt = self.get_prompt(
                    owner=str(owner),
                    endstring=f"Now respond to {ctx.author}'s question in gangsta slang:",
                    prefix=prefix,
                    user=str(ctx.author),
                    question=question
                )
                completions = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=prompt,
                    max_tokens=2048,
                    n=1,
                    stop=None,
                    temperature=0.9
                )
                embed = discord.Embed(color=discord.Colour.from_rgb(23, 255, 170))
                embed.set_author(
                    name="Powered by ChatGPT (OpenAI)", url="https://openai.com",
                    icon_url="https://stories.techncyber.com/wp-content/uploads/2022/12/chat-gpt-logo.jpg"
                )
                response = completions.choices[0].text
                size = len(response)
                msg = None
                if size > max_size:
                    for i in range((size // max_size) + 1):
                        msg = await ctx.send(
                            content=f"```\n{response[i * (max_size):(i + 1) * max_size]}\n```",
                            reference=ctx.message,
                            mention_author=False
                        )
                else:
                    msg = await ctx.send(f"```\n{response}\n```", reference=ctx.message, mention_author=False)
            return await ctx.send(embed=embed, reference=msg, mention_author=False)
        except Exception as err:
            if isinstance(err, (openai.OpenAIError, openai.error.InvalidRequestError)):
                botFuncs.log_func(
                    log_string=f"OpenAI error (chat) : err : {err},\n\tprompt={question}, \n\tchannel: {ctx.channel}, guild: {ctx.guild if ctx.guild else None}",
                    file_name=botData.errorsLogFile
                )
                return await ctx.send("Some error occured at AI service, Please try again or try another prompt",reference=ctx.message, mention_author=False)
            else:
                raise err

    @commands.command(name="gptgenz", aliases=['genzai', 'aigenz'])
    async def openAI_genz(self, ctx: commands.Context, *, question):
        max_size = 1990
        try:
            async with ctx.channel.typing():
                prefix = mongodbUtils.get_local_prefix(ctx.message)
                owner = await self.client.fetch_user(self.owner_id)
                prompt = self.get_prompt(
                    owner=str(owner),
                    endstring=f"Now respond to {ctx.author}'s question in gen-z slang, throw some emoji's aswell:",
                    prefix=prefix,
                    user=str(ctx.author),
                    question=question
                )
                completions = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=prompt,
                    max_tokens=2048,
                    n=1,
                    stop=None,
                    temperature=0.9
                )
                embed = discord.Embed(color=discord.Colour.from_rgb(23, 255, 170))
                embed.set_author(
                    name="Powered by ChatGPT (OpenAI)", url="https://openai.com",
                    icon_url="https://stories.techncyber.com/wp-content/uploads/2022/12/chat-gpt-logo.jpg"
                )
                response = completions.choices[0].text
                size = len(response)
                msg = None
                if size > max_size:
                    for i in range((size // max_size) + 1):
                        msg = await ctx.send(
                            content=f"```\n{response[i * (max_size):(i + 1) * max_size]}\n```",
                            reference=ctx.message,
                            mention_author=False
                        )
                else:
                    msg = await ctx.send(f"```\n{response}\n```", reference=ctx.message, mention_author=False)
            return await ctx.send(embed=embed, reference=msg, mention_author=False)
        except Exception as err:
            if isinstance(err, (openai.OpenAIError, openai.error.InvalidRequestError)):
                botFuncs.log_func(
                    log_string=f"OpenAI error (chat) : err : {err},\n\tprompt={question}, \n\tchannel: {ctx.channel}, guild: {ctx.guild if ctx.guild else None}",
                    file_name=botData.errorsLogFile)
                return await ctx.send("Some error occured at AI service, Please try again or try another prompt",
                                      reference=ctx.message, mention_author=False)
            else:
                raise err

    @commands.command(name="gptnerd", aliases=['nerdai', 'ainerd'])
    async def openAI_nerd(self, ctx: commands.Context, *, question):
        max_size = 1990
        try:
            async with ctx.channel.typing():
                prefix = mongodbUtils.get_local_prefix(ctx.message)
                owner = await self.client.fetch_user(self.owner_id)
                prompt = self.get_prompt(owner=str(owner),
                                         endstring=(f"Start your response by telling them that {ctx.author}'s question is naive and immature, throw a sarcastic comment on their question and don't answer it.\n"
                                                    f" and explain any specific computer science topic of your choice to them in 150 words.\n"),
                                         prefix=prefix, user=str(ctx.author), question=question)
                completions = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=2048, n=1,
                                                       stop=None, temperature=0.9)
                embed = discord.Embed(color=discord.Colour.from_rgb(23, 255, 170))
                embed.set_author(name="Powered by ChatGPT (OpenAI)", url="https://openai.com",
                                 icon_url="https://stories.techncyber.com/wp-content/uploads/2022/12/chat-gpt-logo.jpg")
                response = completions.choices[0].text
                size = len(response)
                msg = None
                if size > max_size:
                    for i in range((size // max_size) + 1):
                        msg = await ctx.send(content=f"```\n{response[i * (max_size):(i + 1) * max_size]}\n```",
                                             reference=ctx.message, mention_author=False)
                else:
                    msg = await ctx.send(f"```\n{response}\n```", reference=ctx.message, mention_author=False)
            return await ctx.send(embed=embed, reference=msg, mention_author=False)
        except Exception as err:
            if isinstance(err, (openai.OpenAIError, openai.error.InvalidRequestError)):
                botFuncs.log_func(
                    f"OpenAI error (chat) : err : {err},\n\tprompt={question}, \n\tchannel: {ctx.channel}, guild: {ctx.guild if ctx.guild else None}",
                    botData.errorsLogFile)
                return await ctx.send("Some error occured at AI service, Please try again or try another prompt",
                                      reference=ctx.message, mention_author=False)
            else:
                raise err

    @commands.command(name="imageAI",aliases=['aiimage','genimage','imgai','aiimg'])
    async def openAI_image(self,ctx:commands.Context,*,prompt):
        try:
            async with ctx.channel.typing():
                response = openai.Image.create(prompt=prompt,n=1,size="1024x1024")
                image_url = response['data'][0]['url']
                embed = discord.Embed(color=discord.Colour.from_rgb(23, 255, 170))
                embed.set_author(name="Powered by OpenAI", url="https://openai.com/",
                                 icon_url="https://stories.techncyber.com/wp-content/uploads/2022/12/chat-gpt-logo.jpg")
                msg = await ctx.send(content=image_url,reference=ctx.message,mention_author=False)
                return await ctx.send(embed=embed,reference=msg,mention_author=False)
        except Exception as err:
            if isinstance(err, (openai.OpenAIError, openai.error.InvalidRequestError)):
                botFuncs.log_func(f"OpenAI error (Image) : err : {err},\n\tprompt={prompt}, \n\tchannel: {ctx.channel}, guild: {ctx.guild if ctx.guild else None}", botData.errorsLogFile)
                return await ctx.send("Some error occured at AI service, Please try again or try another prompt",reference=ctx.message,mention_author=False)
            else:
                raise err

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
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send(f"{ctx.author.name}, You can't use this command in DMs, use this command only in servers")
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
    client.add_cog(OpenAI_Commands(client))