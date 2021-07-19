import discord
import random
import requests
import os
import re
from discord.ext import commands
import asyncio
#-------------------------------------------------- My Files - Imports --------------------------------------------------#
import botFuncs
import botData
#---------------------------------------- To get ENVIRONMENT variables from .env ----------------------------------------#
import dotenv
dotenv.load_dotenv()
#------------------------------------------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------------------------------------------------#
cwd = os.getcwd()
banWordFile = (cwd+"/Data Files/bannedWords.data")
prefixFile = (cwd+"/Data Files/prefix.data")
#------------------------------------------------------------------------------------------------------------------------#
botFuncs.createFiles()
bot_prefix = "$"
operatorList = ["+","-","*"] # --> List of operators used in different commands to add , remove and show respectively
#------------------------------------------------------------------------------------------------------------------------#
client = commands.Bot(command_prefix=bot_prefix ,
                      help_command= None,
                      intents = discord.Intents.all())

@client.event
async def on_ready():
    print(f'{client.user} is online and ready to go.')
    print(f'Current Bot prefix is : {bot_prefix}')


@client.event
async def on_message(message):
    global bot_prefix
    # Data to extract from each message
    fUserName = str(message.author)
    userName = fUserName.split("#")[0]
    fullMsgList = str(message.content).split(" ")
    lowerMsgList = [word.lower() for word in fullMsgList]
    channelName = str(message.channel)

    if message.author == client.user:
        return


    #TODO-false------------------------------------------------ Banned Words Warning -------------------------------------------------#
    if not fullMsgList[0] == (f'{bot_prefix}banword'):
        """if user is using banword command then dont execute this warning code"""

        if any(bnword in lowerMsgList for bnword in botData.bannedWords):
            await message.add_reaction("❗")
            await message.channel.send(f"{userName} Watch your language!")
            return

    if message.content.startswith(f"<@!{client.user.id}>"):
        await message.add_reaction("👍")
        await message.channel.send(f"Yes {message.author.mention}, Im up and running!")
        return

    await client.process_commands(message=message)


@client.command()
async def help(ctx):
    helpPrompt = botData.helpPromt_func(bot_prefix)
    await ctx.send(helpPrompt)


@client.command(aliases = ["mh"])
@commands.has_permissions(manage_guild = True)
async def mod_help(ctx):
    modHelpPrompt = botData.modHlelpPromt_func(bot_prefix)
    await ctx.send(modHelpPrompt)

#TODO-false ----------------------------------------- MOD COMMANDS -----------------------------------------#
@client.command(aliases = ["bw"])
@commands.has_permissions(manage_guild = True)
async def banword(ctx,*args):
    try:
        operator = args[0]
        banWord = args[1].lower()
        cmdWord = args[1].lower()
    except:
        banwStr = (f'```\n{ctx.author.name},That\'s the Incorrect usage of command {bot_prefix}banword\n'
                   f'correct usage:\n'
                   f'{bot_prefix}banword {{opertaor}} {{word}}\n'
                   f'operator : + , -\n'
                   f'+ to add the word to banned words list\n'
                   f'- to remove the word from banned words list\n'
                   f'Util:\n'
                   f'{bot_prefix}banword * show\n'
                   f'shows all banned words'
                   f'```')
        await ctx.send(banwStr)
        return


    if operator == "+":
        if banWord not in botData.bannedWords:
            botData.bannedWords.append(banWord.lower())
            botFuncs.dumpJson(botData.bannedWords, banWordFile)
            banwStr = f'Added {banWord} to banned list.'
            await ctx.message.add_reaction("✅")
        else:
            banwStr = f'{banWord} is already in banned words list.'
    elif operator == "-":
        if banWord in botData.bannedWords:
            botData.bannedWords.remove(banWord)
            botFuncs.dumpJson(botData.bannedWords, banWordFile)
            banwStr = f'Removed {banWord} from the banned words list.'
            await ctx.message.add_reaction("✅")
        else:
            banwStr = f"can't delete something which is not in banned words' list."
    elif operator == "*" and cmdWord == "show":
        banwStr = '```\nList of Banned words:\n'
        i = 1
        for bword in botData.bannedWords:
            banwStr += f'{i}. {bword}\n'
            i += 1
        banwStr += '```'
        await ctx.message.add_reaction("✅")

    await ctx.send(banwStr)


@client.command(aliases = ["p"])
@commands.has_permissions(manage_messages = True)
async def purge(ctx,amount: int = 1 ):
    if amount < 0:
        await ctx.message.add_reaction("❓")
        await ctx.send("Can't delete negative number of messages!", delete_after = 2.5)
    else:
        amount += 1
        await ctx.channel.purge(limit=amount)
        await ctx.send(f'Deleted `{amount - 1}` messages',delete_after = 2.5)



@client.command(aliases = ["m"])
@commands.has_permissions(manage_channels = True)
async def mute(ctx,member: discord.Member):
    listOfGuildRoles = ctx.guild.roles
    listMemberRoles = member.roles

    # Getting the position of highest role of user to be muted
    highestMemberRole_pos = listMemberRoles[len(listMemberRoles)-1].position

    for role in listOfGuildRoles:
        if role.name.lower() == 'muted':
            muted_role = role
            break
    m_pos = muted_role.position

    # Puts the muted role just above user's highes role , if user's highest role is above muted role
    if m_pos < highestMemberRole_pos:
        await muted_role.edit(position = highestMemberRole_pos)
        await ctx.send("Moved Muted role.")

    await member.add_roles(muted_role)
    await ctx.message.add_reaction("✅")
    await ctx.send(f'{member.mention} was Muted!')


