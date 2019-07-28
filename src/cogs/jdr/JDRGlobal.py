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
from src.tools.Character import *
from src.utils.converters import *
import typing

class JDRGlobal(commands.Cog, name="Global (RP/JDR)"):
    def __init__(self,bot,logger):
        self.bot = bot
        self.logger = logger

    @commands.check(check_jdrchannel)
    @commands.group(name="global",invoke_without_command=False)
    async def global_(self,ctx): pass

    @commands.check(check_chanmj)
    @global_.command(name="damage",aliases=["dmg"])
    async def global_damage(self,ctx,chars: commands.Greedy[CharacterConverter],val: int):
        """**GM/MJ only**
        Inflict damages to the specified characters or to everyone if not specified"""
        data = GenericCommandParameters(ctx)
        if len(chars) == 0:
            chars = data.charbase
        val = abs(val)
        embd = discord.Embed(title=data.lang["global_damage"],description=data.lang["damage_taken"]+" "+str(val),colour=discord.Color(int('ff0000',16)))
        embd.set_footer(text="The Tale of Great Cosmos")
        embd.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.avatar_url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        deads = 0
        dead_ls = ""
        for i in chars:
            if i.dead: continue
            i = i.charset('pv',-val)
            embd.add_field(name=i.name,value=str(i.PV)+" (-"+str(val)+")",inline=True)
            if not i.check_life():
                deads += 1
                dead_ls += "{}\n".format(i.name)
        if deads > 0:
            embd.add_field(name=data.lang["dead_players"],value=dead_ls,inline=False)
        self.logger.log(logging.DEBUG+1,"globaldmg to %s in channel %d of server %d",str(chars),ctx.message.channel.id,ctx.message.guild.id)
        await ctx.message.channel.send(embed=embd)

    @commands.check(check_chanmj)
    @global_.command(name="heal")
    async def global_heal(self,ctx,chars: commands.Greedy[CharacterConverter],val: int):
        """**GM/MJ only**
        Heal the specified characters or everyone if not specified"""
        data = GenericCommandParameters(ctx)
        if len(chars) == 0:
            chars = data.charbase
        val = abs(val)
        embd = discord.Embed(title=data.lang["global_heal"],description=data.lang["heal_amount"]+" "+str(val),colour=discord.Color(int('00ff00',16)))
        embd.set_footer(text="The Tale of Great Cosmos")
        embd.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.avatar_url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        for i in chars:
            if i.dead: continue
            trueval = val
            if i.PV+val > i.PVmax:
                trueval = i.PVmax-i.PV
            i = i.charset('pv',trueval)
            embd.add_field(name=i.name,value=str(i.PV)+" (+"+str(trueval)+")",inline=True)
        self.logger.log(logging.DEBUG+1,"globalheal to %s in channel %d of server %d",str(chars),ctx.message.channel.id,ctx.message.guild.id)
        await ctx.message.channel.send(embed=embd)

    @commands.check(check_chanmj)
    @global_.command(name="getpm",aliases=["getmp"])
    async def global_getpm(self,ctx,chars: commands.Greedy[CharacterConverter],val: int):
        """**GM/MJ only**
        Give to or take MP/PM from the specified characters or everyone if not specified.
        The command follow the same rules as for `character getpm` command."""
        data = GenericCommandParameters(ctx)
        if len(chars) == 0:
            chars = data.charbase
        embd = discord.Embed(title=data.lang["global_pm"],description=data.lang["pm_earn"].format(str(val)),colour=discord.Color(int('0000ff',16)))
        embd.set_footer(text="The Tale of Great Cosmos")
        embd.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.avatar_url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        for i in chars:
            if i.dead: continue
            trueval = val
            if i.PM+val > i.PMmax:
                trueval = i.PMmax-i.PM
            if i.PM+trueval < 0:
                trueval = -i.PM
            i = i.charset('pm',trueval)
            embd.add_field(name=i.name,value="{} ({}{})".format(i.PM,("+" if trueval >= 0 else "-"),abs(trueval)),inline=True)
        self.logger.log(logging.DEBUG+1,"globalgetpm to %s in channel %d of server %d",str(chars),ctx.message.channel.id,ctx.message.guild.id)
        await ctx.message.channel.send(embed=embd)

    @commands.cooldown(1,30,commands.BucketType.channel)
    @global_.command(name="stat")
    async def global_stat(self,ctx):
        """**RP/JDR channel only**
        Show dice related statistic - such as fails, success, critic, etc. - of every characters"""
        data = GenericCommandParameters(ctx)
        ls = [0,0,0,0,0,0,0]
        for i in data.charbase:
            for k in range(len(ls)): ls[k] += i.stat[k]
        embd = discord.Embed(title=data.lang["stat"],description=data.lang["stat_all"],colour=discord.Color(randint(0,int('ffffff',16))))
        embd.set_footer(text="The Tale of Great Cosmos")
        embd.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.avatar_url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        embd.add_field(name=data.lang["dice_rolled"],value=str(ls[0]),inline=True)
        embd.add_field(name=data.lang["super_critic_success"],value=str(ls[1]),inline=True)
        embd.add_field(name=data.lang["critic_success"],value=str(ls[2]),inline=True)
        embd.add_field(name=data.lang["success"],value=str(ls[3]),inline=True)
        embd.add_field(name=data.lang["fail"],value=str(ls[4]),inline=True)
        embd.add_field(name=data.lang["critic_fail"],value=str(ls[5]),inline=True)
        embd.add_field(name=data.lang["super_critic_fail"],value=str(ls[6]),inline=True)
        self.logger.log(logging.DEBUG+1,"globalstat in channel %d of server %d",ctx.message.channel.id,ctx.message.guild.id)
        await ctx.message.channel.send(embed=embd)

    @commands.check(check_chanmj)
    @commands.cooldown(2,30,commands.BucketType.channel)
    @global_.command(name="fight",aliases=["battle"])
    async def global_fight(self,ctx,chars: commands.Greedy[CharacterConverter], other: commands.Greedy[BattleEntityConverter]):
        """**GM/MJ only**
        Start a new fight's round. Use agility stat to determine order of actions.
        If chars is empty, then all characters will be selected.
        Other is a list of tag:agility values for other source of actions, such as NPC/PNJ.
        Format for other items follow the rule : `tag:agility` (for example : `boss:70`)
        In case of equality between two entities nothing specific will be done and an arbitrary order will be given to each of them"""
        data = GenericCommandParameters(ctx)
        if len(chars) == 0:
            chars = data.charbase
        entities = []
        for i in chars:
            entities.append([i.name, i.agilite])
        for i in other:
            entities.append(list(i))
        entities.sort(key=lambda entity: entity[1])
        embd = discord.Embed(title=data.lang["fight_round"],colour=discord.Color(int('ff0000',16)))
        embd.set_footer(text="The Tale of Great Cosmos")
        embd.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.avatar_url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        for i in range(len(entities)):
            embd.add_field(name="#{} - {}".format(i+1, entities[i][0]),value=str(entities[i][1]),inline=False)
        self.logger.log(logging.DEBUG+1,"globalfight in channel %d of server %d",ctx.message.channel.id,ctx.message.guild.id)
        await ctx.message.channel.send(embed=embd)
