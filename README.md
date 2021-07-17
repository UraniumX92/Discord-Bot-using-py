I started learning python few months ago, and I learned a lot, so I thought to make a basic discord bot.
And I started coding, and made this bot with some commands that work fine so far.
at first, I was in hurry,so I didn't read documentation well enough and just started coding from whatever I understood
and then after almost getting done with this version, I came to know about methods which I could've used to improve my code.
so in next versions of this bot, im going to re structure my code and add few new features

How this bot works:

Uses json module to load prefix, mod's list and filtered words list

`botData.py` : has the necessary data of bot to be used, made a separate file because i wanted my main file `Bot.py` to only have the commands functions (in this first version all commands are called using `on_message()` function.)

`botFunc.py` : has the functions which are getting used in `Bot.py`, reason for separate file is same as that of `botData.py`

Data Files (Folder) : Contains important data , which gets loaded and dumped using json module in program.