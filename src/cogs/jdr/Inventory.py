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
from discord.ext import commands
import logging,asyncio
import discord
from src.tools.Character import *
from src.tools.CharacterUtils import *
from src.utils.converters import *
import typing

class CharacterCog(commands.Cog, name="Characters"):
    def __init__(self,bot,logger):
        self.bot = bot
        self.logger = logger

    async def _inventory(self,ctx,data,char):
        embd = discord.Embed(title=char.name,description=data.lang["inv"].format(char.inventory.weight, char.inventory.maxweight),colour=discord.Color(int('5B005B',16)))
        embd.set_footer(text="The Tale of Great Cosmos")
        embd.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.avatar_url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        for item, qte in char.inventory.items.items():
            embd.add_field(name=item.name,value=data.lang["inv_item"].format(qte,item.weight),inline=True)
        self.logger.log(logging.DEBUG+1,"inventory list requested for character %s in channel %d on server %d",char.key,ctx.message.channel.id,ctx.message.guild.id)
        await ctx.message.channel.send(embed=embd)

    @commands.check(check_haschar)
    @commands.cooldown(1,10,commands.BucketType.user)
    @commands.group(invoke_without_command=True, aliases=["inv"])
    async def inventory(self,ctx):
        data = GenericCommandParameters(ctx)
        await self._inventory(ctx,data,data.char)

    @commands.check(check_chanmj)
    @commands.cooldown(6,10,commands.BucketType.user)
    @inventory.command(name="add", aliases=["+","append"])
    async def inventory_add(self,ctx,char: CharacterConverter,item,quantity: typing.Optional[int] = 1,weight: typing.Optional[float] = 1.0):
        data = GenericCommandParameters(ctx)
        if char.inventory.weight + (quantity*weight) > char.inventory.maxweight:
            await ctx.message.channel.send(data.lang["inv_full"])
        else:
            char.inventory.additem(Item(item, weight),quantity)
            self.logger.log(logging.DEBUG+1,"item %s added to character %s in channel %d on server %d",item,char.key,ctx.message.channel.id,ctx.message.guild.id)
            await ctx.message.channel.send(data.lang["inv_add"])

    @commands.check(check_chanmj)
    @commands.cooldown(6,10,commands.BucketType.user)
    @inventory.command(name="remove", aliases=["-","rm","delete","del"])
    async def inventory_remove(self,ctx,char: CharacterConverter,item,quantity: typing.Optional[int] = 1):
        data = GenericCommandParameters(ctx)
        itemobject = None
        for i in char.inventory.items.keys():
            if i.name == item:
                itemobject = i
                break
        if itemobject is None:
            await ctx.message.channel.send(data.lang["item_not_found"])
        else:
            char.inventory.rmitem(itemobject,quantity)
            self.logger.log(logging.DEBUG+1,"item %s removed from character %s in channel %d on server %d",item,char.key,ctx.message.channel.id,ctx.message.guild.id)
            await ctx.message.channel.send(data.lang["inv_rm"])
