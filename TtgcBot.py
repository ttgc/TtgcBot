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
    print("server joined")

@client.event
async def on_guild_remove(guild):
    print("server removed")

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
    global statut
    await client.change_presence(activity=statut)
    botaskperm = discord.Permissions().all()
    botaskperm.administrator = botaskperm.manage_channels = botaskperm.manage_guild = botaskperm.manage_webhooks = botaskperm.manage_emojis = botaskperm.manage_nicknames = botaskperm.move_members = False
    url = discord.utils.oauth_url(str(client.user.id),botaskperm)
    print(url)

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
