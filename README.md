# Discord Bot v4.0 :

## Major Update:
 **Until last update, Bot was using universal settings for all servers (from json file)**
 
**From now on, all server specific settings, and server specific prefixes are stored in data base using MongoDB
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
    

That's it for this Update, Took me lots of effort in this one, Learning to use a Data Base, learning to use Python Reddit API Wrapper (PRAW) and Implenting these concepts was **Something!**
***

>**Note: If you want to build this bot together with me, then please contact me on discord `Uranium#4939`, Thank you!!**

***