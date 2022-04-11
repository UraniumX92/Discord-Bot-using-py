import discord
from discord.ext import commands
import random
import botData
import redditUtils
import mongodbUtils
from redditUtils import reddit
from asyncUtils import log_and_raise
import asyncio
import prawcore


class RedditCommands(commands.Cog):
    def __init__(self,client):
        self.client : commands.Bot = client
        self.owner_id = botData.owner_id
        self.reddit_logo_url = "https://i.imgur.com/lnnoLD8.png"


    @commands.command(name="meme")
    async def get_meme(self,ctx):
        subreddit = reddit.subreddit("memes")
        hot = list(subreddit.hot(limit=30))

        random_meme = random.choice(hot)
        embed = discord.Embed(title=random_meme.title,description=f"[Link to Reddit post]({random_meme.url} \"{random_meme.title}\")",color=discord.Colour.dark_gold())
        embed.set_image(url=random_meme.url)
        footer_text = (f"Posted by: u/{random_meme.author} | score : {random_meme.score}\n"
                       f"Requested by {ctx.author}")
        embed.set_footer(text=footer_text,icon_url=ctx.author.avatar_url)
        return await ctx.send(embed=embed,
                              reference=ctx.message,
                              mention_author=False)


    @commands.group(name="reddit",invoke_without_command=True)
    async def reddit_main(self,ctx):
        description_str = ("Reddit command allows you to fetch list posts from given subreddit and then you can select the post from list to get detailed view of post.\n"
                           "In below example we are going to use default bot prefix `$` as example, but you have to use your server prefix while using command")
        command_desc = ("`$reddit (subreddit | sub) <subreddit_name> {sort} {limit}`\n"
                        "sort --> types of sorting to do while searching posts in subreddit\n"
                        "  values for sort:\n"
                        "    Top\n"
                        "    Hot\n"
                        "    New\n"
                        "    Controversial\n"
                        "limit --> number of posts to show in list, should be in range of 1 to 30"
                        "syntax:"
                        "  Exclude the brackets `<>`,`()`,`{}`.\n"
                        "`'|'` means `'or'`, for example, `(subreddit | sub)` in this, you can either use `subreddit` or `sub` both means the same thing\n"
                        "`<>` these brackets means: this field is required compulsory\n"
                        "`{}` These bracket means : this field is optional, you can leave these fields empty,\n"
                        "  Bot will automatically fill these fields with default values,\n"
                        "that is : `sort` will be `\"hot\"` and `limit` will be `15` if you don't provide those fields")
        embed = discord.Embed(title="Reddit Command Help",description=description_str,color=discord.Colour.dark_gold())
        embed.add_field(name="Command Usage:",value=command_desc,inline=False)
        embed.set_thumbnail(url=self.reddit_logo_url)
        embed.set_footer(text=f"Requested by {ctx.author}",icon_url=ctx.author.avatar_url)

        return await ctx.send(embed=embed,
                              reference=ctx.message,
                              mention_author=False)


    @reddit_main.command(name="subreddit",aliases=['sub'])
    async def get_sub_with_sort(self,ctx, subreddit, sort="hot" , limit = 15):
        """
        get list of posts from desired subreddit and then select a post from list
        """
        # This is limitation from discord, any field in embed cannot have more than 1024 characters
        embed_field_character_limit = 1024
        # This is not any kind of restriction from discord, its just me slicing the titles so that the embed looks clean if titles are huge
        title_string_limit = 85
        max_limit = 30

        sort = sort.lower()
        if sort not in redditUtils.subreddit_posts_sort_types:
            response_content = "After the name of subreddits, you can select sorting from following types:\n"
            for index , sort_type in enumerate(redditUtils.subreddit_posts_sort_types):
                response_content += f"{index+1}. {sort_type}\n"

            return await ctx.send(response_content,
                                  reference=ctx.message,
                                  mention_author=False)

        if limit > max_limit:
            return await ctx.send(f"Maximum value for number of posts shown is {max_limit}",
                                  reference=ctx.message,
                                  mention_author=False)
        elif limit <= 0:
            return await ctx.send(f"Minimum value for number of posts to be shown cannot be less than 1",
                                  reference=ctx.message,
                                  mention_author=False)

        posts_list = redditUtils.get_sub_posts_list(subreddit_name=subreddit,
                                                    sort=sort,
                                                    limit=limit)
        menu_str = ""
        for index,post in enumerate(posts_list):
            post_title = post.title if len(post.title) < title_string_limit else f"{post.title[:title_string_limit]}..."
            menu_str += f"**{index+1}. [{post_title}]({post.url})**\n\n"

        menu_embed = discord.Embed(title=f"List of Posts from r/{subreddit}, sorting by: {sort}",description=menu_str,color=discord.Colour.dark_gold())
        menu_embed.add_field(name="To show details, Enter the number associated with post title to select the post.\nRespond within 1 minute!",value='\u200b',inline=False)
        menu_embed.set_footer(text=f"Requested by {ctx.author}",icon_url=ctx.author.avatar_url)
        menu_embed.set_thumbnail(url=self.reddit_logo_url)

        menu_message = await ctx.send(embed=menu_embed,
                                      reference=ctx.message,
                                      mention_author=False)

        def check(msg:discord.Message):
            user_is_author = msg.author.id == ctx.author.id and msg.channel.id == ctx.channel.id
            index_in_range = msg.content.isnumeric() and int(msg.content) in range(1,len(posts_list)+1)
            return user_is_author and index_in_range
        try:
            wait_msg = await self.client.wait_for(event='message',check=check,timeout=60)
        except asyncio.TimeoutError:
            pass
        else:
            media_link_added = False
            content_needed = False
            emb_title_limit = 256
            selected_post = posts_list[int(wait_msg.content)-1]
            embed_title = selected_post.title if len(selected_post.title) < emb_title_limit else f"{selected_post.title[:emb_title_limit-10]}..."
            post_embed = discord.Embed(title=embed_title,description=f"[Link to the Reddit post]({selected_post.url})",color=discord.Colour.dark_gold())
            if selected_post.selftext:
                description_text = selected_post.selftext if len(selected_post.selftext) < (embed_field_character_limit-1) else f"{selected_post.selftext[:embed_field_character_limit-60]}....\n**`To read the remaining Text, use post Link`**"
                post_embed.add_field(name="Description Text:",value=description_text,inline=False)
            try:
                post_embed.set_image(url=selected_post.url)
                if post_embed.image:
                    post_embed.add_field(name="\u200b", value=f"If the image/video is not getting loaded, use this link : [Media Link]({selected_post.url})",inline=False)
                    media_link_added = True
            except:
                pass

            if selected_post.media:
                try:
                    media_link = selected_post.media['reddit_video']['fallback_url']
                    if media_link_added:
                        pass
                    else:
                        post_embed.add_field(name="\u200b",value=f"If the image/video is not getting loaded, use this link : [Media Link]({media_link})",inline=False)
                        content_needed = True
                except:
                    try:
                        media_link = selected_post.media['oembed']['url']
                        post_embed.add_field(name="\u200b",value=f"If Embed is not getting loaded, use this link : [Embed Link]({media_link})",inline=False)
                        content_needed = True
                    except:
                        pass
            post_embed.set_thumbnail(url=self.reddit_logo_url)
            footer_text = (f"Posted by: u/{selected_post.author} | score : {selected_post.score}\n"
                           f"Requested by {ctx.author}")
            post_embed.set_footer(text=footer_text,icon_url=ctx.author.avatar_url)

            if content_needed:
                return await ctx.send(content=media_link,
                                      embed=post_embed,
                                      reference=wait_msg,
                                      mention_author=False)
            else:
                return await ctx.send(embed=post_embed,
                                      reference=wait_msg,
                                      mention_author=False)


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
        elif isinstance(error,prawcore.exceptions.Redirect):
            await ctx.send(f"Invalid Subreddit Name!!",delete_after=del_after)
        else:
            await log_and_raise(client=self.client,ctx=ctx,error=error)



def setup(client:commands.Bot):
    client.add_cog(RedditCommands(client))
