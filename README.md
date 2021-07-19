Discord Bot v2.0 :

As mentioned in earlier version, I found out that there was a possibility to write code more efficiently than version-1.

So, I re-wrote the entire bot's main script using a `command` decorator .

**New Features** : 

* MOD COMMANDS:
    * banword - add , remove or show banned words (filtered words)
    
    * New :
        * Mute
            * If User is having higher role than `muted` role, then bot moves the `muted` role above user's highest role and then mutes the user.
        * Un-mute
        * Kick
        * Ban
        * Unban
    

* UTILITY COMMANDS:
    * regex finder - Finds the possible matches for either Emails or Discord-Tags from given text.
    * New :
        * tenorgif | gif - Gives a Random GIF from tenor - from a given category.
        * code - Encloses the text given in command in a given format of code snippet.
    
* FUN COMMANDS:
    * fax - gives a random % of int to associated quality given in command.
    * sneak | say - makes the bot send the message whatever the command author says, keeps it anonymous as it deletes the author's message instantly.
    * sus - sends a funny message from susMessageList in botData.py while mentioning the mentioned user.
    * New:
        * device | dvc - sends a funny message depending on the platform mentioned-user is active on (Mobile | PC).
        * direct_anonymous | dm - sends dm to mentioned user, message = message of command author in command. (limitation: only users who are in guild can get these messages from bot).
        * dm_withID | dmid - same as {direct_anonymous|dm} but takes user-id instead of user mention, 
            * Works even if user is not in guild , but should have DM's open