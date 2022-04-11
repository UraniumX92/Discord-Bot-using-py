import botData
import mongodbUtils
from discord.ext import commands
from asyncUtils import log_and_raise


class HelpCommands(commands.Cog):
    def __init__(self,client):
        self.client :commands.Bot = client

    @commands.group(invoke_without_command=True)
    async def help(self, ctx):
        prefix = mongodbUtils.get_local_prefix(ctx.message)
        help_Embed = botData.help_embed(title="Help Commands",dictx=botData.help_cmd_dict,member=ctx.author,client=self.client)
        help_Embed.add_field(name='\u200b',value=f"**Invite Bot to your Server using `{prefix}invite` Command**")
        await ctx.send(embed=help_Embed,
                       reference=ctx.message,
                       mention_author=False)


    @help.command(name="fun")
    async def fun_help(self,ctx):
        fun_help_embed = botData.help_embed(title="Fun Commands",dictx=botData.fun_cmd_dict,member=ctx.author,client=self.client)
        await ctx.send(embed=fun_help_embed,
                       reference=ctx.message,
                       mention_author=False)


    @help.command(name="utility",aliases=['util'])
    async def util_help(self,ctx):
        util_help_embed = botData.help_embed(title="Utility Commands",dictx=botData.util_cmd_dict,member=ctx.author,client=self.client)
        await ctx.send(embed=util_help_embed,
                       reference=ctx.message,
                       mention_author=False)


    @help.command(name='moderators',aliases=["mod","mods"])
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def mod_help(self, ctx):
        modHelp_Embed = botData.help_embed(title="Moderator Commands",dictx=botData.modCmdDescription_dict,member=ctx.author,client=self.client)
        await ctx.send(embed=modHelp_Embed,
                       reference=ctx.message,
                       mention_author=False)


    @help.command(name='developers',aliases=['dev','devs'])
    @commands.check(mongodbUtils.is_dev)
    async def dev_help(self, ctx):
        devHelp_Embed = botData.help_embed(title="Developer Commands",dictx=botData.devCmdDescription_dict,member=ctx.author,client=self.client)
        await ctx.send(embed=devHelp_Embed,
                       reference=ctx.message,
                       mention_author=False)


    @help.command(name="custom")
    async def custom_command_help(self,ctx):
        cust_help_cmd = self.client.get_command(name="custom")
        return await ctx.invoke(cust_help_cmd)


    @help.command(name="reddit")
    async def reddit_command_help(self,ctx):
        reddit_help_cmd = self.client.get_command(name="reddit")
        return await ctx.invoke(reddit_help_cmd)


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
        elif isinstance(error,commands.NoPrivateMessage):
            await ctx.send(f"{author.mention}, You are not allowed to use this command in Direct Messages, use this command only in Servers!")
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
    client.add_cog(HelpCommands(client))
