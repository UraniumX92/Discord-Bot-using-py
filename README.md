# Discord Bot v2.1 :

**Lots of Changes, Commands and a \*New Feature\* in this update.**

***New Feature: Pin Messages on Reactions***  

Conditions for Pinning a Message : 
```
 If `number_of_reactions` reaches `react_limit_toPin`, and `number_of_diff_reactions` reaches `diff_reaction_limit`,
 then the message on which reaction was added, will get pinned.
 i.e : with some n different reactions, and some m number of total users reacted on all emojis combined , the message will get pinned
    
 Functionality of number_of_reactions:
     iterates through all the different reactions on a reacted message, counts and adds number of users reacted on all emojis reacted
     (users can repeat in different reactions, it is intentionally designed to count repeated users)
     reactions won't count if 1 user react with 'n' reactions,
     for any emoji reacted, if users reacted > 1 for that emoji, only then reactions will count towards pinning the message.
     if there are any bot reactions, we will not count them at all

 Functionality of 'Pin message on Reactions' feature :
     doesn't pin if Bot's reaction triggered the condition for pinning,
     pins only if pinSwitch is `True` ,
     number_of_reactions >= react_limit_to_pin
     number_of_diff_reactions >= diff_reaction_limit

     All three attributes `pinSwitch` , `react_limit_to_pin` and `diff_reaction_limit` are extracted from file 'switches&data.data' in '/Data Files/'
     and all of them can be controlled using their respective commands.
```
***New :***
* Files :
    * `switches&data.data` in `/Data Files/` : 
        * Switches:
            * Message Scanning for filtered words
            * Pin Message on Reactions
        * Data :
            * Reactions Limit for Feature "Pin Messages on Reactions".
            * Different Reactions Limit for Feature "Pin Messages on Reactions".
    * Directory :
        * `/Err Logs/`:
            * `errorLogs.txt` : To Log the Error with date time , guild.
            * `errorMessages.txt` : To Log the Message content which caused the error; with date time, guild and channel.
        > Note: as you might have already noticed, Exception handling is being done from this version on.
    
    
* Bot-Dev / Bot-Mods Commands:
    * **show-logs** : Sends Error Logging file in response as `discord.File`
    * **show-msglogs** : Sends Error-Message Logging file in response as `discord.File`
    * **mod** (re-added from v1) : add, remove or show from list of Bot-Devs / Bot-Mods
    >Note : Only Users in `botData.modslist` (or) `/Data Files/modList.data` can use Bot-Devs / Bot-Mods Commands.
    This means , Even Guild Owners cannot use these commands , as these are only made for Bot-Devs / Bot-Mods
* Mod Commands :
    * **filter_switch** : Turns message scanning for filtered words on/off
    * **pin_switch** : Turns the feature "Pin Message on Reactions" on/off
    * **reactionsLimit** : Bot Feature "Pin Message on Reactions" : Set the number of reactions needed to pin the message
    * **diffReactionsLimit** : Bot Feature "Pin Message on Reactions" : Set the number of different reactions required to pin the message
* User Commands :
    * **avatar** : Shows Avatar of mentioned user, if not mentioned, then shows user's avatar
    
***Changes in Commands :***
* **Help commands** (Both for Users and Mods) : changed type from Text to `discord.Embed`
* **tenorgif** : added footer, and credit to 'tenor' as thumbnail.
* **code** : Instead of enclosing Given code into a snippet of given format, now the command will make a temp file at server and sends it back to user as `discord.File` with file name as `{author.name}Code.{format}` and sends it in response.

***Changes in Help Command's Data Structure :***
* ***Previous Structure*** : 
    * `List[Command Names]` 
    * `Dict[{commandList[index] : Command Description}]`
    
* ***New Structure*** :
    * `Dict[{Command Name : Command Description}]`
    
> Note : These changes have been applied to both `help` and `mod_help` commands.