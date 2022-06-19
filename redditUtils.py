import praw
import os
from pprint import pprint

client_id = os.environ['REDDIT_CLIENT_ID']
client_secret = os.environ['REDDIT_CLIENT_SECRET']
user_name = os.environ['REDDIT_USERNAME']
password = os.environ['REDDIT_PASSWORD']
user_agent = 'Reddit'

reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     username=user_name,
                     password=password,
                     user_agent=user_agent,
                     check_for_async=False)


subreddit_posts_sort_types = [
    "hot",
    "top",
    "new",
    "controversial"
]


def get_sub_posts_list(subreddit_name,sort,limit):
    """
    gets a subreddit and returns a sorted list based on parameter
    """
    subreddit = reddit.subreddit(subreddit_name)

    if sort == "hot":
        post_list = list(subreddit.hot(limit=limit))
    elif sort == "top":
        post_list = list(subreddit.top(limit=limit))
    elif sort == "new":
        post_list = list(subreddit.new(limit=limit))
    elif sort == "controversial":
        post_list = list(subreddit.controversial(limit=limit))

    return post_list


if __name__ == '__main__':
    hot = get_sub_posts_list("memes","hot",5)
    for post in hot:
        print(f"Title: {post.title}")
        print(f"Description:\n{post.selftext}") if post.selftext else None
        print(f"score: {post.score}, ups: {post.ups} , downs: {post.downs} , likes: {post.likes}")
        # pprint(post.media['reddit_video']['fallback_url'])
        pprint(post.media)
        print(f"post url : {post.url}")
        print("-------------------------------------------")
        # Now i want to print the text part of post, how do i do it?