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
from src.Character import *
from src.CharacterUtils import *
from src.checks import GenericCommandParameters

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
            return Skill(int(arg))
        return Skill.skillsearch(arg)

class OperatorConverter(commands.Converter):
    async def convert(self,ctx,arg):
        if arg not in ["+","-"]:
            raise commands.BadArgument("Operator conversion error ! Not a valid operator")
        return arg

class ItemConverter(commands.Converter):
    async def convert(self,ctx,arg):
        return Item.find(arg)
