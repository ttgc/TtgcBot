#!usr/bin/env python3.7
#-*-coding:utf-8-*-

##    TtgcBot - a bot for discord
##    Copyright (C) 2017  Thomas PIOT
##
##    This program is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this program. If not, see <http://www.gnu.org/licenses/>

# import external and python libs
import discord
from discord.ext import commands
import asyncio
import logging
import traceback
import os
import sys
# from random import randint,choice
# from threading import Thread
# import time
# import zipfile
# import requests
# import subprocess as sub

# import custom libs
from src.utils.inits import *
# from src.utils.INIfiles import *
from src.utils.config import *
from src.tools.BotTools import *
from src.tools.Translator import *
from src.utils.checks import *
from src.help import *
# from parsingdice import *
# from VocalUtilities import *
# from Character import *
# from CharacterUtils import *
# from converter import *
# from mapmanager import *

# import Cogs
from src.cogs.BotManage import *
from src.cogs.Moderation import *
from src.cogs.Other import *
from src.cogs.NSFW import *
#from src.cogs.Keeprole import *
#from src.cogs.Vocal import *
from src.cogs.jdr.MainJDR import *
from src.cogs.jdr.CharacterCog import *
from src.cogs.jdr.SkillCog import *
from src.cogs.jdr.MJ import *
from src.cogs.jdr.PetCog import *
from src.cogs.jdr.JDRGlobal import *
from src.cogs.jdr.Finalize import *
#from src.cogs.jdr.Maps import *
from src.cogs.jdr.InventoryCog import *

global logger
global TOKEN

# Initialize bot status
global statut
statut = discord.Game(name=Config()["discord"]["default-game"])

# Get prefix function
def get_prefix(bot,message):
    try:
        srv = DBServer(str(message.guild.id))
        return srv.prefix
    except (AttributeError,DatabaseException): return Config()["discord"]["default-prefix"]

# Initialize client
global client
client = discord.ext.commands.Bot(get_prefix, case_insensitive=True, activity=statut, intents=discord.Intents.all())

# Global checks
@client.check
def no_pm(ctx): return ctx.message.guild is not None

@client.check
def isbot(ctx): return not ctx.message.author.bot

@client.check
async def blacklist(ctx):
    srv = DBServer(str(ctx.message.guild.id))
    blacklisted,reason = is_blacklisted(str(ctx.message.author.id))
    if blacklisted:
        lgcode = getuserlang(str(ctx.message.author.id))
        if not lang_exist(lgcode): lgcode = "EN"
        lang = get_lang(lgcode)
        await ctx.message.channel.send(lang["blacklisted"].format(ctx.message.author.mention,str(reason)))
    return not blacklisted

# Client events
# @client.event
# async def on_message(message):
#     if not message.content.startswith(get_prefix(client,message)):
#         if message.guild is not None and message.author != client.user:
#             srv = DBServer(str(message.guild.id))
#             filtre = srv.wordblocklist()
#             for i in filtre:
#                 if i in message.content:
#                     lgcode = getuserlang(str(message.author.id))
#                     if not lang_exist(lgcode): lgcode = "EN"
#                     lang = get_lang(lgcode)
#                     await message.delete()
#                     await message.author.send(lang["contentbanned"])
#                     return
#     else:
#         ctx = await client.get_context(message)
#         await client.invoke(ctx)

@client.event
async def on_command_error(ctx,error):
    global logger
    lgcode = getuserlang(str(ctx.message.author.id))
    if not lang_exist(lgcode): lgcode = "EN"
    lang = get_lang(lgcode)
    msg = lang["error"].format(error)

    if isinstance(error,commands.CommandNotFound): msg = lang["error_notfound"]
    elif isinstance(error,commands.MissingPermissions): msg = lang["error_selfperms"]
    elif isinstance(error,commands.BotMissingPermissions): msg = lang["error_perms"]
    elif isinstance(error,commands.NSFWChannelRequired): msg = lang["error_nsfw"]
    elif isinstance(error,commands.DisabledCommand): msg = lang["error_disabled"]
    elif isinstance(error,commands.CheckFailure): return
    elif isinstance(error,commands.UserInputError): msg = lang["error_argument"]
    elif isinstance(error,commands.CommandOnCooldown): msg = lang["error_cd"].format("{0:.2f}".format(error.retry_after))
    else: logger.warning(error)
    await ctx.message.channel.send(msg)

