# TtgcBot
TtgcBot for Discord

**Currently in development please wait**

*Bot is currently on public beta version, you can invit him from a server with command* `/invit`  
*Already available on The Tale of Great Cosmos discord*

<hr/>

## Command Help

### How it works
The commands work following this example : `/example <arg> [optional] [opt1/opt2]` <br/>
The `/` refers to the prefix on your server by default `/`, but if you have changed it, use your own prefix <br/>
`<arg>` is an argument and must be provided (without `<` and `>`) when you call the command <br/>
`[optional]` is an optional argument and could be or not provided (without `[` and `]`) <br/>
`[opt1/opt2]` is an optional argument and if it's provided, it could only be one of the 2 options (`opt1` or `opt2`) <br/>
There are also some features (commands) reserved for some users, it will be precised for each of them. <br/>
Each commands must be used on servers only, else they won't work. <br/>
Bot is casse sensitive, you have to use uppercasse when necessary only

### Basic commands
- `/setprefix <newprefix>` (Administrator only) <br/>
Change the prefix of the bot on the current server
- `/rollindep <value>` <br/>
Roll dices and perform additions or substractions if given in the value field. For rolling a dice, you have to use the litteral expression `xdy` where `x` is the number of dice rolled,  `d` the letter `d` and `y` the number of side of the dice (`1d100` will roll 1 dice with 100 sides for example) <br/>
Full example : `/rollindep 10+1d100-2d10+5d8` will return the result of the following expression : `10+(1 dice with 100 sides)-(2 dices with 10 sides)+(5 dices with 8 sides)`
- `/tell <msg>` <br/>
The bot will tell your message and erase the command input (all tell commands are saved in logs)
- `/ttstell <msg>` <br/>
Same as the tell command but the bot will use tts
- `/pi` <br/>
Display the first decimals of pi
- `/joke` <br/>
Display a joke (Jokes are only in french)
- `/yay` <br/>
Use the power of yay
- `/choquedecu` <br/>
#ChoquéEtDéçu
- `/onichan` <br/>
Because you want to have a little sister who loves you :heart:
- `/invite` <br/>
Display the invitation link of the bot
- `/contentban` (Administrator only) <br/>
Forbid the usage of a string on your server, all message that will contains this string will automatically deleted by the bot and provide a DM to the author to explain why it has been deleted. You can only ban 20 strings per servers
- `/contentunban` (Administrator only) <br/>
Unban a string from your server
- `/warn <mention(s)> | <reason>` (Administrator only) <br/>
Warn a user (or multiple users), number of warns are stored by the bot
- `/configwarn <number> <kick/ban/assign role_mention>` (Adminstrator only) <br/>
Configure the bot on your server to apply a punishment when a user has received the number of warn given. When assign is asked, you have to provide by mentioning it the role to assign.
- `/blacklist <user_id> | <reason>` (Bot manager only) <br/>
Blacklist a user, he won't be able to use any commands of this bot by blacklisting him
- `/unblacklist <user_id>` (Bot manager only) <br/>
Unblacklist someone

### NSFW commands (NSFW channels only)
- `/nsfwjoke` <br/>
Same as joke, but will display a nsfw joke (always in french)
- `/hentai` <br/>
Do I need to explain what it does ?
- `/rule34` <br/>
Rule 34 of the internet : *if it exists, there is porn on it* <br/>
~~Just give a link to rule34 website~~

