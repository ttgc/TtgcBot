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
import json
from discord.ext import commands
from core.commandparameters import GenericCommandParameters
from utils.decorators import deprecated

class CharacterConverter(commands.Converter):
    async def convert(self, ctx, arg):
        data = await GenericCommandParameters.get_from_context(ctx)
        jdr = await data.jdr
        return jdr.get_character(arg)

@deprecated("Old converter using DBManager")
class RaceConverter(commands.Converter):
    async def convert(self, ctx, arg):
        return retrieveRaceID(arg.replace("_"," ")) # noqa

@deprecated("Unused converter that might get removed at some point")
class JSONConverter(commands.Converter):
    async def convert(self, ctx, arg):
        return json.loads(arg) # noqa

@deprecated("Old converter using DBManager")
class SymbiontConverter(commands.Converter):
    async def convert(self, ctx, arg):
        return retrieveSymbiontID(arg.replace("_"," ")) # noqa

@deprecated("Old converter using DBManager")
class SkillConverter(commands.Converter):
    async def convert(self, ctx, arg):
        if arg.isdecimal():
            return [Skill(int(arg))] # noqa
        return Skill.skillsearch(arg.replace("_"," ")) # noqa

@deprecated("Old unused converter that might get removed at some point")
class OperatorConverter(commands.Converter):
    async def convert(self, ctx, arg):
        if arg not in ["+", "-"]:
            raise commands.BadArgument("Operator conversion error ! Not a valid operator")
        return arg

@deprecated("Old unused converter that might get removed at some point")
class MapTokenConverter(commands.Converter):
    async def convert(self, ctx, arg):
        data = GenericCommandParameters.get_from_context(ctx)
        try: tk = Token.load(arg,data.jdr.server,data.jdr.channel) # noqa
        except: # noqa
            await ctx.message.channel.send(data.lang["token_notexist"].format(arg)) # noqa
            return None
        return tk # noqa

@deprecated("Old map feature converter that will be removed at some point")
class ShapeConverter(commands.Converter):
    async def convert(self, ctx, arg):
        if arg.lower() == "circle": return Shape.CIRCLE # noqa
        if arg.lower() == "sphere": return Shape.SPHERE # noqa
        if arg.lower() == "line": return Shape.LINE # noqa
        if arg.lower() == "rect": return Shape.RECT # noqa
        if arg.lower() == "cube": return Shape.CUBE # noqa
        if arg.lower() == "conic": return Shape.CONIC # noqa
        raise commands.BadArgument("Shape conversion error ! Not a valid shape")

@deprecated("Old map feature converter that will be removed at some point")
class MapEffectParameterConverter(commands.Converter):
    async def convert(self, ctx, arg):
        args = arg.split(" ") # noqa
        while "" in args: args.remove("") # noqa
        data = {} # noqa
        for i in args: # noqa
            tag,value = i.split("=")
            if tag.lower() == "lengths": # noqa
                value = value.split("-") # noqa
                for i in range(len(value)): # noqa
                    value[i] = int(value[i]) # noqa
                    if value[i]%2 == 0: # noqa
                        raise commands.BadArgument("Shape parameter lengths invalid ! Should not be divisible by 2") # noqa
            elif tag.lower() == "orientation": # noqa
                directions = {"right":0,"left":180,"up":90,"down":270} # noqa
                if value.lower() in directions: # noqa
                    value = directions[value] # noqa
                else: # noqa
                    value = int(value) # noqa
                    if value not in [0,90,180,270]: # noqa
                        raise commands.BadArgument("Shape parameter orientation invalid ! Should be 0, 90, 180 or 270") # noqa
            else: # noqa
                value = int(value) # noqa
            data[tag] = value # noqa
        return data # noqa

@deprecated("Old converter using DBManager")
class AffiliationConverter(commands.Converter):
    async def convert(self, ctx, arg):
        if arg.lower() == "none": return None
        if not organizationExists(arg): # noqa
            raise commands.BadArgument("Unexisting organization provided")
        return arg

@deprecated("Old converter using DBManager")
class BattleEntityConverter(commands.Converter):
    async def convert(self, ctx, arg):
        if re.match(r"\w+:\d\d?", arg):
            tag, value = arg.split(":")
            return tag, int(value)
        raise commands.BadArgument("Invalid Battle Entity provided, cannot convert")

@deprecated("Old unused converter that might get removed at some point")
class DiceConverter(commands.Converter):
    async def convert(self, ctx, arg):
        match = re.search(r"\d+", arg)
        if match is not None:
            try: return DiceType(int(match.group(0))) # noqa
            except: # noqa
                raise commands.BadArgument("Unable to convert value {} into a dice type".format(arg))
        raise commands.BadArgument("Invalid Dice Type provided, cannot convert")
