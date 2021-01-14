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

from src.utils.checks import *
from src.tools.BotTools import *
from discord.ext import commands
import logging,asyncio
import discord
from src.tools.Translator import *
from src.tools.VocalUtilities import *
from src.utils.config import *
import os

class Vocal(commands.Cog, command_attrs=dict(enabled=Config()["vocal"])):
    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger
        self.vocalcore = VocalCore(self.bot, self.logger)

    @commands.check(check_premium)
    @commands.group(invoke_without_command=False, aliases=["music"])
    async def vocal(self, ctx):
        if self.vocalcore.getvocal(str(ctx.message.guild.id)) is None:
            VocalSystem(str(ctx.message.guild.id), self.vocalcore)

    @vocal.command(name="on")
    async def vocal_on(self, ctx):
        """**Premium Only**
        Join vocal. You have to be also in a vocal channel"""
        data = await GenericCommandParameters(ctx)
        vc = self.vocalcore.getvocal(str(ctx.message.guild.id))
        if ctx.message.author.voice is None:
            await ctx.message.channel.send(data.lang["vocal_cantconnect"])
        else:
            if not vc.vocal: await vc.join(ctx.message.author.voice.channel, ctx.message.channel, data.lang)

    @vocal.command(name="off")
    async def vocal_off(self, ctx):
        """**Premium Only**
        Leave vocal"""
        vc = self.vocalcore.getvocal(str(ctx.message.guild.id))
        if vc.vocal: await vc.leave()

    @vocal.command(name="play", aliases=["ytplay"], enabled=False)
    async def vocal_play(self, ctx, *, search):
        """**Premium Only** / **Disabled command**
        Play a song from YouTube"""
        await self.vocalcore.getvocal(str(ctx.message.guild.id)).append(search, ctx=ctx)

    @commands.check(check_botowner)
    @vocal.command(name="playlocal", aliases=["localplay"], hidden=True)
    async def vocal_playlocal(self, ctx, *, search):
        vc = self.vocalcore.getvocal(str(ctx.message.guild.id))
        if not os.access("Music/",os.F_OK) or (not search in os.listdir("Music/") and not "{}.mp3".format(search) in os.listdir("Music/") and not "{}.wav".format(search) in os.listdir("Music/")):
            await vc.textchan.send(vc.lang["playlocal_notfound"])
        else:
            path = search
            if "{}.mp3".format(search) in os.listdir("Music/"): path += ".mp3"
            elif "{}.wav".format(search) in os.listdir("Music/"): path += ".wav"
            await vc.append("Music/{}".format(path), False)

    @commands.cooldown(1, 2, commands.BucketType.guild)
    @vocal.command(name="skip")
    async def vocal_skip(self, ctx):
        """**Premium Only**
        Skip the current playing song"""
        await self.vocalcore.getvocal(str(ctx.message.guild.id)).skip()

    @commands.check(check_admin)
    @vocal.command(name="pause")
    async def vocal_pause(self, ctx):
        """**Premium Only**
        Pause the current playing song"""
        await self.vocalcore.getvocal(str(ctx.message.guild.id)).pause()

    @commands.check(check_admin)
    @vocal.command(name="resume")
    async def vocal_resume(self, ctx):
        """**Premium Only**
        Resume the current playing song"""
        await self.vocalcore.getvocal(str(ctx.message.guild.id)).resume()

    @commands.check(check_botmanager)
    @commands.cooldown(1, 60, commands.BucketType.default)
    @vocal.command(name="disconnectall", aliases=["forcedisconect"], hidden=True)
    async def vocal_disconnectall(self, ctx):
        await ctx.message.channel.send("This will disconnect the bot from all vocal connections, are you sure ?\nType `confirm` to perform this")
        chk = lambda m: m.author == ctx.message.author and m.channel == ctx.message.channel and m.content.lower() == 'confirm'
        try: answer = await self.bot.wait_for('message', check=chk, timeout=60)
        except asyncio.TimeoutError: answer = None
        if answer is None:
            await ctx.message.channel.send("your request has timeout")
        else:
            await self.vocalcore.interupt(ctx)
