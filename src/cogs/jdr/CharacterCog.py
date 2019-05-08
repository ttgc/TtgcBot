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
from src.BotTools import *
from discord.ext import commands
import logging,asyncio
import discord
from src.Translator import *
from src.Character import *
from src.CharacterUtils import *
from src.discordConverters import *
from src.parsingdice import *
import typing

class CharacterCog(commands.Cog):
    def __init__(self,bot,logger):
        self.bot = bot
        self.logger = logger

    @commands.check(check_jdrchannel)
    @commands.group(invoke_without_command=False,aliases=['char'])
    async def character(self,ctx): pass

    @commands.check(check_chanmj)
    @character.command(name="create",aliases=["+"])
    async def character_create(self,ctx,race: RaceConverter,classeName,name):
        classe = retrieveClassID(race,classeName.replace("_"," "))
        data = GenericCommandParameters(ctx)
        if (race is None or classe is None):
            await ctx.message.channel.send(data.lang["unknown_class"])
        else:
            if name in data.charbase:
                await ctx.message.channel.send(data.lang["character_existing"])
            else:
                data.jdr.charcreate(name,classe)
                await ctx.message.channel.send(data.lang["charcreate"].format(name))

    @commands.check(check_chanmj)
    @commands.cooldown(1,5,commands.BucketType.channel)
    @character.command(name="delete",aliases=["del","-"])
    async def character_delete(self,ctx,name):
        data = GenericCommandParameters(ctx)
        await ctx.message.channel.send(data.lang["chardelete_confirm"].format(name))
        chk = lambda m: m.author == ctx.message.author and m.channel == ctx.message.channel and m.content.lower() == 'confirm'
        try: answer = await self.bot.wait_for('message',check=chk,timeout=60)
        except asyncio.TimeoutError: answer = None
        if answer is None:
            await ctx.message.channel.send(data.lang["timeout"])
        else:
            data.jdr.chardelete(name)
            await ctx.message.channel.send(data.lang["chardelete"])

    @commands.check(check_chanmj)
    @character.command(name="link",aliases=["assign"])
    async def character_link(self,ctx,character: CharacterConverter, player: discord.Member):
        data = GenericCommandParameters(ctx)
        character.link(str(player.id))
        await ctx.message.channel.send(data.lang["charlink"].format(character.name,player.mention))

    @commands.check(check_chanmj)
    @character.command(name="unlink",aliases=["unassign"])
    async def character_unlink(self,ctx,character: typing.Optional[CharacterConverter] = None):
        data = GenericCommandParameters(ctx)
        if character is None and data.char is not None:
            data.char.unlink()
            await ctx.message.channel.send(data.lang["charunlink"].format(data.char.name))
        elif character is not None:
            character.unlink()
            await ctx.message.channel.send(data.lang["charunlink"].format(character.name))

    @commands.check(check_haschar)
    @commands.cooldown(1,5,commands.BucketType.user)
    @character.command(name="select")
    async def character_select(self,ctx,key):
        data = GenericCommandParameters(ctx)
        for i in member_charbase:
            if i.key == key and i.linked == str(ctx.message.author.id):
                i.select()
                await ctx.message.channel.send(data.lang["charselect"].format(data.char.key,i.key))
                return
        await ctx.message.channel.send(data.lang["charnotexist"].format(key))

    @commands.check(check_haschar)
    @character.command(name="roll",aliases=["r"])
    async def character_roll(self,ctx,stat,operator: typing.Optional[OperatorConverter] = "+",*,expression=None):
        data = GenericCommandParameters(ctx)
        modifier = 0
        if expression is not None:
            modifier = ParseRoll(expression).resolv()
        if not data.char.dead:
            await data.char.roll(ctx.channel,data.lang,stat,modifier*((-1)**(operator=="-")))
        else:
            await ctx.message.channel.send(data.lang["is_dead"].format(data.char.name))

    @commands.check(check_chanmj)
    @character.command(name="set")
    async def character_set(self,ctx,key,char: CharacterConverter,*,value):
        data = GenericCommandParameters(ctx)
        if key.lower() == "name":
            char.setname(value)
            await ctx.message.channel.send(data.lang["charset"].format(data.lang["name"]))
        elif key.lower() == "pv":
            char = char.charset('pvmax',int(value))
            await ctx.message.channel.send(data.lang["charset"].format(data.lang["PV"]+" max"))
        elif key.lower() == "pm":
            char = char.charset('pmmax',int(value))
            await ctx.message.channel.send(data.lang["charset"].format(data.lang["PM"]+" max"))
        elif key.lower() in ["str","force","strength"]:
            char = char.charset('str',int(value))
            await ctx.message.channel.send(data.lang["charset"].format(data.lang["force"]))
        elif key.lower() in ["spr","esprit","spirit"]:
            char = char.charset('spr',int(value))
            await ctx.message.channel.send(data.lang["charset"].format(data.lang["esprit"]))
        elif key.lower() in ["cha","charisme","charisma"]:
            char = char.charset('cha',int(value))
            await ctx.message.channel.send(data.lang["charset"].format(data.lang["charisme"]))
        elif key.lower() in ["agi","agilite","agility","furtivite"]:
            char = char.charset('agi',int(value))
            await ctx.message.channel.send(data.lang["charset"].format(data.lang["agilite"]))
        elif key.lower() in ["lp","lightpt","lightpoint"]:
            if int(value) >= 0:
                char = char.charset('lp',int(value))
                await ctx.message.channel.send(data.lang["charset"].format("Light Points"))
        elif key.lower() in ["dp","darkpt","darkpoint"]:
            if int(value) >= 0:
                char = char.charset('dp',int(value))
                await ctx.message.channel.send(data.lang["charset"].format("Dark Points"))
        elif key.lower() in ["dmod","defaultmod"]:
            if value in ["offensive","offensif","defensive","defensif"]:
                ndm = 0
                if ndm in ["defensive","defensif"]: ndm = 1
                if ndm != char.default_mod:
                    char = char.switchmod(True)
                await ctx.message.channel.send(data.lang["charset"].format(data.lang["default"]+" "+data.lang["mod"]))
        elif key.lower() in ["dkar","dkarma","defaultkarma"]:
            if int(value) >= -10 and int(value) <= 10:
                char = char.charset('dkar',int(value))
                await ctx.message.channel.send(data.lang["charset"].format(data.lang["default"]+" karma"))
        elif key.lower() in ["int","intuition","instinct"]:
            if int(value) >= 1 and int(value) <= 6:
                char = char.charset('int',int(value))
                await ctx.message.channel.send(data.lang["charset"].format(data.lang["intuition"]))
        else:
            await ctx.message.channel.send(data.lang["charset_invalid"].format(key))

    @commands.check(check_chanmj)
    @character.command(name="damage",aliases=["dmg"])
    async def character_damage(self,ctx,char: CharacterConverter, val: int):
        data = GenericCommandParameters(ctx)
        val = abs(val)
        char = char.charset('pv',-val)
        embd = discord.Embed(title=char.name,description=data.lang["damaged"],colour=discord.Color(int('ff0000',16)))
        embd.set_footer(text="The Tale of Great Cosmos")
        embd.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.avatar_url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        embd.add_field(name=data.lang["damage_taken"],value=str(val),inline=True)
        embd.add_field(name=data.lang["remaining_pv"],value=str(char.PV)+"/"+str(char.PVmax),inline=True)
        await ctx.message.channel.send(embed=embd)

    @commands.check(check_chanmj)
    @character.command(name="heal")
    async def character_heal(self,ctx,char: CharacterConverter, val: int):
        data = GenericCommandParameters(ctx)
        val = abs(val)
        if char.PV+ val > char.PVmax: val = char.PVmax-char.PV
        char = char.charset('pv',val)
        embd = discord.Embed(title=char.name,description=data.lang["healed"],colour=discord.Color(int('00ff00',16)))
        embd.set_footer(text="The Tale of Great Cosmos")
        embd.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.avatar_url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        embd.add_field(name=data.lang["heal_amount"],value=str(val),inline=True)
        embd.add_field(name=data.lang["remaining_pv"],value=str(char.PV)+"/"+str(char.PVmax),inline=True)

    @commands.check(check_chanmj)
    @character.command(name="getpm",aliases=["getmp"])
    async def character_getpm(self,ctx,char: CharacterConverter, val: int):
        data = GenericCommandParameters(ctx)
        if char.PM + val < 0:
            await ctx.message.channel.send(data.lang["no_more_pm"].format(str(char.pm)))
        else:
            if char.PM+val > char.PMmax: val = char.PMmax - char.PM
            char = char.charset('pm',val)
        got = data.lang["recovered"]
        if val < 0: got = data.lang["lost"]
        embd = discord.Embed(title=char.name,description=data.lang["get_pm"].format(got),colour=discord.Color(int('0000ff',16)))
        embd.set_footer(text="The Tale of Great Cosmos")
        embd.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.avatar_url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        embd.add_field(name=data.lang["get_pm_amount"].format(got),value=str(abs(val)),inline=True)
        embd.add_field(name=data.lang["remaining_pm"],value=str(char.PM)+"/"+str(char.PMmax),inline=True)
        await ctx.message.channel.send(embed=embd)

    @commands.check(check_chanmj)
    @character.command(name="setkarma",aliases=["getkarma","addkarma"])
    async def character_setkarma(self,ctx,char: CharacterConverter, val: int):
        data = GenericCommandParameters(ctx)
        if Skill.isskillin(char.skills,7): val *= 2 #chanceux
        if Skill.isskillin(char.skills,84): #creature harmonieuse
            if char.karma == 0 and val < 0: val -= 5
            elif char.karma == 0 and val > 0: val += 5
            elif char.karma+val > -5 and char.karma+val < 5 and val < 0: val -= 9
            elif char.karma+val > -5 and char.karma+val < 5 and val > 0: val += 9
        if char.karma+val < -10: val=-10-char.karma #char.karma = -10
        if char.karma+val > 10: val=10-char.karma #char.karma = 10
        char = char.charset('kar',val)
        got = data.lang["recovered"]
        if val < 0: got = data.lang["lost"]
        embd = discord.Embed(title=char.name,description=data.lang["get_karma"].format(got),colour=discord.Color(int('5B005B',16)))
        embd.set_footer(text="The Tale of Great Cosmos")
        embd.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.avatar_url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        embd.add_field(name=data.lang["get_karma_amount"].format(got),value=str(val),inline=True)
        embd.add_field(name=data.lang["current_karma"],value=str(char.karma),inline=True)
        await ctx.message.channel.send(embed=embd)

    @commands.check(check_chanmj)
    @character.command(name="reset")
    async def character_reset(self,ctx,char: CharacterConverter):
        data = GenericCommandParameters(ctx)
        char.resetchar()
        await ctx.message.channel.send(data.lang["resetchar"].format(char.name))

    @commands.check(check_haschar)
    @character.command(name="pay")
    async def character_pay(self,ctx,val: int):
        data = GenericCommandParameters(ctx)
        val = abs(val)
        if data.char.money-val < 0:
            await ctx.message.channel.send(data.lang["no_more_money"].format(char.money))
        else:
            data.char = data.char.charset('po',-val)
            embd = discord.Embed(title=data.char.name,description=data.data.lang["paid"],colour=discord.Color(int('ffff00',16)))
            embd.set_footer(text="The Tale of Great Cosmos")
            embd.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.avatar_url)
            embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
            embd.add_field(name=data.lang["money_spent"],value=str(val),inline=True)
            embd.add_field(name=data.lang["remaining_money"],value=str(data.char.money),inline=True)
            await ctx.message.channel.send(embed=embd)

    @commands.check(check_chanmj)
    @character.command(name="earnmoney",aliases=["earnpo"])
    async def character_earnpo(self,ctx,char: CharacterConverter, val: int):
        data = GenericCommandParameters(ctx)
        val = abs(val)
        char = char.charset('po',val)
        embd = discord.Embed(title=char.name,description=data.lang["paid"],colour=discord.Color(int('ffff00',16)))
        embd.set_footer(text="The Tale of Great Cosmos")
        embd.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.avatar_url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        embd.add_field(name=data.lang["money_spent"],value=str(val),inline=True)
        embd.add_field(name=data.lang["remaining_money"],value=str(char.money),inline=True)
        await ctx.message.channel.send(embed=embd)

    @commands.check(check_haschar)
    @commands.cooldown(1,10,BucketType.user)
    @character.command(name="info")
    async def character_info(self,ctx):
        data = GenericCommandParameters(ctx)
        if data.char.mod == 0: modd = data.lang["offensive"]
        else: modd = data.lang["defensive"]
        embd = discord.Embed(title=char.name,description="{} {}".format(data.char.race,data.char.classe))
        if char.dead: embd.set_image(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2018/06/you-are-dead.png")
        embd.set_footer(text="The Tale of Great Cosmos")
        embd.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.avatar_url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        if data.char.dead:
            embd.add_field(name=data.lang["PV"]+" :",value="DEAD",inline=True)
        else:
            embd.add_field(name=data.lang["PV"]+" :",value=str(data.char.PV)+"/"+str(data.char.PVmax),inline=True)
        if not data.char.dead: embd.add_field(name=data.lang["PM"]+" :",value=str(char.PM)+"/"+str(data.char.PMmax),inline=True)
        embd.add_field(name=data.lang["lvl"].capitalize()+" :",value=str(data.char.lvl),inline=True)
        if not data.char.dead: embd.add_field(name=data.lang["intuition"].capitalize()+" :",value=str(char.intuition),inline=True)
        if not data.char.dead: embd.add_field(name=data.lang["force"].capitalize()+" :",value=str(data.char.force),inline=True)
        if not data.char.dead: embd.add_field(name=data.lang["esprit"].capitalize()+" :",value=str(data.char.esprit),inline=True)
        if not data.char.dead: embd.add_field(name=data.lang["charisme"].capitalize()+" :",value=str(data.char.charisme),inline=True)
        if not data.char.dead: embd.add_field(name=data.lang["agilite"].capitalize()+" :",value=str(data.char.furtivite),inline=True)
        if not data.char.dead: embd.add_field(name=data.lang["karma"].capitalize()+" :",value=str(data.char.karma),inline=True)
        embd.add_field(name=data.lang["money"].capitalize()+" :",value=str(data.char.money),inline=True)
        if not data.char.dead: embd.add_field(name=data.lang["lp"]+" :",value=str(data.char.lp),inline=True)
        if not data.char.dead: embd.add_field(name=data.lang["dp"]+" :",value=str(data.char.dp),inline=True)
        if not data.char.dead: embd.add_field(name=data.lang["mod"].capitalize()+" :",value=modd,inline=True)
        embd.add_field(name=data.lang["mental"].capitalize()+" :",value=str(data.char.mental),inline=True)
        await ctx.message.channel.send(embed=embd)

    @commands.check(check_haschar)
    @commands.cooldown(1,10,BucketType.user)
    @character.command(name="stat")
    async def character_stat(self,ctx):
        data = GenericCommandParameters(ctx)
