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
        """**RP/JDR channel only**
        Display the worldmap of Terae (alpha dimension)"""
        self.logger.log(logging.DEBUG+1,"worldmap requested by %d in channel %d on server %d",ctx.message.author.id,ctx.message.channel.id,ctx.message.guild.id)
        with open("pictures/mapmonde.png","rb") as f:
            await ctx.message.channel.send(file=discord.File(f))

    @commands.check(check_chanmj)
    @commands.cooldown(1,60,commands.BucketType.channel)
    @map.command(name="show")
    async def map_show(self,ctx,width: int, height: int, depth: typing.Optional[int] = 0):
        """**GM/MJ only**
        Display your game battle map"""
        data = GenericCommandParameters(ctx)
        mp = Map(width,height,data.jdr.server,data.jdr.channel)
        self.logger.log(logging.DEBUG+1,"battlemap requested in channel %d on server %d",ctx.message.channel.id,ctx.message.guild.id)
        await mp.send(ctx,depth)

    @commands.check(check_chanmj)
    @commands.cooldown(1,30,commands.BucketType.channel)
    @map.command(name="clear",aliases=["reset","clr"])
    async def map_clear(self,ctx):
        """**GM/MJ only**
        Clear all tokens and effects on your game battle map"""
        data = GenericCommandParameters(ctx)
        Map.clear(data.jdr.server,data.jdr.channel)
        self.logger.log(logging.DEBUG+1,"map clear requested in channel %d on server %d",ctx.message.channel.id,ctx.message.guild.id)
        await ctx.message.channel.send(data.lang["mapreset"])

    @commands.check(check_chanmj)
    @map.group(name="token",invoke_without_command=False,aliases=["tk"])
    async def map_token(self,ctx): pass

    @map_token.command(name="add",aliases=["+"])
    async def map_token_add(self,ctx,tkname):
        """**GM/MJ only**
        Add a token on your game battle map"""
        data = GenericCommandParameters(ctx)
        tk = Token(tkname,data.jdr.server,data.jdr.channel)
        tk.save()
        self.logger.log(logging.DEBUG+1,"token %s registered in channel %d on server %d",tkname,ctx.message.channel.id,ctx.message.guild.id)
        await ctx.message.channel.send(data.lang["tokenadd"].format(tk.name))

    @map_token.command(name="remove",aliases=["rm","-","delete","del"])
    async def map_token_remove(self,ctx,tk: MapTokenConverter):
        """**GM/MJ only**
        Remove a token and all its effects associated from your game battle map"""
        if tk is not None:
            data = GenericCommandParameters(ctx)
            tk.remove()
            self.logger.log(logging.DEBUG+1,"token %s removed in channel %d on server %d",tk.name,ctx.message.channel.id,ctx.message.guild.id)
            await ctx.message.channel.send(data.lang["tokenrm"].format(tk.name))

    @map_token.command(name="move",aliases=["mv"])
    async def map_token_move(self,ctx,tk: MapTokenConverter, dx: int, dy: int, dz: typing.Optional[int] = 0):
        """**GM/MJ only**
        Move a token in the given direction"""
        data = GenericCommandParameters(ctx)
        if tk is not None:
            tk.move(dx,dy,dz)
            self.logger.log(logging.DEBUG+1,"token %s moved into direction (%d,%d,%d) in channel %d on server %d",tk.name,dx,dy,dz,ctx.message.channel.id,ctx.message.guild.id)
            await ctx.message.channel.send(data.lang["tokenmove"].format(tk.name,tk.x,tk.y,tk.z))

    @commands.check(check_chanmj)
    @map.group(name="effect",invoke_without_command=False)
    async def map_effect(self,ctx): pass

    @map_effect.command(name="add",aliases=["+"])
    async def map_effect_add(self,ctx,tk: MapTokenConverter, dx: int, dy: int, dz: int, shape: ShapeConverter,*,params: MapEffectParameterConverter):
        """**GM/MJ only**
        Register an area of effect for a given token. shape must be one of the following : `circle`,`sphere`,`line`,`rect`,`cube`,`conic`.
        Each of theese shape have their own parameters, some of them have to be given for the generation.
        List of parameters avalaible :
        ```
        circle : <r>
        sphere : <r>
        line : <length> [<orientation (default=0)> <height (default=1)> <thickness (default=0)>]
            orientation -> the value in degrees (following counter-clockwise rotation), can only be one of the following : 0, 90, 180 or 270
        rect : <rx> <ry>
        cube : <rx> <ry> <rz>
        conic : <lengths> [orientation (default=0)]
            lengths -> list of lengths separated with '-' symbol, the first value is the closest line from the origin and the last the farthest line from the origin (example : 1-3-5). DO NOT USE SPACE BETWEEN LENGTHS VALUES.
            orientation -> the value in degrees (following counter-clockwise rotation), can only be one of the following : 0, 90, 180 or 270
        ```"""
        data = GenericCommandParameters(ctx)
        if tk is not None:
            try: tk.spawnAreaEffect(dx,dy,dz,shape,params)
            except:
                await ctx.message.channel.send(data.lang["effect_parse_error"])
                return
            tk.registerEffect(dx,dy,dz,shape,params)
            self.logger.log(logging.DEBUG+1,"token effect (%s) registered for token %s at relative position (%d,%d,%d) in channel %d on server %d",shape.name,tk.name,dx,dy,dz,ctx.message.channel.id,ctx.message.guild.id)
            await ctx.message.channel.send(data.lang["effect_register"].format(tk.name))

    @commands.cooldown(3,5,commands.BucketType.channel)
    @map_effect.command(name="clear",aliases=["reset","clr"])
    async def map_effect_clear(self,ctx,tk: MapTokenConverter):
        """**GM/MJ only**
        Clear all effects from the given token"""
        data = GenericCommandParameters(ctx)
        if tk is not None:
            tk.cleareffect()
            self.logger.log(logging.DEBUG+1,"token effect clear requested for token %s in channel %d on server %d",tk.name,ctx.message.channel.id,ctx.message.guild.id)
            await ctx.message.channel.send(data.lang["token_clear"].format(tk.name))
