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
from discord.ext import commands
import logging
from src.discordConverters import *
import typing

class MJ(commands.Cog):
    def __init__(self,bot,logger):
        self.bot = bot
        self.logger = logger
        self.charcog = self.bot.get_cog("CharacterCog")
        # self.invcog = self.bot.get_cog("InventoryCog")
        # self.petcog = self.bot.get_cog("PetCog")

    @commands.check(check_chanmj)
    @commands.group(invoke_without_command=False)
    async def mj(self,ctx): pass

    @mj.command(name="info",aliases=["charinfo","characterinfo"])
    async def mj_info(self,ctx,char: CharacterConverter):
        data = GenericCommandParameters(ctx)
        await self.charcog.charinfo(ctx,data,char)

    # @mj.command(name="inventory",aliases=["inv"])
    # async def mj_inventory(self,ctx,char: CharacterConverter):
    #     pass

    @mj.command(name="switchmod",aliases=["switchmode"])
    async def mj_switchmod(self,ctx,char: CharacterConverter):
        data = GenericCommandParameters(ctx)
        await self.charcog.switchmod(ctx,data,char)

    @mj.command(name="pay")
    async def mj_pay(self,ctx,char: CharacterConverter,amount: int):
        data = GenericCommandParameters(ctx)
        await self.charcog.pay(ctx,data,char,val)

    @mj.command(name="setmental")
    async def mj_setmental(self,ctx,char: CharacterConverter,op: typing.Optional[OperatorConverter],amount: int):
        data = GenericCommandParameters(ctx)
        await self.charcog.setmental(ctx,data,char,op,val)

    @mj.command(name="roll",aliases=["r"])
    async def mj_roll(self,ctx,char,stat,operator: typing.Optional[OperatorConverter] = "+",*,expression=None):
        data = GenericCommandParameters(ctx)
        await self.charcog.charroll(ctx,data,char,stat,operator,expression)

    # @mj.group(name="pet",invoke_without_command=False)
    # async def mj_pet(self,ctx): pass
    #
    # @mj_pet.command(name="roll",aliases=["r"])
    # async def mj_pet_roll(self,ctx,...):
    #     pass
    #
    # @mj_pet.command(name="switchmod",aliases=["switchmode"])
    # async def mj_pet_switchmod(self,ctx,...):
    #     pass
    #
    # @mj_pet.command(name="info")
    # async def mj_pet_info(self,ctx,...):
    #     pass