### JDR commands
- `/setMJrole <role_mention>` (Administrator only) <br/>
Set the role that every user need on your server to create JDR and use MJ commands after (the role have to be mentionned)
- `/JDRstart <channel_mention>` (MJ only) <br/>
Start a JDR in the mentionned channel
- `/JDRdelete <channel_mention>` (Administrator only) <br/>
Delete a JDR in the mentionned channel, this cannot be undone
- `/MJtransfer <mention>` (MJ only and JDR channel only) <br/>
transfer ownership of a JDR to the mentionned user, this user need to have the MJ role and to accept the request
- `/JDRcopy <from> <to>` (Administrator only) <br/>
Copy a JDR from a mentionned channel to an other. if the destination channel has already a JDR, this will be totally replaced by the copy (no merging)
- `/charcreate <namekey>` (MJ only and JDR channel only) <br/>
Create a new character referenced by the namekey given. The namekey is not the same things as the name of the character, the namekey is just the unique identifier of the character and will be needed each time you will want to perform commands on this character
- `/chardelete <namekey>` (MJ only and JDR channel only) <br/>
Delete a character (this cannot be undone once performed)
- `/link <charkey> <mention>` (MJ only and JDR channel only) <br/>
Link a character to a discord account (only for the channel and server). Mention is a discord mention tag of the user. An account can only be linked one time per JDR
- `/unlink [mention]` (MJ only and JDR channel only) <br/>
Unlink a discord account from a character, if not provided, unlink the author of the command
- `/charset <item> <charkey> <value>` (MJ only and JDR channel only) <br/>
Set a property of a character to the given value. The following properties can be set with this command : <br/>
```
name - (text) Set the name of the character
PV - (positive integer) Set the max HP of the character
PM - (positive integer) Set the max Mana points of the character
force - (integer between 1 and 100) Set the strength
esprit - (integer between 1 and 100) Set the spirit
charisme - (integer between 1 and 100) Set the charisma
agilite/furtivite - (integer between 1 and 100) Set the agility
lp - (integer) Add the number of light point given to the character
dp - (integer) Same as lp but for the dark points
defaultmod - (offensiv/defensiv) Set the default mod of the character
defaultkarma - (integer between -10 and 10) Set the default karma
intuition - (integer between 1 and 6) Set the intuition
```
- `/chardmg <charkey> <amount>` (MJ only and JDR channel only) <br/>
Damage a character, he will lose the number of HP given in the command
- `/globaldmg <amount>` (MJ only and JDR channel only) <br/>
Damage all the characters with the number of points given
- `/charheal <charkey> <amount>` (MJ only and JDR channel only) <br/>
Heal a character with the number of points given
- `/globalheal <amount>` (MJ only and JDR channel only) <br/>
Heal all the characters with the number of points given
- `/getPM <charkey> <amount>` (MJ only and JDR channel only) <br/>
Restore the given amount of mana points provided, if the amount is negative, the character will lose mana points
- `/globalgetPM <amount>` (MJ only and JDR channel only) <br/>
Add the given amount of mana points to all the characters, if the amount is negative, the characters will lose mana points
- `/setkarma <charkey> <amount>` (MJ only and JDR channel only) <br/>
Add or substract karma points to the current karma of the character
- `/resetchar <charkey>` (MJ only and JDR channel only) <br/>
Restore fully Health and Mana points, set the karma to its default value and set the mod to its default value for a character
- `/earnmoney <charkey> <amount>` (MJ only and JDR channel only) <br/>
Give to the character the amount of money provided
- `/map` (MJ only and JDR channel only) <br/>
Display the world map of Terae
- `/apart [mention(s)]` (MJ only and JDR channel only) <br/>
Mute and deafen all the players that are not mentionned by the command. If there is no single mention, the bot will unmute and undeafen all the players. (Spectators and MJ will not be affected by this)
- `/roll <stat> [+bonus/-malus]` (PJ only) <br/>
Roll a dice in the given statistic and adding bonus or substracting malus if provided. The result will tell you if the action is a success or not, according to the rules of TTGC game.
- `/pay <amount>` (PJ only) <br/>
Pay the amount given
- `/charinfo` (PJ only) <br/>
Display all the current informations of your character
- `/stat` (PJ only) <br/>
Display statistics about dice rolled for your character
- `/globalstat` (JDR channel only) <br/>
Display statistics about dice rolled for the group
- `/use <lightpt/darkpt>` (PJ only) <br/>
Use a light point or a dark point
- `/switchmod` (PJ only) <br/>
Switch your current mod between offensive and defensive mods
- `/setmental [+/-]<amount>` (PJ only) <br/>
Set the mental health of your character with the given value, if `+` or `-` is provided in the command, the amount will be added respectivly substracted to your mental health
- `/mj...` (MJ only and JDR channel only) <br/>
Use a PJ command when you are MJ, the following commands can be used : <br/>
```
/mjcharinfo <charkey>
/mjswitchmod <charkey>
/mjsetmental <charkey> [+/-]<amount>
/mjroll <charkey> <stat> [+bonus/-malus]
```
- `/wiki <topic>` <br/>
Search on the wiki the given topic, if found a summary will be displayed with the link to the page
- `/jointhegame` <br/>
provide an invite link to the official discord of TTGC game (French discord)

### Vocal commands (Premium user only)
- `/vocal <on/off>` <br/>
Make the bot join or leave your voice channel
- `/ytplay <url>` <br/>
Make the bot play the youtube video given. You can provide keywords instead of url and the bot will search and play the first result of your query.
- `/musicskip` <br/>
Skip the current song
- `/playlocal <song>` <br/>
Play the song given from the music directory of the bot
- `/disconnectvocal` (Bot manager only) <br/>
Instant leave all the vocal channels where the bot is connected
