#!usr/bin/env python3
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

import re
import discord
import json
from discord.ext import commands
from models import Character
from core.commandparameters import GenericCommandParameters
from utils.decorators import deprecated

class CharacterConverter(commands.Converter):
    async def convert(self, ctx, arg):
        data = await GenericCommandParameters.get_from_context(ctx)
        jdr = await data.jdr
        return jdr.get_character(arg)

@deprecated("Old converter using DBManager")
class RaceConverter(commands.Converter):
    async def convert(self,ctx,arg):
        return retrieveRaceID(arg.replace("_"," "))

@deprecated("Unused converter that might get removed at some point")
class JSONConverter(commands.Converter):
    async def convert(self, ctx, arg):
        return json.loads(arg)

@deprecated("Old converter using DBManager")
class SymbiontConverter(commands.Converter):
    async def convert(self,ctx,arg):
        return retrieveSymbiontID(arg.replace("_"," "))

@deprecated("Old converter using DBManager")
class SkillConverter(commands.Converter):
    async def convert(self,ctx,arg):
        if arg.isdecimal():
            return [Skill(int(arg))]
        return Skill.skillsearch(arg.replace("_"," "))

@deprecated("Old unused converter that might get removed at some point")
class OperatorConverter(commands.Converter):
    async def convert(self,ctx,arg):
        if arg not in ["+","-"]:
            raise commands.BadArgument("Operator conversion error ! Not a valid operator")
        return arg

@deprecated("Old unused converter that might get removed at some point")
class MapTokenConverter(commands.Converter):
    async def convert(self,ctx,arg):
        data = await GenericCommandParameters(ctx)
        try: tk = Token.load(arg,data.jdr.server,data.jdr.channel)
        except:
            await ctx.message.channel.send(data.lang["token_notexist"].format(arg))
            return None
        return tk

@deprecated("Old map feature converter that will be removed at some point")
class ShapeConverter(commands.Converter):
    async def convert(self,ctx,arg):
        if arg.lower() == "circle": return Shape.CIRCLE
        if arg.lower() == "sphere": return Shape.SPHERE
        if arg.lower() == "line": return Shape.LINE
        if arg.lower() == "rect": return Shape.RECT
        if arg.lower() == "cube": return Shape.CUBE
        if arg.lower() == "conic": return Shape.CONIC
        raise commands.BadArgument("Shape conversion error ! Not a valid shape")

@deprecated("Old map feature converter that will be removed at some point")
class MapEffectParameterConverter(commands.Converter):
    async def convert(self,ctx,arg):
        args = arg.split(" ")
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

@deprecated("Old converter using DBManager")
class AffiliationConverter(commands.Converter):
    async def convert(self,ctx,arg):
        if arg.lower() == "none": return None
        if not organizationExists(arg):
            raise commands.BadArgument("Unexisting organization provided")
        return arg

@deprecated("Old converter using DBManager")
class BattleEntityConverter(commands.Converter):
    async def convert(self,ctx,arg):
        if re.match(r"\w+:\d\d?", arg):
            tag, value = arg.split(":")
            return tag, int(value)
        raise commands.BadArgument("Invalid Battle Entity provided, cannot convert")

@deprecated("Old unused converter that might get removed at some point")
class DiceConverter(commands.Converter):
    async def convert(self, ctx, arg):
        match = re.search(r"\d+", arg)
        if match is not None:
            try: return DiceType(int(match.group(0)))
            except:
                raise commands.BadArgument("Unable to convert value {} into a dice type".format(arg))
        raise commands.BadArgument("Invalid Dice Type provided, cannot convert")
