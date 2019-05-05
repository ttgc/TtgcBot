#!usr/bin/env python3.7
#-*-coding:utf-8-*-
#Vocal Utilities for Turtle Bot

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

import asyncio
import discord
import youtube_dl
import logging

# def singleton(classe_definie):
#     instances = {} # Dictionnaire de nos instances singletons
#     def get_instance():
#         if classe_definie not in instances:
#             # On crée notre premier objet de classe_definie
#             instances[classe_definie] = classe_definie()
#         return instances[classe_definie]
#     return get_instance
#
# @singleton
class VocalCore:
    def __init__(self,bot,logger):
        self.bot = bot
        self.logger = logger
        self.voclist = {}

    def _addtolist(self,servid,vocobj):
        if not servid in self.voclist:
            self.logger.log(logging.DEBUG+1,"vocalcore - server added to list : %s",servid)
            self.voclist[servid] = vocobj
            return True
        self.logger.log(logging.DEBUG+1,"vocalcore - cannot add server %s to list, already exist",servid)
        return False

    def removefromlist(self,servid):
        if servid in self.voclist:
            vocobj = self.voclist[servid]
            del(vocobj)
            del(self.voclist[servid])
            self.logger.log(logging.DEBUG+1,"vocalcore - server removed from list : %s",servid)
            return True
        self.logger.log(logging.DEBUG+1,"vocalcore - cannot remove server %s from list, doesnt exist",servid)
        return False

    def getvocal(self,servid):
        if servid in self.voclist:
            return self.voclist[servid]
        return None

    async def interupt(self,ctx):
        self.logger.warning("Vocal service interuption requested by botmanager")
        for i in list(self.voclist.keys()):
            if self.voclist[i].vocal:
                await self.voclist[i].textchan.send(":x: System interuption launched by administrators, vocal disconnected")
                await self.voclist[i].leave(True)
                asyncio.sleep(1)
            self.removefromlist(i)
        await ctx.message.channel.send("Vocal service disconnected successful")

class VocalSystem:
    def __init__(self,servid,vc):
        self.vocal = False
        self.co = None
        self.queue = []
        self.textchan = None
        self.vocalchan = None
        self.bot = vc.bot
        self.logger = vc.logger
        self.lang = None
        vc._addtolist(servid,self)

    async def join(self,chan,textchan,lang):
        self.vocal = True
        self.co = await chan.connect()
        self.vocalchan = chan
        self.textchan = textchan
        self.lang = lang
        self.logger.info("Joining vocal channel %d (binding to text channel %d) on server %d",self.vocalchan.id,self.textchan.id,self.vocalchan.guild.id)
        await self.textchan.send(self.lang["vocal_on"].format(str(self.vocalchan),str(self.textchan)))

    async def append(self,path,yt=True):
        self.vocal = self.co is not None and self.co.is_connected()
        if not self.vocal: return
        if yt:
            with youtube_dl.YoutubeDL({"no_playlist":True,"playlist_items":"1","default_search":"ytsearch"}) as ydl:
                song_info = ydl.extract_info(path,download=False)
                if "entries" in song_info: song_info = song_info["entries"][0]
                path = ydl.urllopen(song_info["webpage_url"]).file
            #path = song_info#["webpage_url"]
            name = song_info["title"]
        else:
            name = path.replace("\\","/").split("/")[-1]
        song = discord.FFmpegPCMAudio(path)
        if not self.co.is_playing():
            self.co.play(song,after=lambda err: asyncio.run_coroutine_threadsafe(self.after(),self.bot.loop))
        self.queue.append((name,song))
        self.logger.info("added song %s (%s) to queue on server %d",name,path,self.vocalchan.guild.id)
        await self.textchan.send(self.lang["vocal_play"].format(name))

    async def after(self):
        self.queue.pop(0)
        self.vocal = self.co is not None and self.co.is_connected()
        if not self.vocal: return
        if len(self.queue) == 0:
            await self.textchan.send(self.lang["vocal_stop"])
            self.logger.info("finished playing on server %d",self.vocalchan.guild.id)
        else:
            self.co.play(self.queue[0][1],after=lambda err: asyncio.run_coroutine_threadsafe(self.after(),self.bot.loop))
            await self.textchan.send(self.lang["vocal_next"].format(self.queue[0][0]))
            self.logger.info("playing next song on server %d",self.vocalchan.guild.id)

    async def skip(self):
        self.vocal = self.co is not None and self.co.is_connected()
        if not self.vocal: return
        if not self.co.is_playing(): return
        self.co.stop()
        await self.textchan.send(self.lang["musicskip"])
        self.logger.info("skipping song on server %d",self.vocalchan.guild.id)

    async def pause(self):
        self.vocal = self.co is not None and self.co.is_connected()
        if not self.vocal: return
        self.co.pause()
        self.logger.info("pausing vocal on server %d",self.vocalchan.guild.id)
        await self.textchan.send(self.lang["vocal_pause"])

    async def resume(self):
        self.vocal = self.co is not None and self.co.is_connected()
        if not self.vocal: return
        self.co.resume()
        self.logger.info("resuming vocal on server %d",self.vocalchan.guild.id)
        await self.textchan.send(self.lang["vocal_resume"])

    async def leave(self,forced=False):
        self.vocal = False
        await self.co.disconnect(force=forced)
        self.logger.info("leaving voice channel on server %d",self.vocalchan.guild.id)
        await self.textchan.send(self.lang["vocal_off"])
        self.co = None
        self.queue = []
        self.vocalchan = None
        self.textchan = None
        self.lang = None
