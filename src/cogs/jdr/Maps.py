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
from src.tools.mapmanager import *
from src.utils.converters import *
import typing

class Maps(commands.Cog):
    def __init__(self,bot,logger):
        self.bot = bot
        self.logger = logger

    @commands.check(check_jdrchannel)
    @commands.cooldown(1,60,commands.BucketType.channel)
    @commands.group(invoke_without_command=True)
    async def map(self,ctx):
        with open("pictures/mapmonde.png") as f:
            await ctx.message.channel.send(file=discord.File(f))

    @commands.check(check_chanmj)
    @commands.cooldown(1,60,commands.BucketType.channel)
    @map.command(name="show")
    async def map_show(self,ctx,width: int, height: int, depth: typing.Optional[int] = 0):
        data = GenericCommandParameters(ctx)
        mp = Map(width,height,data.jdr.server,data.jdr.channel)
        await mp.send(ctx,depth)

    @commands.check(check_chanmj)
    @commands.cooldown(1,30,commands.BucketType.channel)
    @map.command(name="clear",aliases=["reset","clr"])
    async def map_clear(self,ctx):
        data = GenericCommandParameters(ctx)
        Map.clear(data.jdr.server,data.jdr.channel)
        await ctx.message.channel.send(data.lang["mapreset"])

    @commands.check(check_chanmj)
    @map.group(name="token",invoke_without_command=False,aliases=["tk"])
    async def map_token(self,ctx): pass

    @map_token.command(name="add",aliases=["+"])
    async def map_token_add(self,ctx,tkname):
        data = GenericCommandParameters(ctx)
        tk = Token(tkname,data.jdr.server,data.jdr.channel)
        tk.save()
        await ctx.message.channel.send(data.lang["tokenadd"].format(tk.name))

    @map_token.command(name="remove",aliases=["rm","-","delete","del"])
    async def map_token_remove(self,ctx,tk: MapTokenConverter):
        if tk is not None:
            data = GenericCommandParameters(ctx)
            tk.remove()
            await ctx.message.channel.send(data.lang["tokenrm"].format(tk.name))

    @map_token.command(name="move",aliases=["mv"])
    async def map_token_move(self,ctx,tk: MapTokenConverter, dx: int, dy: int, dz: typing.Optional[int] = 0):
        if tk is not None:
            tk.move(dx,dy,dz)
            await ctx.message.channel.send(data.lang["tokenmove"].format(tk.name,tk.x,tk.y,tk.z))

    @commands.check(check_chanmj)
    @map.group(name="effect",invoke_without_command=False)
    async def map_effect(self,ctx): pass

    @map_effect.command(name="add",aliases=["+"])
    async def map_effect_add(self,ctx,tk: MapTokenConverter, dx: int, dy: int, dz: int, shape: ShapeConverter,*,params: MapEffectParameterConverter):
        if tk is not None:
            try: tk.spawnAreaEffect(dx,dy,dz,shape,params)
            except:
                await ctx.message.channel.send(data.lang["effect_parse_error"])
                return
            tk.registerEffect(dx,dy,dz,shape,params)
            await ctx.message.channel.send(data.lang["effect_register"].format(tk.name))

    @commands.cooldown(3,5,commands.BucketType.channel)
    @map_effect.command(name="clear",aliases=["reset","clr"])
    async def map_effect_clear(self,ctx,tk: MapTokenConverter):
        if tk is not None:
            tk.cleareffect()
            await ctx.message.channel.send(data.lang["token_clear"].format(tk.name))
