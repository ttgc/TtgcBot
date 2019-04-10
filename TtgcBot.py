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

# external and python libs
import discord
import asyncio
# from random import randint,choice
# from threading import Thread
import logging
# import time
# import os
# import zipfile
# import sys
# import requests
# import subprocess as sub
# import traceback

# custom libs
from logs import *
from INIfiles import *
# from parsingdice import *
# from VocalUtilities import *
# from Character import *
# from CharacterUtils import *
# from converter import *
from BotTools import *
from Translator import *
# from mapmanager import *

global logger
logger = initlogs()

global TOKEN
tokenf = INI()
tokenf.load("token")
TOKEN = tokenf.section["TOKEN"]["Bot"]
del(tokenf)

global statut
statut = discord.Game(name="Ohayo !")

global client
client = discord.Client()

@client.event
async def on_message(message):
    if message.author.id != client.user.id: print("hello world !")

@client.event
async def on_member_join(member):
    print("member joined")

@client.event
async def on_member_remove(member):
    print("member removed")

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
    message = args[0]
    lgcode = getuserlang(str(message.author.id))
    if not lang_exist(lgcode): lgcode = "EN"
    lang = get_lang(lgcode)
    logging.warning(traceback.format_exc())
    await client.send_message(message.channel,lang["error"].format(traceback.format_exc(limit=1000)))

@client.event
async def on_ready():
    global statut,logger
    logger.info("Successful connected. Initializing bot system")
    await client.change_presence(activity=statut)
    botaskperm = discord.Permissions().all()
    botaskperm.administrator = botaskperm.manage_channels = botaskperm.manage_guild = botaskperm.manage_webhooks = botaskperm.manage_emojis = botaskperm.manage_nicknames = botaskperm.move_members = False
    url = discord.utils.oauth_url(str(client.user.id),botaskperm)
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

async def main():
    global TOKEN
    await client.login(TOKEN)
    await client.connect()

loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(main())
except:
    loop.run_until_complete(client.logout())
finally:
    loop.close()
