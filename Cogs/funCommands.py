import discord
from discord.ext import commands
import botFuncs
import botData
import random


class FunCommands(commands.Cog):
    def __init__(self,client):
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


    @commands.command(aliases=["platform"])
    async def device(self, ctx, member: discord.Member = None):
        member = ctx.author if not member else member

        if member.is_on_mobile():
            await ctx.send(f'{member.mention} is a Cringe mobile user lol.',
                           reference=ctx.message,
                           mention_author=False)
            for reaxn in botData.reactionsList:
                await ctx.message.add_reaction(reaxn)
        else:
            await ctx.message.add_reaction("🙌")
            await ctx.send(f'{member.mention} is a Chad PCMR member , **RESPECT!!**',
                           reference=ctx.message,
                           mention_author=False)


    @commands.command(aliases=["dm"])
    async def direct_anonymous(self, ctx, member: discord.Member, *, message):
        user = member
        await user.send(message)
        await ctx.send("Successfully sent.",
                       reference=ctx.message,
                       mention_author=False)


    @commands.command(aliases=['dmid'])
    async def dm_withID(self, ctx, userID: int, *, message):
        user = await self.client.fetch_user(userID)
        await user.send(message)
        await ctx.send("Successfully sent.",
                       reference=ctx.message,
                       mention_author=False)


def setup(client):
    client.add_cog(FunCommands(client))