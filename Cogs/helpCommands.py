import discord
from discord.ext import commands
import botData
import botFuncs


class HelpCommands(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.command()
    async def help(self, ctx):
        bot_prefix = botFuncs.get_local_prefix(ctx.message)
        help_Embed = botData.helpPrompt_func(ctx.author, self.client, bot_prefix)
        await ctx.send(embed=help_Embed,
                       reference=ctx.message,
                       mention_author=False)

    @commands.command(name='modhelp',aliases=["mh"])
    @commands.has_permissions(manage_guild=True)
    async def mod_help(self, ctx):
        modHelp_Embed = botData.modHelpPrompt_func(ctx.author, self.client)
        await ctx.send(embed=modHelp_Embed,
                       reference=ctx.message,
                       mention_author=False)

    @commands.command(name='devhelp',aliases=['devh'])
    @commands.check(botFuncs.is_dev)
    async def dev_help(self, ctx):
        devHelp_Embed = botData.devHelpPrompt_func(ctx.author, self.client)
        await ctx.send(embed=devHelp_Embed,
                       reference=ctx.message,
                       mention_author=False)


def setup(client):
    client.add_cog(HelpCommands(client))
