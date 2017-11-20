#!usr/bin/env python3.4
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

from threading import Thread
import time
import asyncio
import discord

def singleton(classe_definie):
    instances = {} # Dictionnaire de nos instances singletons
    def get_instance():
        if classe_definie not in instances:
            # On crée notre premier objet de classe_definie
            instances[classe_definie] = classe_definie()
        return instances[classe_definie]
    return get_instance

@singleton
class VocalCore:
    def __init__(self):
        self.bot = None
        self.loop = asyncio.get_event_loop()
        self.voclist = {}

    def _addtolist(self,servid,vocobj):
        if not servid in self.voclist:
            self.voclist[servid] = vocobj
            return True
        return False

    def removefromlist(self,servid):
        if servid in self.voclist:
            vocobj = self.voclist[servid]
            del(vocobj)
            del(self.voclist[servid])
            return True
        return False

    def getvocal(self,servid):
        if servid in self.voclist:
            return self.voclist[servid]
        return None

    @asyncio.coroutine
    def interupt(self):
        for i in self.voclist.keys():
            if self.voclist[i].vocal:
                yield from self.bot.send_message(self.voclist[i].textchan,":x: System interuption launched by administrators, vocal disconnected")
                yield from self.voclist[i].leave()
            vocobj = self.voclist[i]
            del(vocobj)
            self.voclist[i] = None
        self.voclist = {}
                
        
class VocalSystem:
    def __init__(self,servid,vc=VocalCore()):
        self.vocal = False
        self.co = None
        self.loop = vc.loop
        self.timer = VocalTimeout(60,self.loop)
        self.queue = []
        self.current = None
        self.is_playing = False
        self.textchan = None
        self.bot = vc.bot
        vc._addtolist(servid,self)

    @asyncio.coroutine
    def join(self,chan,textchan):
        self.vocal = True
        self.co = yield from self.bot.join_voice_channel(chan)
        self.textchan = textchan
        self.timer.start()

    @asyncio.coroutine
    def append(self,path,yt=True):
        self.timer.reset()
        if not self.vocal: return
        if yt:
            song = yield from self.co.create_ytdl_player(path,ytdl_options={"noplaylist":True,"playlist_items":"1"},after=self.after)
        else:
            song = self.co.create_ffmpeg_player(path,after=self.after)
        self.queue.append(song)
        self.timer.reset()

    def play(self):
        if not self.vocal: return
        if self.is_playing: return
        if len(self.queue) == 0:
            self.is_playing = False
            return
        self.is_playing = True
        self.timer = VocalTimeout(60,self.loop)
        self.queue[0].start()
        self.current = self.queue[0]
        del(self.queue[0])

    def after(self):
        if not self.vocal: return
        self.is_playing = False
        self.play()
        if not self.is_playing:
            self.current = None
            self.queue = []
            #self.timer = VocalTimeout(60)
            self.timer.start()

    def skip(self):
        if not self.vocal: return
        if not self.is_playing: return
        if not self.current.is_done():
            self.current.stop()
        #del(self.queue[0])
        #self.after()             

    @asyncio.coroutine
    def leave(self):
        self.vocal = False
        yield from self.co.disconnect()
        self.co = None
        self.timer = VocalTimeout(60,self.loop)
        self.queue = []
        self.current = None
        self.is_playing = False
        self.textchan = None

    @asyncio.coroutine
    def _timeout_leave(self):
        yield from self.bot.send_message(self.textchan,"Leaving Voice for inactivity")
        yield from self.leave()

class VocalTimeout(Thread):
    def __init__(self,tmax,loop):
        Thread.__init__(self)
        self.timer = 0
        self.tmax = tmax
        self.from_ = None
        self.current = None
        self.timeout = False
        self.loop = loop
        #self.loop = asyncio.get_event_loop()

    def run(self):
        self.from_ = time.clock()
        self.current = time.clock()
        self.timer = self.current - self.from_
        while self.timer < self.tmax:
            self.current = time.clock()
            self.timer = self.current - self.from_
            time.sleep(0.01)
        self.timeout = True
        system = VocalSystem()
        if self == system.timer and system.vocal and (not system.is_playing):
            self.loop.create_task(system._timeout_leave())
            #loop = asyncio.get_event_loop()
            #asyncio.set_event_loop(loop)
            #loop.run_until_complete(system._timeout_leave())
            #asyncio.async(system._timeout_leave())

    def reset(self):
        self.from_ = time.clock()
