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

import discord
from discord.ext import commands
from src.tools.Character import *
from src.tools.CharacterUtils import *
from src.utils.checks import GenericCommandParameters
from src.tools.mapmanager import *

class CharacterConverter(commands.Converter):
    async def convert(self,ctx,arg):
        data = GenericCommandParameters(ctx)
        return data.jdr.get_character(arg)

class RaceConverter(commands.Converter):
    async def convert(self,ctx,arg):
        return retrieveRaceID(arg.replace("_"," "))

class SkillConverter(commands.Converter):
    async def convert(self,ctx,arg):
        if arg.isdecimal():
            return [Skill(int(arg))]
        return Skill.skillsearch(arg.replace("_"," "))

class OperatorConverter(commands.Converter):
    async def convert(self,ctx,arg):
        if arg not in ["+","-"]:
            raise commands.BadArgument("Operator conversion error ! Not a valid operator")
        return arg

class ItemConverter(commands.Converter):
    async def convert(self,ctx,arg):
        return Item.find(arg)

class MapTokenConverter(commands.Converter):
    async def convert(self,ctx,arg):
        data = GenericCommandParameters(ctx)
        try: tk = Token.load(arg,data.jdr.server,data.jdr.channel)
        except:
            await ctx.message.channel.send(data.lang["token_notexist"].format(arg))
            return None
        return tk

class ShapeConverter(commands.Converter):
    async def convert(self,ctx,arg):
        if arg.lower() == "circle": return Shape.CIRCLE
        if arg.lower() == "sphere": return Shape.SPHERE
        if arg.lower() == "line": return Shape.LINE
        if arg.lower() == "rect": return Shape.RECT
        if arg.lower() == "cube": return Shape.CUBE
        if arg.lower() == "conic": return Shape.CONIC
        raise commands.BadArgument("Shape conversion error ! Not a valid shape")

class MapEffectParameterConverter(commands.Converter):
    async def convert(self,ctx,arg):
        ls = arg.split(" ")
        while "" in args: args.remove("")
        data = {}
        for i in args:
            tag,value = i.split("=")
            if tag.lower() == "lengths":
                value = value.split("-")
                for i in range(len(value)):
                    value[i] = int(value[i])
                    if value[i]%2 == 0:
                        raise commands.BadArgument("Shape parameter lengths invalid ! Should not be divisible by 2")
            elif tag.lower() == "orientation":
                directions = {"right":0,"left":180,"up":90,"down":270}
                if value.lower() in directions:
                    value = directions[value]
                else:
                    value = int(value)
                    if value not in [0,90,180,270]:
                        raise commands.BadArgument("Shape parameter orientation invalid ! Should be 0, 90, 180 or 270")
            else:
                value = int(value)
            data[tag] = value
        return data
