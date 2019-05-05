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

from src.checks import *
from src.BotTools import *
from discord.ext import commands
import logging,asyncio
import discord
from src.Translator import *
from src.VocalUtilities import *
import os

class Vocal(commands.Cog):
    def __init__(self,bot,logger):
        self.bot = bot
        self.logger = logger
        self.vocalcore = VocalCore(self.bot,self.logger)

    @commands.check(check_premium)
    @commands.bot_has_permissions(connect=True,speak=True)
    @commands.group(invoke_without_command=False,aliases=["music"])
    async def vocal(self,ctx):
        if self.vocalcore.getvocal(str(ctx.message.guild.id)) is None:
            VocalSystem(str(ctx.message.guild.id),self.vocalcore)

    @vocal.command(name="on")
    async def vocal_on(self,ctx):
        data = GenericCommandParameters(ctx)
        if ctx.message.author.voice.channel is None:
            await ctx.message.channel.send(data.lang["vocal_cantconnect"])
        else:
            await self.vocalcore.getvocal(str(ctx.message.guild.id)).join(ctx.message.author.voice.channel,ctx.message.channel,data.lang)

    @vocal.command(name="off")
    async def vocal_off(self,ctx):
        await self.vocalcore.getvocal(str(ctx.message.guild.id)).leave()

    @vocal.command(name="play",aliases=["ytplay"])
    async def vocal_play(self,ctx,*,search):
        await self.vocalcore.getvocal(str(ctx.message.guild.id)).append(search)

    @commands.check(check_botowner)
    @vocal.command(name="playlocal",aliases=["localplay"])
    async def vocal_playlocal(self,ctx,*,search):
        vc = self.vocalcore.getvocal(str(ctx.message.guild.id))
        if not os.access("Music/",os.F_OK) or not search in os.listdir("Music/") or not "{}.mp3".format(search) in os.listdir("Music/") or not "{}.wav".format(search) in os.listdir("Music/"):
            await vc.textchan.send(vc.lang["playlocal_notfound"])
        else:
            path = search
            if "{}.mp3".format(search) in os.listdir("Music/"): path += ".mp3"
            elif "{}.wav".format(search) in os.listdir("Music/"): path += ".wav"
            await vc.append(path,False)

    @vocal.command(name="skip")
    async def vocal_skip(self,ctx):
        self.vocalcore.getvocal(str(ctx.message.guild.id)).skip()

    @command.check(check_admin)
    @vocal.command(name="pause")
    async def vocal_pause(self,ctx):
        self.vocalcore.getvocal(str(ctx.message.guild.id)).pause()

    @command.check(check_admin)
    @vocal.command(name="resume")
    async def vocal_resume(self,ctx):
        self.vocalcore.getvocal(str(ctx.message.guild.id)).resume()

    @command.check(check_botmanager)
    @vocal.command(name="disconnectall",aliases=["forcedisconect"])
    async def vocal_disconnectall(self,ctx):
        await ctx.message.channel.send("This will disconnect the bot from all vocal connections, are you sure ?\nType `confirm` to perform this")
        chk = lambda m: m.author == ctx.message.author and m.channel == ctx.message.channel and m.content.lower() == 'confirm'
        try: answer = await self.bot.wait_for('message',check=chk,timeout=60)
        except asyncio.TimeoutError: answer = None
        if answer is None:
            await ctx.message.channel.send("your request has timeout")
        else:
            await self.vocalcore.interupt(ctx)