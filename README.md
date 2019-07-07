# TtgcBot
[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)

![Generic badge](https://img.shields.io/badge/Bot Version-2.0-blue.svg) [![GitHub license](https://img.shields.io/github/license/ttgc/TtgcBot.svg)](https://github.com/ttgc/TtgcBot/blob/master/LICENSE) ![Generic badge](https://img.shields.io/badge/Python Version-3.5 | 3.6 | 3.7-blue.svg) [![Generic badge](https://img.shields.io/badge/Languages-EN | FR-green.svg)](https://github.com/ttgc/TtgcBot/tree/master/Lang) ![CircleCI](https://circleci.com/gh/ttgc/TtgcBot/tree/master.svg?style=svg) <br/>
[![Generic badge](https://img.shields.io/badge/discord.py-1.2.3-blue.svg)](https://pypi.python.org/pypi/discord.py/) [![Generic badge](https://img.shields.io/badge/asyncio-3.4.3-blue.svg)](https://pypi.org/project/asyncio/) [![Generic badge](https://img.shields.io/badge/Pillow-5.4.1-blue.svg)](https://pypi.org/project/Pillow/) [![Generic badge](https://img.shields.io/badge/psycopg2-2.8.1-blue.svg)](https://pypi.org/project/psycopg2/) [![Generic badge](https://img.shields.io/badge/PyNaCl-1.3.0-blue.svg)](https://pypi.org/project/PyNaCl/) [![Generic badge](https://img.shields.io/badge/request-2018.11.20-blue.svg)](https://pypi.org/project/request/) [![Generic badge](https://img.shields.io/badge/requests-2.21.0-blue.svg)](https://pypi.org/project/requests/) [![Generic badge](https://img.shields.io/badge/urllib3-1.24.2-blue.svg)](https://pypi.org/project/urllib3/) [![Generic badge](https://img.shields.io/badge/latex-0.7.0-blue.svg)](https://pypi.org/project/latex/)

TtgcBot is a bot for Discord made at the beginning for RP (JDR) on The Tale of Great Cosmos universe ([French Website here](http://thetaleofgreatcosmos.fr)). But, today the bot is having many useful tools and features such as Keeprole system that allow leaving member to keep their roles after joining again your server, warn users that doesn't follow your rules, and more things (list of commands below). The bot is developed in Python 3 using [discord.py](https://github.com/Rapptz/discord.py/tree/async) lib and use also a postgresql 9 database.

**[Invite link](https://discordapp.com/oauth2/authorize?client_id=331147011938320396&scope=bot&permissions=385350855)**

*you can invit him from a server with command* `/invite`  
*Also available on The Tale of Great Cosmos discord*

<hr/>

# Table of content
<!-- MDTOC maxdepth:6 firsth1:0 numbering:1 flatten:0 bullets:0 updateOnSave:1 -->

1. [Contribute to translation](#contribute-to-translation)   
2. [Command Help](#command-help)   
&emsp;2.1. [How it works](#how-it-works)   
&emsp;2.2. [Basic commands](#basic-commands)   
&emsp;2.3. [Fun commands](#fun-commands)   
&emsp;2.4. [Moderation commands](#moderation-commands)   
&emsp;2.5. [Keeprole commands (Administrator only)](#keeprole-commands-administrator-only)   
&emsp;2.6. [Vocal commands (Premium user only)](#vocal-commands-premium-user-only)   
&emsp;2.7. [NSFW commands (NSFW channels only)](#nsfw-commands-nsfw-channels-only)   
&emsp;2.8. [RP/JDR commands](#rpjdr-commands)   
&emsp;&emsp;2.8.1. [Main commands](#main-commands)   
&emsp;&emsp;2.8.2. [Character commands](#character-commands)   
&emsp;&emsp;2.8.3. [Global commands](#global-commands)   
&emsp;&emsp;2.8.4. [GM/MJ commands](#gmmj-commands)   
&emsp;&emsp;2.8.5. [Skill commands](#skill-commands)   
&emsp;&emsp;2.8.6. [Pet commands](#pet-commands)   
&emsp;&emsp;2.8.7. [Map commands](#map-commands)   
&emsp;&emsp;2.8.8. [Inventory commands](#inventory-commands)   
&emsp;&emsp;2.8.9. [Finalize commands](#finalize-commands)   
&emsp;2.9. [Bot Management (Bot Manager only)](#bot-management-bot-manager-only)   

<!-- /MDTOC -->

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
`[opt1|opt2]` is an optional argument and if it's provided, it could only be one of the 2 options (`opt1` or `opt2`) <br/>
`(name1|name2)` same as above, but used for commands group names instead. You can use the name1 or name2 for each subcommands. <br/>
`[,...]` means that you can pass as many as you want parameters of the same type <br/>
There are also some features (commands) reserved for some users, it will be precised for each of them. <br/>
Each commands must be used on servers only, else they won't work. <br/>
Bot is casse insensitive, you can use uppercasse like lowercase for calling commands <br/>
For some commands there are alliases avalaible wich will be given for each commands having it

### Basic commands
- `/help [command]` <br/>
Show the help message. If a command, or group of command is provided, show detailled information about it.
- `/invite` <br/>
Get the [invitation link](https://discordapp.com/oauth2/authorize?client_id=331147011938320396&scope=bot&permissions=385350855) of the bot. <br/>
Alias : `invit`
- `/setlang <language>` <br/>
Set your language for bot messages, language represents the code of your language and there are currently only two languages supported : `EN` for English and `FR` for French <br/>
NB : language code is case insensitive so you can precise it in upper or lower case as you wish
Alias : `setlanguage`
- `/ping` <br/>
pong ! :ping_pong:

### Fun commands
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
- `/tell <msg>` <br/>
The bot will tell your message and erase the command input (all tell commands are saved in logs)
- `/ttstell <msg>` <br/>
Same as the tell command but the bot will use tts <br/>
Alias : `telltts`

### Moderation commands
- `/setprefix <newprefix>` (Administrator only) <br/>
Change the prefix of the bot on the current server <br/>
Alias : `prefix`
- `/setadminrole <role>` (Administrator only) <br/>
Set the admin role for your server <br/>
Alias : `adminrole`
- `/contentban <content>` (Administrator only) <br/>
Forbid the usage of a string on your server, all message that will contains this string will automatically deleted by the bot and provide a DM to the author to explain why it has been deleted. You can only ban 20 strings per servers
- `/contentunban <content>` (Administrator only) <br/>
Unban a string from your server
- `/warn <member[,...]> <reason>` (Administrator only) <br/>
Warn a user (or multiple users), number of warns are stored by the bot
- `/unwarn <member[,...]>` (Administrator only) <br/>
Unwarn a user (or multiple users)
- `/configwarn <number> <kick|ban|assign role>` (Adminstrator only) <br/>
Configure the bot on your server to apply a punishment when a user has received the number of warn given. When assign is asked, you have to provide by mentioning it the role to assign.
- `/warnlist` (Administrator only) <br/>
Display all users warned on your server with the number of warn for each of them <br/>
Alias : `warnls`
- `/warnconfiglist` (Administrator only) <br/>
Display all punishment on your server <br/>
Aliases : `warnconfigls`, `warncfgls`, `warncfglist`
- `/userblock <username>` (Admin only) <br/>
Block users wich have a username matching the username mask parameter given and avoid them to join your server. If someone matching the template try to join, it will be banned instantly
- `/userunblock <username>` (Admin only) <br/>
Delete a template of usernames blocked on your server

### Keeprole commands (Administrator only)
Keeprole system allow you to set roles that will be automatically reassigned to member when they leave with theese roles and join again your server
- `/(keeprole|kr) enabled` <br/>
enable or disable the keeprole system on your server <br/>
Alias : `switch`
- `/(keeprole|kr) clear` <br/>
Delete all users stored for the keeprole system, they won't get their roles after joining after using that
- `/(keeprole|kr) roles list` <br/>
Show the list of roles registered in the keeprole system for your server
- `/(keeprole|kr) roles add <role[,...]>` <br/>
Add the roles mentionned to the list of roles that should be kept. If the role is above or equal to the highest role of the bot, it won't be added <br/>
Alias : `+`
- `/(keeprole|kr) roles delete <role[,...]>` <br/>
Remove role(s) mentionned from the keeprole list <br/>
Aliases : `del`, `-`, `remove`, `rm`
- `/(keeprole|kr) members list` <br/>
Show the list of members that will get roles after joining your server (the list show also the roles concerned for each user)

### Vocal commands (Premium user only)
- `/(vocal|music) <on/off>` <br/>
Make the bot join or leave your voice channel
- ~~`/(vocal|music) play <url>`~~ **(DISABLED)** <br/>
Make the bot play the youtube video given. You can provide keywords instead of url and the bot will search and play the first result of your query. <br/>
Alias : `ytplay`
- `/(vocal|music) playlocal <song>` (Bot owner only) <br/>
Play the song given from the music directory of the bot <br/>
Alias : `localplay`
- `/(vocal|music) skip` <br/>
Skip the current song
- `/(vocal|music) pause` (Administrator only) <br/>
Pause the current playing song
- `/(vocal|music) resume` (Administrator only) <br/>
Resume the previously paused song
- `/(vocal|music) disconnectvocal` (Bot manager only) <br/>
Instant leave all the vocal channels where the bot is connected

### NSFW commands (NSFW channels only)
- `/nsfwjoke` <br/>
Same as joke, but will display a nsfw joke (always in french)
- `/hentai` <br/>
Do I need to explain what it does ?
- `/rule34` <br/>
Rule 34 of the internet : *if it exists, there is porn on it* <br/>
~~Just give a link to rule34 website~~

### RP/JDR commands
#### Main commands
- `/roll <expression>` <br/>
Roll dice and perform operations (supported symbols and operations : `*,+,-,/,()`) if given in the expression field. For rolling a dice, you have to use the litteral expression `xdy` where `x` is the number of dice rolled,  `d` the letter `d` and `y` the number of side of the dice (`1d100` will roll 1 dice with 100 sides for example). You can also roll special dice with your own values by writing them between brackets as following : `1d{red,blue,yellow,green}`. <br/>
Full example : `/roll (10+1d100)*(2d10-5d8)` will return the result of the following expression : `(10+(1 dice with 100 sides))*((2 dice with 10 sides)-(5 dice with 8 sides))` <br/>
Special dice example : `/roll 1d{1,2,3,4,5,6,7,8,9,10,Jack,Queen,King}+1d{Clubs,Diamonds,Hearts,Spades}` will return a single card with its value and its color (example : Queen of Spades) <br/>
Aliases : `rolldice`, `r`
- `/setmjrole <role>` (Administrator only) <br/>
Set the role that every user need on your server to create JDR and use GM/MJ commands after (the role have to be mentionned) <br/>
Aliases : `setgmrole`
- `/apart [mention[,...]]` (GM/MJ only and RP/JDR channel only) <br/>
Mute and deafen all the players that are not mentionned by the command. If there is no single mention, the bot will unmute and undeafen all the players. (Spectators and GM/MJ will not be affected by this)
- `/wiki <topic>` <br/>
Search on the wiki the given topic, if found a summary will be displayed with the link to the page
- `/jointhegame` <br/>
provide an invite link to the official discord of TTGC game (French discord) <br/>
Aliases : `jointtgc`, `ttgc`
- `/(jdr|rp) start <channel>` (GM/MJ only) <br/>
Start a RP/JDR in the mentionned channel <br/>
Alias : `create`
- `/(jdr|rp) delete <channel>` (Administrator only) <br/>
Delete a RP/JDR in the mentionned channel, this cannot be undone
- `/(jdr|rp) copy <from> <to>` (Administrator and GM/MJ only) <br/>
Copy a RP/JDR from a mentionned channel to an other. if the destination channel has already a RP/JDR, this will be totally replaced by the copy (no merging)
- `/(jdr|rp) extend <from> <to>` (Administrator and GM/MJ only) <br/>
Extend a RP/JDR through an other channel, the two channel will work with the same database and commands executed in one will affect the two channels. If a RP/JDR exists in the destination channel, it will be deleted.
- `/(jdr|rp) unextend <from> <to>` (Administrator only) <br/>
Unextend a RP/JDR through the precised channel, only source channel will contain the data after using that
- `/(jdr|rp) unextendall <from>` (Administrator only) <br/>
Unextend the RP/JDR in all the channel where there were extended, only source channel will contain data after using that
- `/(jdr|rp) list` (Administrator only) <br/>
Show the list of all RP/JDR existing in your server (extension won't be shown)

#### Character commands
- `/(character|char) create <race> <class> <namekey>` (MJ only and JDR channel only) <br/>
Create a new character with the given race and class and referenced by the namekey given. The race and class is the exact name of the race and class (french names), go to the website to know all existing classes. Use `_` instead of space character for race and class name. The namekey is not the same things as the name of the character, the namekey is just the unique identifier of the character and will be needed each time you will want to perform commands on this character <br/>
Alias : `+`
- `/(character|char) delete <namekey>` (MJ only and JDR channel only) <br/>
Delete a character (this cannot be undone once performed) <br/>
Aliases : `del`, `-`
- `/(character|char) link <charkey> <member>` (MJ only and JDR channel only) <br/>
Link a character to a discord account (only for the channel and server). An account can only be linked one time per JDR <br/>
Alias : `assign`
- `/(character|char) unlink [charkey]` (MJ only and JDR channel only) <br/>
Unlink a character previously linked with character link command, if not provided, unlink the character linked to you (and selected) <br/>
Alias : `unassign`
- `/(character|char) select <charkey>` (PJ only) <br/>
Select an other character. For selecting a character, you'll need to be linked first to this character with the `link` command. `character select` allow you to switch from a character to an other.
- `/(character|char) roll <stat> [<+|-> <expression>]` (PJ only) <br/>
Roll a dice in the given statistic and adding bonus or substracting malus if provided, the bonus/malus is formatted as for classical roll command and can be a complex expression such as `1d10-1d8+...`. The result will tell you if the action is a success or not, according to the rules of TTGC game. <br/>
Alias : `r`
- `/(character|char) set <item> <charkey> <value>` (MJ only and JDR channel only) <br/>
Set a property of a character to the given value. The following properties can be set with this command : <br/>
```
name - (text) Set the name of the character
hp/pv - (positive integer) Set the max HP of the character
mp/pm - (positive integer) Set the max Mana points of the character
force/str/strength - (integer between 1 and 100) Set the strength
esprit/spr/spirit - (integer between 1 and 100) Set the spirit
charisme/cha/charisma - (integer between 1 and 100) Set the charisma
agilite/furtivite/agi/agility - (integer between 1 and 100) Set the agility
lp/lightpt/lightpoint - (integer) Set the number of light point of the character
dp/darkpt/darkpoint - (integer) Same as lp but for the dark points
defaultmod/dmod - (offensiv/defensiv) Set the default mod of the character
defaultkarma/dkar/dkarma - (integer between -10 and 10) Set the default karma
intuition/int/instinct - (integer between 1 and 6) Set the intuition
```
- `/(character|char) damage <charkey> <amount>` (MJ only and JDR channel only) <br/>
Damage a character, he will lose the number of HP given in the command <br/>
Alias : `dmg`
- `/(character|char) heal <charkey> <amount>` (MJ only and JDR channel only) <br/>
Heal a character with the number of points given
- `/(character|char) getpm <charkey> <amount>` (MJ only and JDR channel only) <br/>
Restore the given amount of mana points provided, if the amount is negative, the character will lose mana points <br/>
Alias : `getmp`
- `/(character|char) setkarma <charkey> <amount>` (MJ only and JDR channel only) <br/>
Add or substract karma points to the current karma of the character <br/>
Aliases : `addkarma`, `getkarma`
- `/(character|char) reset <charkey>` (MJ only and JDR channel only) <br/>
Restore fully Health and Mana points, set the karma to its default value and set the mod to its default value for a character
- `/(character|char) pay <amount>` (PJ only) <br/>
Pay the amount given
- `/(character|char) earnmoney <charkey> <amount>` (MJ only and JDR channel only) <br/>
Give to the character the amount of money provided <br/>
Alias : `earnpo`
- `/(character|char) info` (PJ only) <br/>
Display all the current informations of your character
- `/(character|char) stat` (PJ only) <br/>
Display statistics about dice rolled for your character
- `/(character|char) use <item>` (PJ only) <br/>
Consume an item from your inventory
- `/(character|char) use lightpt` (PJ only) <br/>
Consume a light point from your current character <br/>
Aliases : `lp`, `lightpoint`
- `/(character|char) use darkpt` (PJ only) <br/>
Consume a dark point from your current character <br/>
Aliases : `dp`, `darkpoint`
- `/(character|char) switchmod` (PJ only) <br/>
Switch your current mod between offensive and defensive mods <br/>
Alias : `switchmode`
- `/(character|char) setmental [+|-] <amount>` (PJ only) <br/>
Set the mental health of your character with the given value, if `+` or `-` is provided in the command, the amount will be added respectivly substracted to your mental health
- `/(character|char) lvlup <charkey>` (MJ only and JDR channel only) <br/>
Give one more level to the character and announce the bonus for this level <br/>
Alias : `levelup`
- `/(character|char) kill <charkey>` (MJ only and JDR channel only) <br/>
Kill definitively a character, this will unlink it from its owner and the character wont be playable anymore
- `/(character|char) export <charkey> [language]` (MJ only and JDR channel only) <br/>
Export a character to PDF format using LaTeX technology, and send the generated file through discord. By default, the generated PDF is in french, use `EN` value for `language` to output in english your character.
- `/(character|char) xp <charkey> <amount> [allowlevelup]` (MJ only and JDR channel only) <br/>
Give XP to a character. XP is printed on exported PDF from the character, but it can also be used by the level system. if allowlevelup is true, then every 100 XP, the character will automatically earn one level. It is highly recomended to use all the time the same value for allowlevelup parameter to avoid xp to level conversion errors. <br/>
Alias : `exp`

#### Global commands
- `/global damage <amount>` (MJ only and JDR channel only) <br/>
Damage all the characters with the number of points given <br/>
Alias : `dmg`
- `/global heal <amount>` (MJ only and JDR channel only) <br/>
Heal all the characters with the number of points given
- `/global getpm <amount>` (MJ only and JDR channel only) <br/>
Add the given amount of mana points to all the characters, if the amount is negative, the characters will lose mana points <br/>
Alias : `getmp`
- `/global stat` (JDR channel only) <br/>
Display statistics about dice rolled for the group

#### GM/MJ commands
- `/mj transfer <member>` (MJ only and JDR channel only) <br/>
transfer ownership of a JDR to the mentionned user, this user need to have the MJ role and to accept the request
- `/mj ...` (MJ only and JDR channel only) <br/>
Use a PJ command when you are MJ, theese commands works exactly as the same character commands. The `mj` prefix replace the `character` or `char` prefix and the commands work with sames arguments, the result will also be the same. For example `/mj info` will produce same result as `/character info` but you will have to precise for wich character this commands must be used for as the following : `/mj info <charkey>`. Refers to the PJ commands' doc to know result and how arguments works for each commands <br/>
The following commands can be used : <br/>
```
/mj (info|charinfo|characterinfo) <charkey>
/mj (switchmod|switchmode) <charkey>
/mj pay <charkey> <amount>
/mj setmental <charkey> [+|-] <amount>
/mj (roll|r) <charkey> <stat> [<+|-> <expression>]
/mj pet (roll|r) <charkey> <petkey> <stat> [<+|-> <expression>]
/mj pet (switchmod|switchmode) <charkey> <petkey>
/mj pet info <charkey> <petkey>
/mj (inventory|inv) <charkey>
```

#### Skill commands
- `/skill` (PJ only) <br/>
Show the list of skills of your character <br/>
Alias : `sk`
- `/(skill|sk) info <query>` (JDR channel only) <br/>
Search skills in the database with their names. Use quotes or underscore for searching skills wich contains several words.
- `/(skill|sk) assign <charkey> <skill>` (MJ only and JDR channel only) <br/>
Assign a skill to a character. Prefer using ID instead of name to avoid conflict between skills with similar names. To get a skill ID, you can use `skill info` command.

#### Pet commands
- `/pet add <charkey> <petkey>` (MJ only and JDR channel only) <br/>
Pet are linked to a single character and cannot be shared, they allow the owner of the character to execute standard PJ commands for pets. A character can have multiple pet and each of them have an unique identifier the `petkey` such as the `charkey` for characters.<br/>
This command add a new pet to a character <br/>
Alias : `+`
- `/pet remove <charkey> <petkey>` (MJ only and JDR channel only) <br/>
Remove and delete completly a pet, this cannot be undone and have no confirmation message<br/>
Aliases : `-`, `delete`, `del`, `rm`
- `/pet set <item> <charkey> <petkey> <value>` (MJ only and JDR channel only) <br/>
Such as `character set` set a value of a pet. The same shortcuts as for `character set` are still avalaible. Only the following attributes are avalaible :<br/>
```
name
species
hp/pm
strength/spirit/charisma/agility
instinct (replace intuition)
defaultmod
```
- `/pet switchmod <petkey>` (PJ only) <br/>
Switchmod for a pet <br/>
Alias : `switchmode`
- `/pet lvlup <charkey> <petkey>` (MJ only and JDR channel only) <br/>
Levels are not linked between characters and their pets. So to level up a pet you have to use this commands <br/>
Alias : `levelup`
- `/pet roll <petkey> <stat> [+bonus/-malus]` (PJ only) <br/>
Roll the dice for your pet, same rules as for classical `roll` command <br/>
Alias : `r`
- `/pet info <petkey>` (PJ only) <br/>
Show informations about your pet such as `character info`
- `/pet setkarma <charkey> <petkey> <value>` (MJ only and JDR channel only) <br/>
Equivalent of `setkarma` for pets
- `/pet stat <petkey>` (PJ only) <br/>
Show all stat of a pet you have (such as `/stat` for characters)
- `/pet damage <charkey> <petkey> <amount>` (MJ only and JDR channel only) <br/>
Inflict damages to a pet <br/>
Alias : `dmg`
- `/pet heal <charkey> <petkey> <amount>` (MJ only and JDR channel only) <br/>
Heal a pet <br/>
Alias : `cure`
- `/pet getpm <charkey> <petkey> <amount>` (MJ only and JDR channel only) <br/>
Manage MP for a pet such as `getPM` for a character <br/>
Alias : `getmp`

#### Map commands
- `/map` (MJ only and JDR channel only) <br/>
Display the world map of Terae
- `/map show <width> <height> [depth]` (MJ only and JDR channel only) <br/>
Show the local fight map displaying all tokens and effects registered for the current game. Only effects affecting this depth (Z axis) given will be displayed, if not given, depth is considered equal to 0.
- `/map clear` (MJ only and JDR channel only) <br/>
Clear all tokens and effects on your local fight map <br/>
Aliases : `clr`, `reset`
- `/map (token|tk) add <name>` (MJ only and JDR channel only) <br/>
Add a token on your local fight map, a token represents an entity that can be moved and can generate area of effects (AOE). When created, the token will automatically put on the origin (0;0;0) of the map. Use token move command to move it. <br/>
Alias : `+`
- `/map (token|tk) remove <name>` (MJ only and JDR channel only) <br/>
Remove a token from your local fight map <br/>
Aliases : `rm`, `delete`, `del`, `map token -`, `-`
- `/map token move <name> <dx> <dy> [dz]` (MJ only and JDR channel only) <br/>
Move a token in the direction given by the vector (dx;dy;dz). If not given dz is equal to 0 <br/>
Alias : `mv`
- `/map effect add <tkname> <dx> <dy> <dz> <shape> [parameters]` (MJ only and JDR channel only) <br/>
Register an area of effect for a given token. shape must be one of the following : `circle`,`sphere`,`line`,`rect`,`cube`,`conic`. Each of theese shape have their own parameters, some of them have to be given for the generation. <br/>
The parameters format is a list of key/value separated by space characters. The key/value pair should be as following : `key=value`.
Alias : `+` <br/>
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
Clear all effects for the given token <br/>
Aliases : `clr`, `reset`

#### Inventory commands
- `/(inventory|inv)` (PJ only) <br/>
Show your current inventory
- `/(inventory|inv) add <charkey> <item> [number] [weight]` (MJ only and JDR channel only) <br/>
Add the number of item to the inventory of the character, by default number is equal to 1 and weight to 1.0. The item name must not contains space char or need to be escaped with `""` (write `"healing potion"` instead of `healing potion`) <br/>
Aliases : `+`, `append`
- `/(inventory|inv) remove <charkey> <item> [number]` (MJ only and JDR channel only)<br/>
Remove the number of item from the inventory of the character, by default number is equal to 1. Item name must not contains spaces like for `inventory add` command <br/>
Aliases : `rm`, `delete`, `del`, `-`

#### Finalize commands
- `/finalize` (MJ only and JDR channel only) <br/>
This command will start the finalizing operation displaying credits with some random informations of your game and also your own finalize fields. After that, the JDR will be fully deleted from the database.
- `/finalize set <title>` (MJ only and JDR channel only) <br/>
Set the finalize field with the given title (if it doesn't exists, it will be created)
- `/finalize delete <title>` (MJ only and JDR channel only) <br/>
Delete the finalize field given <br/>
Aliases : `del`, `-`, `remove`, `rm`

### Bot Management (Bot Manager only)
- `/blacklist <user_id> | <reason>` (Bot manager only) <br/>
Blacklist a user, he won't be able to use any commands of this bot by blacklisting him
- `/unblacklist <user_id>` (Bot manager only) <br/>
Unblacklist someone
- `/purgeserver <days>` (Bot manager only) <br/>
Delete servers from the database that have kicked the bot at least number of days given ago