@client.command(aliases = ["unm"])
@commands.has_permissions(manage_channels = True)
async def unmute(ctx,member: discord.Member):
    listOfGuildRoles = ctx.guild.roles

    for role in listOfGuildRoles:
        if role.name.lower() == 'muted':
            muted_role = role
            break

    await member.remove_roles(muted_role)
    await ctx.message.add_reaction("✅")
    await ctx.send(f'{member.mention} was Unmuted!')


@client.command(aliases = ["k"])
@commands.has_permissions(kick_members = True)
async def kick(ctx,member: discord.Member,*,reason = "No Reason Provided"):
    await member.send(f'You were kicked from {ctx.guild.name}, Reason : {reason}')
    await member.kick(reason=reason)
    await ctx.message.add_reaction("✅")
    await ctx.send(f'`{member.name}` was Kicked from `{ctx.guild.name}`.')


@client.command(aliases = ["b"])
@commands.has_permissions(ban_members = True)
async def ban(ctx,member: discord.Member,*,reason = "No Reason Provided"):
    await member.send(f'You were banned from {ctx.guild.name}, Reason : {reason}')
    await member.ban(reason=reason)
    await ctx.message.add_reaction("✅")
    await ctx.send(f'`{member.mention}` was banned from `{ctx.guild.name}`.')


@client.command(aliases = ["unb"])
@commands.has_permissions(ban_members = True)
async def unban(ctx,*,member):
    member_name,member_disc = member.split("#")
    ban_entriesList = await ctx.guild.bans()

    for ban_entry in ban_entriesList:
        user = ban_entry.user
        if (user.name,user.discriminator) == (member_name,member_disc):
            await ctx.guild.unban(user)
            await ctx.message.add_reaction("✅")
            await ctx.send(f'{user} was Unbanned!')
            return

    await ctx.message.add_reaction("❌")
    await ctx.send(f'{member} not found in this guild\'s banned list.')
    return

#TODO-false ------------------------------------------- Commands For Users ------------------------------------------------#

#TODO-false ------------------------------------------- Utility Commands --------------------------------------------------#
@client.command(aliases = ['ref'])
async def regfind(ctx,emailORdisctag,operator,*,text):

    toFind = emailORdisctag.lower()
    operator_present = operator == "--"
    find_in = text
    command_ok = toFind == "email" or toFind == "disctag"

    if command_ok and operator_present:
        if toFind == "email":
            matches = re.findall(r'[\w%./-]+@[a-zA-Z0-9]+[-]*[a-zA-Z0-9]*\.com', find_in)
            toFind = "Email"
        elif toFind == "disctag":
            matches = re.findall(r'[\w%!.&*-]+#\d{4}',find_in)
            toFind = "Discord Tag"

        regResponseStr = (f'```\n{len(matches)} Possible {toFind} matches were extracted from the given text.\n')
        i = 1
        for match in matches:
            regResponseStr += f'{toFind}-{i} : {match}\n'
            i += 1
        regResponseStr += '```'
    else:
        regResponseStr = ('Incorrect usage of command `regfind`\n'
                     f'{ctx.author.name}, correct usage is:\n'
                     f'```\n'
                     f'{bot_prefix}regfind {{email | disctag}} -- {{Your text here}}\n'
                     f'\nUsage:\n'
                     f'| --> or\n'
                     '{} exclude the brackets\n'
                     '```')
    await ctx.send(regResponseStr)


@client.command(aliases = ['gif'])
async def tenorgif(ctx,*,category):
    """
    Gets a Random GIF from tenor, in a requested Category
    """
    gifsList = botFuncs.getTenorList(category)
    embed = discord.Embed(title=f"Random GIF in Category : {category.title()}",description=f"**Requested by {ctx.author.mention}**", color= discord.Colour.gold())
    embed.set_image(url = random.choice(gifsList))
    await ctx.send(embed = embed)


@client.command()
async def code(ctx,format,*,code):
    codeResponse = (f'```{format}\n'
                    f'{code}'
                    f'\n```')
    await ctx.send(codeResponse)


#TODO-false ----------------------------------------------- Fun Commands --------------------------------------------------#

@client.command(aliases = ['fax'])
async def funfax(ctx,thing,*,quality):
    await ctx.message.add_reaction("👀")
    await ctx.send(f'{thing} is {botFuncs.genRand()}% {quality}!')


@client.command(aliases = ['say'])
async def sneak(ctx,*,messageTosay):
    await ctx.message.delete()
    await ctx.send(messageTosay)


@client.command(aliases = ['sus', 'amoggus'])
async def suspicious(ctx,member: discord.Member):
    susStr = random.choice(botData.susList)
    await ctx.message.add_reaction("🤨")
    await ctx.send(f'{member.mention} {susStr}')


@client.command(aliases = ["dvc"])
async def device(ctx,member:discord.Member):
    if member.is_on_mobile():
        for reaxn in botData.reactionsList:
            await ctx.message.add_reaction(reaxn)
        await ctx.send(f'{member.mention} is a Cringe mobile user lol.')
    else:
        await ctx.message.add_reaction("🙌")
        await ctx.send(f'{member.mention} is a Chad PCMR member , **RESPECT!!**')


@client.command(aliases = ["dm"])
async def direct_anonymous(ctx,member:discord.Member,*,message):
    user = member
    await user.send(message)
    await ctx.send("Done")


@client.command(aliases = ['dmid'])
async def dm_withID(ctx,memberID:int,*,message):
    user = await client.fetch_user(memberID)
    await user.send(message)
    await ctx.send("Done.")


BOT_TOKEN = os.environ['BOT_TOKEN']

client.run(BOT_TOKEN)