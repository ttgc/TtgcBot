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

from src.utils.checks import *
from discord.ext import commands
import logging,asyncio
from src.utils.converters import *
import discord
import typing
from src.utils.decorators import deprecated

@deprecated("Old 2.0 cog")
class MJ(commands.Cog):
    def __init__(self,bot,logger):
        self.bot = bot
        self.logger = logger
        self.charcog = self.bot.get_cog("Characters")
        self.invcog = self.bot.get_cog("Inventory")
        self.petcog = self.bot.get_cog("Pets")

    @commands.check(check_chanmj)
    @commands.group(invoke_without_command=False)
    async def mj(self,ctx): pass

    @mj.command(name="info",aliases=["charinfo","characterinfo"])
    async def mj_info(self,ctx,char: CharacterConverter):
        """**GM/MJ only**
        GM version of character info command"""
        data = await GenericCommandParameters(ctx)
        self.logger.log(logging.DEBUG+1,"/mjcharinfo (%s) in channel %d of server %d",char.key,ctx.message.channel.id,ctx.message.guild.id)
        await self.charcog._charinfo(ctx,data,char)

    @mj.command(name="inventory",aliases=["inv"])
    async def mj_inventory(self,ctx,char: CharacterConverter):
        data = await GenericCommandParameters(ctx)
        await self.invcog._inventory(ctx,data,char)

    @mj.command(name="switchmod",aliases=["switchmode"])
    async def mj_switchmod(self,ctx,char: CharacterConverter):
        """**GM/MJ only**
        GM version of character switchmod command"""
        data = await GenericCommandParameters(ctx)
        self.logger.log(logging.DEBUG+1,"/mjswitchmod (%s) in channel %d of server %d",char.key,ctx.message.channel.id,ctx.message.guild.id)
        await self.charcog._switchmod(ctx,data,char)

    @mj.command(name="pay")
    async def mj_pay(self,ctx,char: CharacterConverter,amount: int):
        """**GM/MJ only**
        GM version of character pay command"""
        data = await GenericCommandParameters(ctx)
        self.logger.log(logging.DEBUG+1,"/mjpay (%s) in channel %d of server %d",char.key,ctx.message.channel.id,ctx.message.guild.id)
        await self.charcog._pay(ctx,data,char,amount)

    @mj.command(name="setmental")
    async def mj_setmental(self,ctx,char: CharacterConverter,op: typing.Optional[OperatorConverter],amount: int):
        """**GM/MJ only**
        GM version of character setmental command"""
        data = await GenericCommandParameters(ctx)
        self.logger.log(logging.DEBUG+1,"/mjsetmental (%s) in channel %d of server %d",char.key,ctx.message.channel.id,ctx.message.guild.id)
        await self.charcog._setmental(ctx,data,char,op,amount)

    @mj.command(name="roll",aliases=["r"])
    async def mj_roll(self,ctx,char: CharacterConverter,stat,operator: typing.Optional[OperatorConverter] = "+",*,expression=None):
        """**GM/MJ only**
        GM version of character roll command"""
        data = await GenericCommandParameters(ctx)
        self.logger.log(logging.DEBUG+1,"/mjroll (%s) in channel %d of server %d",char.key,ctx.message.channel.id,ctx.message.guild.id)
        await self.charcog._charroll(ctx,data,char,stat,operator,expression)

    @mj.group(name="pilot",aliases=["p", "piloting", "pilotage"],invoke_without_command=False)
    async def mj_pilot(self,ctx): pass

    @mj_pilot.command(name="astral",aliases=["interplanetaire", "a"])
    async def mj_pilot_astral(self, ctx, dice: DiceConverter, chars: commands.Greedy[CharacterConverter], operator: typing.Optional[OperatorConverter] = "+", *, expression=None):
        """**GM/MJ only**
        GM version of character pilot astral command"""
        data = await GenericCommandParameters(ctx)
        self.logger.log(logging.DEBUG+1,"/mjpilot astral (%s) in channel %d of server %d",char.key,ctx.message.channel.id,ctx.message.guild.id)
        if len(chars) == 0:
            raise commands.MissingRequiredArgument(chars)
        await self.charcog._charpilot(ctx, PiloteRollType.ASTRAL, data, dice, chars, operator, expression)

    @mj_pilot.command(name="planet", aliases=["planetaire", "p"])
    async def mj_pilot_planet(self, ctx, dice: DiceConverter, chars: commands.Greedy[CharacterConverter], operator: typing.Optional[OperatorConverter] = "+", *, expression=None):
        """**GM/MJ only**
        GM version of character pilot planet command"""
        data = await GenericCommandParameters(ctx)
        self.logger.log(logging.DEBUG+1,"/mjpilot planet (%s) in channel %d of server %d",char.key,ctx.message.channel.id,ctx.message.guild.id)
        if len(chars) == 0:
            raise commands.MissingRequiredArgument(chars)
        await self.charcog._charpilot(ctx, PiloteRollType.PLANET, data, dice, chars, operator, expression)

    @mj.command(name="transfer")
    async def mj_transfer(self,ctx,newMJ: discord.Member):
        """**GM/MJ only**
        Transfer ownership of a RP/JDR to someone else (this member needs the GM/MJ role)"""
        data = await GenericCommandParameters(ctx)
        destisMJ = discord.utils.get(ctx.message.guild.roles,id=int(data.srv.mjrole)) in newMJ.roles
        if not destisMJ:
            await ctx.message.channel.send(data.lang["mjtransfer_notmj"])
        else:
            await ctx.message.channel.send(data.lang["mjtransfer_step1"].format(ctx.message.channel.mention,newMJ.mention))
            chk = lambda m: m.author == ctx.message.author and m.channel == ctx.message.channel and m.content.lower() == 'confirm'
            try: answer = await self.bot.wait_for('message',check=chk,timeout=60)
            except asyncio.TimeoutError: answer = None
            if answer is None:
                await ctx.message.channel.send(data.lang["timeout"])
            else:
                await ctx.message.channel.send(data.lang["mjtransfer_step2"].format(newMJ.mention,ctx.message.author.mention,ctx.message.channel.mention))
                chk = lambda m: m.author == newMJ and m.channel == ctx.message.channel and m.content.lower() == 'accept'
                try: answer = await self.bot.wait_for('message',check=chk,timeout=60)
                except asyncio.TimeoutError: answer = None
                if answer is None:
                    await ctx.message.channel.send(data.lang["mjtransfer_timeout"].format(newMJ))
                else:
                    data.jdr.MJtransfer(str(newMJ.id))
                    self.logger.log(logging.DEBUG+1,"/mjtranfer (%d -> %d) in channel %d of server %d",ctx.message.author.id,newMJ.id,ctx.message.channel.id,ctx.message.guild.id)
                    await ctx.message.channel.send(data.lang["mjtransfer"].format(newMJ))

    @mj.group(name="pet",invoke_without_command=False)
    async def mj_pet(self,ctx): pass

    @mj_pet.command(name="roll",aliases=["r"])
    async def mj_pet_roll(self,ctx,char: CharacterConverter,petkey,stat,operator: typing.Optional[OperatorConverter] = "+",*,expression=None):
        """**GM/MJ only**
        GM version of pet roll command"""
        data = await GenericCommandParameters(ctx)
        self.logger.log(logging.DEBUG+1,"/mjpetroll (%s / %s) in channel %d of server %d",char.key,petkey,ctx.message.channel.id,ctx.message.guild.id)
        await self.petcog._petroll(ctx,data,char,petkey,stat,operator,expression)

    @mj_pet.command(name="switchmod",aliases=["switchmode"])
    async def mj_pet_switchmod(self,ctx,char: CharacterConverter,petkey):
        """**GM/MJ only**
        GM version of pet switchmod command"""
        data = await GenericCommandParameters(ctx)
        self.logger.log(logging.DEBUG+1,"/mjpetswitchmod (%s / %s) in channel %d of server %d",char.key,petkey,ctx.message.channel.id,ctx.message.guild.id)
        await self.petcog._switchmod(ctx,data,char,petkey)

    @mj_pet.command(name="info")
    async def mj_pet_info(self,ctx,char: CharacterConverter,petkey):
        """**GM/MJ only**
        GM version of pet info command"""
        data = await GenericCommandParameters(ctx)
        self.logger.log(logging.DEBUG+1,"/mjpetinfo (%s / %s) in channel %d of server %d",char.key,petkey,ctx.message.channel.id,ctx.message.guild.id)
        await self.petcog._petinfo(ctx,data,char,petkey)
