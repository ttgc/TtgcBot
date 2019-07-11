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
import os
from random import choice
from src.tools.Translator import *

class NSFW(commands.Cog):
    def __init__(self,bot,logger):
        self.bot = bot
        self.logger = logger

    @commands.cooldown(5,30,commands.BucketType.channel)
    @commands.cooldown(1,5,commands.BucketType.user)
    @commands.is_nsfw()
    @commands.command()
    async def nsfwjoke(self,ctx):
        """**NSFW channel required**
        Display a NSFW joke (only in french currently)"""
        with open("Jokes/nsfw-fr.txt",encoding="utf-8") as f:
            await ctx.message.channel.send(choice(f.readlines()).replace("\\n","\n"))

    @commands.cooldown(5,30,commands.BucketType.channel)
    @commands.cooldown(3,5,commands.BucketType.user)
    @commands.is_nsfw()
    @commands.command()
    async def hentai(self,ctx):
        """**NSFW channel required**
        Display a random hentai pic :smirk:"""
        with open("Hentai/{}".format(choice(os.listdir("Hentai"))),"rb") as f:
            await ctx.message.channel.send(file=discord.File(f))

    @commands.cooldown(1,30,commands.BucketType.channel)
    @commands.is_nsfw()
    @commands.command()
    async def rule34(self,ctx):
        """**NSFW channel required**
        Do you really need some further explanations ?"""
        await ctx.message.channel.send("Rule 34 : *If it exists, there is porn on it*\nhttps://rule34.paheal.net/")
