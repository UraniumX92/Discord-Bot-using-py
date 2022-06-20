# *Discord Bot v4.2.0 :*
### ***New:***
* DataBase Structure changes:
  * Merged `guild_prefixes` `guild_bannedwords` `guild_custom_commands` `guild_switches` into 1 Collection named `guild_info`
* New Features/Commands:
  * Welcome/Goodbye messages when users join the server
    * This feature can be initialized using `setchannel` commands. (Mod Command - Only server admins can use this)
    * Set welcome message and goodbye message using `setmessage` command. (Mod Command - Only server admins can use this)
  * 2 time related commands added in Utility Commands (Unix <-> Human readable):
    * `timestampnow` -> gives the current unix timestamp from UTC. time zone can be modified using a format (see help command for utility commands)
    * `fromtimestamp` -> takes the timestamp from unix and converts it into human-readable date-time
  * Miscellaneous:
    * Now `guild_name` will be updated in database as soon as name of a server is changed and the change is logged in `./Bot Event Logs/guild_joined.txt`
    * v4.2.1 : fixed some unhandled exceptions
  
#### *Change Log from v4.1.0:*
* Separate Cog for game commands
  * New Typing practice game
    * Random words : Type randomly selected words from top 100 or top 1000 most used English words.
    * Quotes : Type randomly selected quote
    * Shows the amount of time taken, calculates the WPM and CPM and displays it after message is sent
    * ***Flexibility :*** Timer starts only when user starts typing and ends when message is sent
      * little clock emoji reaction is added as soon as timer starts, and it is removed when message is sent.
* Added Help command for gameCommands.
* small changes/updates:
  * Updated `purge` command in modCommands. now a user's message can be deleted by mentioning a user.
  * Added new command `getquote` in funCommands; Gives a random quote with name of Author.
  * new files in `Data Files`:
    * `quotes.json` for using quotes in typing game and fun commands
    * `topwords100.json` for using in typing game
    * `topwords1000.json` for using in typing game
#### v4.0.21
* ***TicTacToe Game added in Fun Commands***
  * Play TicTacToe against good AI
  * Play with your friends
* TicTacToe Algorithm made by me using `numpy`
  * `tttgame.py` has the algorithm utils to play TicTacToe on Console app.
  * Logic Building of AI is explained in code comments
  * **QoL upgrades:**
    * while game is going on, users can quit ongoing game by simply entering `quit`
    * Difficulty modes added:
      * Easy : Bot will make completely random plays
      * Medium : Bot only checks when someone is about to win, otherwise random play
      * Hard : the initial algorithm used in v4.0.2 will be used as hard mode
### Change log from v4.0.1:
* ***Hangman game added in Fun Commands.***
  * From a collection of 300+ words, a random word is selected to play hangman using a command.
  * New twisted "YOLO" mode in hangman where the player has to guess entire word in 1 guess (2 random characters are revealed). making it insanely difficult to guess.

# Change Log from v4.0:
## Major Update:
 **Until last update, Bot was using universal settings for all servers (from json file)**
 
**From now on, all server specific settings, and server specific prefixes are stored in database using MongoDB
and these settings will be implemented on each server**

***New Commands Categories :***
* **Custom Commands :**
  * *Custom Commands exclusive to servers*
    * These can only be used in server, anyone in server can use these command within server
    * Either Custom command Author (User who created the command) or Server Moderators can Remove Custom Commands
  * *Custom Commands exclusive to user*
    * These can only be used by the user, and can be used in any server where the bot is present
    * Not to mention, only the user can delete these Custom Commands
  

* **Reddit Commands :**
  * *`reddit sub` Command : Get list of posts from any subreddit*
    * You can specify the sorting of posts, like hot, new, top etc
    * You can also specify the number of posts to show in list (max = 30)
    * If you do not specify above parameters, then bot will use default values i.e : hot , 30 respectively
    * Shows the List of Post titles in Embed Message
    * After getting the List of Reddit Posts, you can select a Post from List by entering the associated number with post, bot will then show the detailed version of selected post
  * *`meme` Command :*
    * Gets a random meme from r/meme, sorting by Hot and sends it in Embed Message.

    
***Improvements :***
* **Help Commands :**
  * **Help Commands are now categorized into 6 different categories:**
    * Fun
    * Utility
    * Custom
    * Reddit
    * Moderator
    * Developer


* **In Fun Commands, `device` Command was Improved**
  * Previously, if you used this command, bot used to only check if user was on mobile or not
  * *New Improvement :*
    * Now Bot checks if the user is on Mobile , Desktop or Web version of Discord
    * Also checks if the user is active on multiple platforms, and responds accordingly



* **Hotfix Update:**
  * **In Custom commands, show commands were Improved**
    * If the number of commands exceeds the limit for number of fields for an Embed, bot will split the commands' data into several parts based on the total number of commands present
    * 2 emojis for next and previous are reacted by bot, if the user who called the command reacts on these emojis , then the commands' page will go to next, previous based on the reaction added by command author
    * after 1 minutes of inactivity , these reactions will get cleared and a No Entry emoji is added as reaction indicating that bot will not take any response
    * ***All of this was built pretty much from scratch, took me 1 complete day to make algorithm for splitting and then creating a menu logic, while handling the IndexError***
  * **In Reddit Commands, get sub command got Improved**
    * previously it would display `Description Text is too long to display in Embed...` 
    * Now this problem got solved, Instead, now the description text is sliced till the discord.Embed field limit
    * same goes with titles
    

That's it for this Update, Took me lots of effort in this one, Learning to use a Data Base, learning to use Python Reddit API Wrapper (PRAW) and Implementing these concepts was **Something!**
***

>**Note: If you want to build this bot together with me, then please contact me on discord `Uranium#4939`, Thank you!!**

***