# @client.event
# async def on_member_join(member):
#     global logger
#     srv = DBServer(str(member.guild.id))
#     userblocked = srv.blockuserlist()
#     for i in userblocked:
#         if i in str(member).split("#")[0]:
#             await asyncio.sleep(1)
#             await member.ban(delete_message_days=1)
#             try: logger.info("Auto banned user '%s'(ID=%s) from guild '%s'(ID=%s) because of blockuserlist",str(member),str(member.id),str(member.guild),str(member.guild.id))
#             except: logger.info("Auto banned user '%s' from guild '%s' because of blockuserlist",str(member.id),str(member.guild.id))
#             return
#     if srv.keepingrole:
#         await asyncio.sleep(1)
#         await srv.restorerolemember(member.guild,member)
#         try: logger.info("Restored user roles for %s(ID=%s) in guild %s(ID=%s)",str(member),str(member.id),str(member.guild),str(member.guild.id))
#         except: logger.info("Restored user roles for %s in guild %s",str(member.id),str(member.guild.id))

# @client.event
# async def on_member_remove(member):
#     srv = DBServer(str(member.guild.id))
#     if srv.keepingrole:
#         srv.backuprolemember(member)
#         try: logger.info("Backuped user roles for %s(ID=%s) in guild %s(ID=%s)",str(member),str(member.id),str(member.guild),str(member.guild.id))
#         except: logger.info("Backuped user roles for %s in guild %s",str(member.id),str(member.guild.id))

@client.event
async def on_guild_join(guild):
    global logger
    addserver(guild)
    try: logger.info("Added server '%s' to the database : ID=%s",str(guild),str(guild.id))
    except: logger.info("Added server to the database : ID=%s",str(guild.id))

@client.event
async def on_guild_remove(guild):
    global logger
    srv = DBServer(str(guild.id))
    srv.remove()
    logger.info("Removed server from the database : ID=%s",str(guild.id))

@client.event
async def on_error(event,*args,**kwargs):
    global logger
    logger.error(traceback.format_exc())
    # infos = await client.application_info()
    # await infos.owner.send(get_lang()["error"].format(traceback.format_exc(limit=100)))
    client.get_cog("Bot Management").handlederror += 1

@client.event
async def on_connect():
    global client, logger
    if len(client.cogs) > 0: return

    await client.add_cog(BotManage(client,logger))
    await client.add_cog(Moderation(client,logger))
    await client.add_cog(Other(client,logger))
    await client.add_cog(NSFW(client,logger))
    #await client.add_cog(Keeprole(client,logger))
    #await client.add_cog(Vocal(client,logger))
    await client.add_cog(MainJDR(client,logger))
    await client.add_cog(CharacterCog(client,logger))
    await client.add_cog(SkillCog(client,logger))
    await client.add_cog(PetCog(client,logger))
    await client.add_cog(JDRGlobal(client,logger))
    await client.add_cog(Finalize(client,logger))
    #await client.add_cog(Maps(client,logger))
    await client.add_cog(InventoryCog(client,logger))
    await client.add_cog(MJ(client,logger))

    test_guild = Config()['discord']['test-guild']
    if test_guild is not None:
        logger.log(12, "Test guild provided. Copying global command to test guild.")
        client.tree.copy_global_to(guild=discord.Object(id=test_guild))

    await client.tree.sync()

@client.event
async def on_ready():
    global statut, logger
    logger.info("Successful connected. Initializing bot system")
    botaskperm = discord.Permissions().all()
    botaskperm.administrator = botaskperm.manage_channels = botaskperm.manage_guild = botaskperm.manage_webhooks = botaskperm.manage_emojis = botaskperm.manage_nicknames = botaskperm.move_members = False
    url = discord.utils.oauth_url(client.user.id, permissions=botaskperm)
    print(url)
    logger.info("Generate invite link : %s",url)
    srvid,nbr = [],0
    for i in client.guilds:
        srvid.append(str(i.id))
        if str(i.id) not in srvlist():
            addserver(i)
            nbr += 1
            try: logger.info("This server has invited the bot during off period, adding it to the database : %s (ID=%s)",str(i),str(i.id))
            except: logger.info("Server added (ID=%s)",str(i.id))
    logger.info("Added %d new servers to the database successful",nbr)
    logger.info("Purged %d servers wich have kicked the bot at least one year ago successful",purgeservers(365))
    nbr = 0
    for i in srvlist():
        if i not in srvid:
            srv = DBServer(i)
            srv.remove()
            nbr += 1
            logger.info("This server has kicked the bot during off period, removing it from the database : ID=%s",str(i))
    logger.info("Removed %d old servers from the database successful",nbr)
    logger.info("Bot is now ready")

@client.event
async def on_resumed():
    global logger
    logger.info("Resumed session")

# ========== MAIN ========== #
def main():
    # Initialize logs
    global logger
    logger = initlogs()

    # Check bot directories and files
    initdirs(logger)
    checkfiles(logger)

    # Get bot Token
    global TOKEN
    TOKEN = Config()["token"]

    # Boot
    logger.info("Starting TtgcBot alpha 3.0")
    client.run(TOKEN)

# Launch the bot
if __name__ == "__main__":
    main()
