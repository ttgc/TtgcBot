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
from src.tools.Translator import *
from src.tools.CharacterUtils import *
from src.utils.converters import *
import typing

class SkillCog(commands.Cog, name="Skills"):
    def __init__(self,bot,logger):
        self.bot = bot
        self.logger = logger

    @commands.check(check_haschar)
    @commands.group(invoke_without_command=True,aliases=['sk'])
    async def skill(self,ctx):
        """**Player only**
        Display all natural skills inherited by your character"""
        data = GenericCommandParameters(ctx)
        embd = discord.Embed(title=data.char.name,description=data.lang["sklist"],colour=discord.Color(int('5B005B',16)))
        embd.set_footer(text="The Tale of Great Cosmos")
        embd.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.avatar_url)
        embd.set_thumbnail(url="https://www.thetaleofgreatcosmos.fr/wp-content/uploads/2019/11/TTGC_Text.png")
        for i in data.char.skills:
            if not organizationExists(i.origine) or not isOrganizationHidden(i.origine):
                embd.add_field(name="{}#{} ({})".format(i.ID,i.name,i.origine),value=i.description.replace("\\n","\n"),inline=True)
        self.logger.log(logging.DEBUG+1,"skill list requested for character %s in channel %d on server %d",data.char.key,ctx.message.channel.id,ctx.message.guild.id)
        await ctx.message.channel.send(embed=embd)


    @commands.check(check_jdrchannel)
    @skill.command(name="info")
    async def skill_info(self,ctx,search: commands.Greedy[SkillConverter]):
        """**RP/JDR channel only**
        Search for one or many natural skills, retrieving all information and ID"""
        data = GenericCommandParameters(ctx)
        embd = discord.Embed(title=data.lang["skillsearch"],colour=discord.Color(int('5B005B',16)))
        embd.set_footer(text="The Tale of Great Cosmos")
        embd.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.avatar_url)
        embd.set_thumbnail(url="https://www.thetaleofgreatcosmos.fr/wp-content/uploads/2019/11/TTGC_Text.png")
        for sklist in search:
            for i in sklist:
                embd.add_field(name="{}#{} ({})\n[{}]".format(i.ID,i.name,i.origine,i.extension),value=i.description.replace("\\n","\n"),inline=True)
        self.logger.log(logging.DEBUG+1,"skill search by %d in channel %d on server %d",ctx.message.author.id,ctx.message.channel.id,ctx.message.guild.id)
        await ctx.message.channel.send(embed=embd)

    @commands.check(check_chanmj)
    @skill.command(name="assign")
    async def skill_assign(self,ctx,char: CharacterConverter,*, skill: SkillConverter):
        """**GM/MJ only**
        Assign a natural skill to a given character"""
        data = GenericCommandParameters(ctx)
        if len(skill) == 0:
            await ctx.message.channel.send(data.lang["skill_notfound"])
        elif len(skill) > 1:
            embd = discord.Embed(title="Skill Assign",description=data.lang["skill_assign_choice"],colour=discord.Color(int('5B005B',16)))
            embd.set_footer(text="The Tale of Great Cosmos")
            embd.set_author(name=message.author.name,icon_url=message.author.avatar_url)
            embd.set_thumbnail(url="https://www.thetaleofgreatcosmos.fr/wp-content/uploads/2019/11/TTGC_Text.png")
            for i in skill:
                embd.add_field(name="{}#{} ({})\n[{}]".format(i.ID,i.name,i.origine,i.extension),value=i.description.replace("\\n","\n"),inline=True)
            botmsg = await ctx.message.channel.send(embed=embd)
            chk = lambda m: m.author == ctx.message.author and m.channel == ctx.message.channel and m.content.isdecimal()
            try: answer = await self.bot.wait_for('message',check=chk,timeout=60)
            except asyncio.TimeoutError: answer = None
            botmsg.delete(delay=0.5)
            if answer is None:
                await ctx.message.channel.send(data.lang["timeout"])
            else:
                val = int(answer.content)
                answer.delete()
                for i in skill:
                    if i.ID == val:
                        char.assign_skill(i)
                        self.logger.log(logging.DEBUG+1,"assign skill %d to %s in channel %d on server %d",i.ID,char.key,ctx.message.channel.id,ctx.message.guild.id)
                        await ctx.message.channel.send(data.lang["assign_skill"].format(i.name,char.name))
                        return
                await ctx.message.channel.send(data.lang["skill_invalidid"])
        else:
            char.assign_skill(skill[0])
            self.logger.log(logging.DEBUG+1,"assign skill %d to %s in channel %d on server %d",skill[0].ID,char.key,ctx.message.channel.id,ctx.message.guild.id)
            await ctx.message.channel.send(data.lang["assign_skill"].format(skill[0].name,char.name))
