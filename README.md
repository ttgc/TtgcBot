# TtgcBot 
[![CircleCI](https://circleci.com/gh/ttgc/TtgcBot/tree/master.svg?style=svg)](https://circleci.com/gh/ttgc/TtgcBot/tree/master)

TtgcBot is a bot for Discord made at the beginning for RP (JDR) on The Tale of Great Cosmos universe ([French Website here](http://thetaleofgreatcosmos.fr)). But, today the bot is having many useful tools and features such as Keeprole system that allow leaving member to keep their roles after joining again your server, warn users that doesn't follow your rules, and more things (list of commands below). The bot is developed in Python 3 using [discord.py](https://github.com/Rapptz/discord.py/tree/async) lib and use also a postgresql 9 database.

**[Invite link](https://discordapp.com/oauth2/authorize?client_id=331147011938320396&scope=bot&permissions=385350855)**

*you can invit him from a server with command* `/invite`  
*Already available on The Tale of Great Cosmos discord*

<hr/>

## Contribute to translation
TtgcBot supports currently only two languages (English and French), if you want that the bot support more languages you can contribute by creating your own translation in a language file ! Follow the steps and rules given below to contribute to translation :
1. Create a new file named as following : the language code in uppercasse (`EN` for English for example) and with the extension `.lang`
2. Begin to write your file and respect coding rules below :
    - `#` is used to defined a comment line and must only placed at the beginning of the line to work
    - A line is equal to a key/value couple corresponding at a single message of the bot
    - Here is the correct format of a line : `key=value`
    - Write only translation as value for each key existing in other languages files (use `EN.lang` file as reference for having all the keys)
    - Use `\n` as new line character and you can also keep discord formatting
    - Use brackets `{}` to define a missing value that will be replaced by a result during execution of the command. For example : `Who are you ? I'm {}` means that the `{}` will be replaced by the name of a person when the command would be executed.
    - Put the same number of `{}` for a value as the number of `{}` for the same value in the reference file (`EN.lang`)
3. Commit and put the language file in the Lang directory
4. Wait for validation....
5. You have successful contributed to bot translation ! Congratulations !

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
Bot is casse sensitive, you have to use uppercasse when necessary only <br/>
For some commands there are alliases avalaible wich will be given for each commands having it

### Basic commands
- `/setprefix <newprefix>` (Administrator only) <br/>
Change the prefix of the bot on the current server <br/>
Aliases : `prefix`
- `/setadminrole <role_mention>` (Server owner only) <br/>
Set the admin role for your server <br/>
Aliases : `adminrole`
- `/setlang <language>` <br/>
Set your language for bot messages, language represents the code of your language and there are currently only two languages supported : `EN` for English and `FR` for French <br/>
NB : language code is case insensitive so you can precise it in upper or lower case as you wish
Aliases : `setlanguage`
- `/rollindep <expression>` <br/>
Roll dice and perform operations (supported symbols and operations : `*,+,-,/,()`) if given in the expression field. For rolling a dice, you have to use the litteral expression `xdy` where `x` is the number of dice rolled,  `d` the letter `d` and `y` the number of side of the dice (`1d100` will roll 1 dice with 100 sides for example). You can also roll special dice with your own values by writing them between brackets as following : `1d{red,blue,yellow,green}`. <br/>
Full example : `/rollindep (10+1d100)*(2d10-5d8)` will return the result of the following expression : `(10+(1 dice with 100 sides))*((2 dice with 10 sides)-(5 dice with 8 sides))` <br/>
Special dice example : `/rollindep 1d{1,2,3,4,5,6,7,8,9,10,Jack,Queen,King}+1d{Clubs,Diamonds,Hearts,Spades}` will return a single card with its value and its color (example : Queen of Spades) <br/>
Aliases : `rolldice`, `r`
- `/tell <msg>` <br/>
The bot will tell your message and erase the command input (all tell commands are saved in logs)
- `/ttstell <msg>` <br/>
Same as the tell command but the bot will use tts <br/>
Aliases : `telltts`, `tell --tts`, `tell -t`
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
- `/ping` <br/>
pong ! :ping_pong:
- `/contentban <content>` (Administrator only) <br/>
Forbid the usage of a string on your server, all message that will contains this string will automatically deleted by the bot and provide a DM to the author to explain why it has been deleted. You can only ban 20 strings per servers
- `/contentunban <content>` (Administrator only) <br/>
Unban a string from your server
- `/warn <mention(s)> | <reason>` (Administrator only) <br/>
Warn a user (or multiple users), number of warns are stored by the bot
- `/unwarn <mention(s)>` (Administrator only) <br/>
Unwarn a user (or multiple users)
- `/configwarn <number> <kick/ban/assign role_mention>` (Adminstrator only) <br/>
Configure the bot on your server to apply a punishment when a user has received the number of warn given. When assign is asked, you have to provide by mentioning it the role to assign.
- `/warnlist` (Administrator only) <br/>
Display all users warned on your server with the number of warn for each of them <br/>
Aliases : `warnls`
- `/warnconfiglist` (Administrator only) <br/>
Display all punishment on your server <br/>
Aliases : `warnconfigls`, `warncfgls`, `warncfglist`
- `/blacklist <user_id> | <reason>` (Bot manager only) <br/>
Blacklist a user, he won't be able to use any commands of this bot by blacklisting him
- `/unblacklist <user_id>` (Bot manager only) <br/>
Unblacklist someone
- `/purgeserver <days>` (Bot manager only) <br/>
Delete servers from the database that have kicked the bot at least number of days given ago
- `/userblock <username>` (Admin only) <br/>
Block users wich have a username matching the username mask parameter given and avoid them to join your server. If someone matching the template try to join, it will be banned instantly
- `/userunblock <username>` (Admin only) <br/>
Delete a template of usernames blocked on your server

### Keeprole commands (Administrator only)
- The basic syntax for this commands is : `/keeprole <subcommand> ...`. Instead of `keeprole` you can just write `kr`. Aliases will be given just for the subcommand but you still have to precised `keeprole` or `kr` before the alias. Keeprole system allow you to set roles that will be automatically reassigned to member when they leave with theese roles and join again your server
- `/keeprole enabled` <br/>
enable or disable the keeprole system on your server <br/>
Aliases : `switch`
- `/keeprole roles add <role(s)>` <br/>
Add the roles mentionned to the list of roles that should be kept. If the role is above or equal to the highest role of the bot, it won't be added <br/>
Aliases : `roles +`
- `/keeprole roles delete <role(s)>` <br/>
Remove role(s) mentionned from the keeprole list <br/>
Aliases : `roles del`, `roles -`
- `/keeprole roles list` <br/>
Show the list of roles registered in the keeprole system for your server
- `/keeprole clear` <br/>
Delete all users stored for the keeprole system, they won't get their roles after joining after using that
- `/keeprole members list` <br/>
Show the list of members that will get roles after joining your server (the list show also the roles concerned for each user)

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
Set the role that every user need on your server to create JDR and use MJ commands after (the role have to be mentionned) <br/>
Aliases : `setmjrole`
- `/JDRstart <channel_mention>` (MJ only) <br/>
Start a JDR in the mentionned channel <br/>
Aliases : `jdrstart`, `JDRcreate`, `jdrcreate`
- `/JDRdelete <channel_mention>` (Administrator only) <br/>
Delete a JDR in the mentionned channel, this cannot be undone <br/>
Aliases : `jdrdelete`
- `/MJtransfer <mention>` (MJ only and JDR channel only) <br/>
transfer ownership of a JDR to the mentionned user, this user need to have the MJ role and to accept the request <br/>
Aliases : `mjtransfer`
- `/JDRcopy <from> <to>` (Administrator only) <br/>
Copy a JDR from a mentionned channel to an other. if the destination channel has already a JDR, this will be totally replaced by the copy (no merging) <br/>
Aliases : `jdrcopy`
- `/JDRextend <from> <to>` (Administrator only) <br/>
Extend a JDR through an other channel, the two channel will work with the same database and commands executed in one will affect the two channels. If a JDR exists in the destination channel, it will be deleted. <br/>
Aliases : `jdrextend`
- `/JDRunextend <from> <to>` (Administrator only) <br/>
Unextend a JDR through the precised channel, only source channel will contain the data after using that <br/>
Aliases : `jdrunextend`
- `/JDRunextend --all <from>` (Administrator only) <br/>
Unextend the JDR in all the channel where there were extended, only source channel will contain data after using that <br/>
Aliases : `jdrunextend --all`
- `/JDRlist` (Administrator only) <br/>
Show the list of all JDR existing in your server (extension won't be shown) <br/>
Aliases : `jdrlist`
- `/setfinalizer <title>|<content>` (MJ only and JDR channel only) <br/>
Set the finalize field with the given title (if it doesn't exists, it will be created)
- `/delfinalizer <title>` (MJ only and JDR channel only) <br/>
Delete the finalize field given <br/>
Aliases : `deletefinalizer`
- `/finalize` (MJ only and JDR channel only) <br/>
This command will start the finalizing operation displaying credits with some random informations of your game and also your own finalize fields. After that, the JDR will be fully deleted from the database.
- `/charcreate <race> <class> <namekey>` (MJ only and JDR channel only) <br/>
Create a new character with the given race and class and referenced by the namekey given. The race and class is the exact name of the race and class (french names), go to the website to know all existing classes. Use `_` instead of space character for race and class name. The namekey is not the same things as the name of the character, the namekey is just the unique identifier of the character and will be needed each time you will want to perform commands on this character <br/>
Aliases : `createchar`
- `/chardelete <namekey>` (MJ only and JDR channel only) <br/>
Delete a character (this cannot be undone once performed) <br/>
Aliases : `deletechar`, `chardel`, `delchar`
- `/link <charkey> <mention>` (MJ only and JDR channel only) <br/>
Link a character to a discord account (only for the channel and server). Mention is a discord mention tag of the user. An account can only be linked one time per JDR <br/>
Aliases : `charlink`
- `/unlink [mention]` (MJ only and JDR channel only) <br/>
Unlink a discord account from a character, if not provided, unlink the author of the command <br/>
Aliases : `charunlink`
- `/charselect <charkey>` (PJ only) <br/>
Select an other character. For selecting a character, you'll need to be linked first to this character with the `link` command. `charselect` allow you to switch from a character to an other.
- `/charset <item> <charkey> <value>` (MJ only and JDR channel only) <br/>
Set a property of a character to the given value. The following properties can be set with this command : <br/>
Aliases : you can write in one word charset+item (example : `/charsetpv`)
```
name - (text) Set the name of the character
PV/pv - (positive integer) Set the max HP of the character
PM/pm - (positive integer) Set the max Mana points of the character
force/str/strength - (integer between 1 and 100) Set the strength
esprit/spr/spirit - (integer between 1 and 100) Set the spirit
charisme/cha/charisma - (integer between 1 and 100) Set the charisma
agilite/furtivite/agi/agility - (integer between 1 and 100) Set the agility
lp/lightpt - (integer) Set the number of light point of the character
dp/darkpt - (integer) Same as lp but for the dark points
defaultmod/dmod - (offensiv/defensiv) Set the default mod of the character
defaultkarma/dkar - (integer between -10 and 10) Set the default karma
intuition/int - (integer between 1 and 6) Set the intuition
```
- `/charset lore <charkey>` <br/>
The bot will ask you to enter the lore of the character to be set once replied
- `/chardmg <charkey> <amount>` (MJ only and JDR channel only) <br/>
Damage a character, he will lose the number of HP given in the command <br/>
Aliases : `chardamage`
- `/globaldmg <amount>` (MJ only and JDR channel only) <br/>
Damage all the characters with the number of points given <br/>
Aliases : `globaldamage`, `gdmg`, `gdamage`
- `/charheal <charkey> <amount>` (MJ only and JDR channel only) <br/>
Heal a character with the number of points given
- `/globalheal <amount>` (MJ only and JDR channel only) <br/>
Heal all the characters with the number of points given <br/>
Aliases : `gheal`
- `/getPM <charkey> <amount>` (MJ only and JDR channel only) <br/>
Restore the given amount of mana points provided, if the amount is negative, the character will lose mana points <br/>
Aliases : `getpm`
- `/globalgetPM <amount>` (MJ only and JDR channel only) <br/>
Add the given amount of mana points to all the characters, if the amount is negative, the characters will lose mana points <br/>
Aliases : `ggetPM`, `globalgetpm`, `ggetpm`
- `/setkarma <charkey> <amount>` (MJ only and JDR channel only) <br/>
Add or substract karma points to the current karma of the character <br/>
Aliases : `addkarma`, `getkarma`
- `/resetchar <charkey>` (MJ only and JDR channel only) <br/>
Restore fully Health and Mana points, set the karma to its default value and set the mod to its default value for a character <br/>
Aliases : `resetcharacter`
- `/earnmoney <charkey> <amount>` (MJ only and JDR channel only) <br/>
Give to the character the amount of money provided <br/>
Aliases : `earnpo`, `earnPO`
- `/map` (MJ only and JDR channel only) <br/>
Display the world map of Terae
- `/map show <width> <height> [depth]` (MJ only and JDR channel only) <br/>
Show the local fight map displaying all tokens and effects registered for the current game. Only effects affecting this depth (Z axis) given will be displayed, if not given, depth is considered equal to 0.
- `/map clearall` (MJ only and JDR channel only) <br/>
Clear all tokens and effects on your local fight map <br/>
Aliases : `map clrall`, `map reset`
- `/map token add <name>` (MJ only and JDR channel only) <br/>
Add a token on your local fight map, a token represents an entity that can be moved and can generate area of effects (AOE). When created, the token will automatically put on the origin (0;0;0) of the map. Use token move command to move it. <br/>
Aliases : `map tk add`, `map token +`, `map tk +`
- `/map token remove <name>` (MJ only and JDR channel only) <br/>
Remove a token from your local fight map <br/>
Aliases : `map tk rm`, `map token rm`, `map tk remove`, `map token -`, `map tk -`
- `/map token move <name> <dx> <dy> [dz]` (MJ only and JDR channel only) <br/>
Move a token in the direction given by the vector (dx;dy;dz). If not given dz is equal to 0 <br/>
Aliases : `map tk move`
- `/map effect add <tkname> <dx> <dy> <dz> <shape> [parameters]` (MJ only and JDR channel only) <br/>
Register an area of effect for a given token. shape must be one of the following : `circle`,`sphere`,`line`,`rect`,`cube`,`conic`. Each of theese shape have their own parameters, some of them have to be given for the generation.
Aliases : `map effect +`<br/>
```
List of parameters avalaible :
circle : <r>
sphere : <r>
line : <length> [<orientation (default=0)> <height (default=1)> <thickness (default=0)>]
    orientation -> the value in degrees (following counter-clockwise rotation), can only be one of the following : 0, 90, 180 or 270
rect : <rx> <ry>
cube : <rx> <ry> <rz>
conic : <lengths> [orientation (default=0)]
    lengths -> list of lengths separated with '-' symbol, the first value is the closest line from the origin and the last the farthest line from the origin (example : 1-3-5). DO NOT USE SPACE BETWEEN LENGTHS VALUES.
    orientation -> the value in degrees (following counter-clockwise rotation), can only be one of the following : 0, 90, 180 or 270
```
- `/map effect clear <tkname>` (MJ only and JDR channel only) <br/>
Clear all effects for the given token
- `/apart [mention(s)]` (MJ only and JDR channel only) <br/>
Mute and deafen all the players that are not mentionned by the command. If there is no single mention, the bot will unmute and undeafen all the players. (Spectators and MJ will not be affected by this)
- `/lvlup <charkey>` (MJ only and JDR channel only) <br/>
Give one more level to the character and announce the bonus for this level <br/>
Aliases : `levelup`
- `/inventory add <charkey> <item> [number]` (MJ only and JDR channel only) <br/>
Add the number of item to the inventory of the character, by default number is equal to 1. The item name must not contains space char and spaces have to be replaces by underscore (write `potion_soin` instead of `potion soin`) <br/>
Aliases : `inv add`
- `/inventory delete <charkey> <item> [number]` (MJ only and JDR channel only) <br/>
Remove the number of item from the inventory of the character, by default number is equal to 1. Item name must not contains space like for "inventory add" command <br/>
Aliases : `inv delete`, `inventory del`, `inv del`
- `/inventory` (PJ only) <br/>
Show your current inventory <br/>
Aliases : `inv`
- `/roll <stat> [+bonus/-malus]` (PJ only) <br/>
Roll a dice in the given statistic and adding bonus or substracting malus if provided. The result will tell you if the action is a success or not, according to the rules of TTGC game.
- `/pay <amount>` (PJ only) <br/>
Pay the amount given
- `/charinfo` (PJ only) <br/>
Display all the current informations of your character <br/>
Aliases : `characterinfo`
- `/stat` (PJ only) <br/>
Display statistics about dice rolled for your character <br/>
Aliases : `charstat`, `characterstat`
- `/globalstat` (JDR channel only) <br/>
Display statistics about dice rolled for the group <br/>
Aliases : `gstat`
- `/use <lightpt/darkpt/item>` (PJ only) <br/>
Use a light point or a dark point. If an item name is precised instead of lightpt or darkpt, the item will be consumed
- `/switchmod` (PJ only) <br/>
Switch your current mod between offensive and defensive mods <br/>
Aliases : `switchmode`
- `/setmental [+/-]<amount>` (PJ only) <br/>
Set the mental health of your character with the given value, if `+` or `-` is provided in the command, the amount will be added respectivly substracted to your mental health
- `/petadd <charkey> <petkey>` (MJ only and JDR channel only) <br/>
Pet are linked to a single character and cannot be shared, they allow the owner of the character to execute standard PJ commands for pets. A character can have multiple pet and each of them have an unique identifier the `petkey` such as the `charkey` for characters.<br/>
This command add a new pet to a character <br/>
Aliases : `pet+`
- `/petremove <charkey> <petkey>` (MJ only and JDR channel only) <br/>
Remove and delete completly a pet, this cannot be undone and have no confirmation message<br/>
Aliases : `pet-`
- `/petset <item> <charkey> <petkey> <value>` (MJ only and JDR channel only) <br/>
Such as `charset` set a value of a pet. The same shortcuts as for `charset` are still avalaible. Only the following attributes are avalaible :<br/>
```
name
species
PV/PM
strength/spirit/charisma/agility
instinct (replace intuition)
defaultmod
```
- `/petswitchmod <petkey>` (PJ only) <br/>
Switchmod for a pet
- `/petlvlup <charkey> <petkey>` (MJ only and JDR channel only) <br/>
Levels are not linked between characters and their pets. So to level up a pet you have to use this commands
- `/petroll <petkey> <stat> [+bonus/-malus]` (PJ only) <br/>
Roll the dice for your pet, same rules as for classical `roll` command
- `/petinfo <petkey>` (PJ only) <br/>
Show informations about your pet such as `charinfo`
- `/petsetkarma <charkey> <petkey> <value>` (MJ only and JDR channel only) <br/>
Equivalent of `setkarma` for pets
- `/petstat <petkey>` (PJ only) <br/>
Show all stat of a pet you have (such as `/stat` for characters)
- `/petdmg <charkey> <petkey> <amount>` (MJ only and JDR channel only) <br/>
Inflict damages to a pet <br/>
Aliases : `petdamage`
- `/petheal <charkey> <petkey> <amount>` (MJ only and JDR channel only) <br/>
Heal a pet <br/>
Aliases : `petcure`
- `/petgetPM <charkey> <petkey> <amount>` (MJ only and JDR channel only) <br/>
Manage MP for a pet such as `getPM` for a character <br/>
Aliases : `petgetpm`, `petgetMP`, `petgetmp`, `petPM`, `petpm`, `petMP`, `petmp`
- `/kill <player>` (MJ only and JDR channel only) <br/>
Kill definitively a character, this will unlink it from its owner and the character wont be playable anymore <br/>
Aliases : `characterkill`, `charkill`
- `/skill` (PJ only) <br/>
Show the list of skills of your character <br/>
Aliases : `sk`, `charskill`, `charsk`
- `/skillinfo <query>` (JDR channel only) <br/>
Search skills in the database with their names. To give many skill name in the query parameter, give them separated with `|` <br/>
Aliases : `skinfo`
- `/skillassign <charkey> <skillID>` (MJ only and JDR channel only) <br/>
Assign a skill to a character, if you dont know the ID of the skill, use `skillinfo` command to search your skill by name <br/>
Aliases : `skassign`
- `/mj...` (MJ only and JDR channel only) <br/>
Use a PJ command when you are MJ, theese commands works exactly as the same commands without the `mj` prefix with sames arguments, the result will also be the same. For example `/mjcharinfo` will produce same result as `/charinfo` but you will have to precise for wich character this commands must be used for as the following : `/charinfo <charkey>`. Refers to the PJ commands' doc to know result and how arguments works for each commands <br/>
The following commands can be used : <br/>
```
/mjcharinfo <charkey>
/mjswitchmod <charkey>
/mjsetmental <charkey> [+/-]<amount>
/mjroll <charkey> <stat> [+bonus/-malus]
/mjinventory <charkey>
/mjpetroll <charkey> <petkey> <stat> [+bonus/-malus]
/mjpetinfo <charkey> <petkey>
/mjpetswitchmod <charkey> <petkey>
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
