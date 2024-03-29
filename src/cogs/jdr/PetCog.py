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
from src.tools.Character import *
from src.tools.CharacterUtils import *
from src.utils.converters import *
from src.tools.parsingdice import *
import typing
from random import randint

class PetCog(commands.Cog, name="Pets"):
    def __init__(self,bot,logger):
        self.bot = bot
        self.logger = logger

    @commands.check(check_jdrchannel)
    @commands.group(invoke_without_command=False)
    async def pet(self,ctx): pass

    @commands.check(check_chanmj)
    @pet.command(name="add",aliases=["+"])
    async def pet_add(self,ctx,char: CharacterConverter,petkey):
        """**GM/MJ only**
        Add a pet to a given character"""
        data = GenericCommandParameters(ctx)
        if char.pet_add(petkey):
            self.logger.log(logging.DEBUG+1,"/petadd (%s / %s) in channel %d of server %d",char.key,petkey,ctx.message.channel.id,ctx.message.guild.id)
            await ctx.message.channel.send(data.lang["petadd"].format(petkey,char.name))
        else:
            await ctx.message.channel.send(data.lang["petexist"].format(petkey))

    @commands.check(check_chanmj)
    @commands.cooldown(3,5,commands.BucketType.user)
    @pet.command(name="remove",aliases=["-","delete","del","rm"])
    async def pet_remove(self,ctx,char: CharacterConverter,petkey):
        """**GM/MJ only**
        Delete a pet from the given character. This cannot be undone"""
        data = GenericCommandParameters(ctx)
        if char.pet_delete(petkey):
            self.logger.log(logging.DEBUG+1,"/petrm (%s / %s) in channel %d of server %d",char.key,petkey,ctx.message.channel.id,ctx.message.guild.id)
            await ctx.message.channel.send(data.lang["petrm"].format(petkey,char.name))
        else:
            await ctx.message.channel.send(data.lang["petnotfound"].format(petkey))

    @commands.check(check_chanmj)
    @pet.command(name="set")
    async def pet_set(self,ctx,key,char: CharacterConverter,petkey,*,value):
        """**GM/MJ only**
        Same as character set command but for the specified pet.
        Somme attributes for characters are not avalaible for pet."""
        data = GenericCommandParameters(ctx)
        if petkey not in char.pet:
            await ctx.message.channel.send(data.lang["petnotfound"].format(petkey))
        else:
            self.logger.log(logging.DEBUG+1,"/petset %s (%s / %s) in channel %d of server %d",key,char.key,petkey,ctx.message.channel.id,ctx.message.guild.id)
            if key.lower() == "name":
                char.pet[petkey].setname(value)
                await ctx.message.channel.send(data.lang["petset"].format(data.lang["name"]))
            elif key.lower() in ["pv","hp"]:
                char = char.pet[petkey].petset('pvmax',int(value))
                await ctx.message.channel.send(data.lang["petset"].format(data.lang["PV"]+" max"))
            elif key.lower() in ["pm","mp"]:
                char = char.pet[petkey].petset('pmmax',int(value))
                await ctx.message.channel.send(data.lang["petset"].format(data.lang["PM"]+" max"))
            elif key.lower() in ["str","force","strength"]:
                char = char.pet[petkey].petset('str',int(value))
                await ctx.message.channel.send(data.lang["petset"].format(data.lang["force"]))
            elif key.lower() in ["spr","esprit","spirit"]:
                char = char.pet[petkey].petset('spr',int(value))
                await ctx.message.channel.send(data.lang["petset"].format(data.lang["esprit"]))
            elif key.lower() in ["cha","charisme","charisma"]:
                char = char.pet[petkey].petset('cha',int(value))
                await ctx.message.channel.send(data.lang["petset"].format(data.lang["charisme"]))
            elif key.lower() in ["agi","agilite","agility","furtivite"]:
                char = char.pet[petkey].petset('agi',int(value))
                await ctx.message.channel.send(data.lang["petset"].format(data.lang["agilite"]))
            elif key.lower() in ["prec","precision"]:
                char = char.pet[petkey].petset('prec',int(value))
                await ctx.message.channel.send(data.lang["petset"].format(data.lang["precision"]))
            elif key.lower() in ["luck","chance"]:
                char = char.pet[petkey].petset('luck',int(value))
                await ctx.message.channel.send(data.lang["petset"].format(data.lang["chance"]))
            elif key.lower() in ["dmod","defaultmod"]:
                if value in ["offensive","offensif","defensive","defensif"]:
                    ndm = 0
                    if value in ["defensive","defensif"]: ndm = 1
                    if ndm != char.pet[petkey].default_mod:
                        char = char.pet[petkey].switchmod(True)
                    await ctx.message.channel.send(data.lang["petset"].format(data.lang["default"]+" "+data.lang["mod"]))
            elif key.lower() in ["int","instinct"]:
                if int(value) >= 1 and int(value) <= 6:
                    char = char.pet[petkey].petset('int',int(value))
                    await ctx.message.channel.send(data.lang["petset"].format(data.lang["instinct"]))
            elif key.lower() in ["espece","species","spe"]:
                char.pet[petkey].setespece(value)
                await ctx.message.channel.send(data.lang["petset"].format(data.lang["espece"]))
            else:
                await ctx.message.channel.send(data.lang["charset_invalid"].format(key))

    async def _switchmod(self,ctx,data,char,petkey):
        if petkey not in char.pet:
            await ctx.message.channel.send(data.lang["petnotfound"].format(petkey))
        else:
            char = char.pet[petkey].switchmod()
            mod = data.lang["defensive"]
            if char.pet[petkey].mod == 0: mod = data.lang["offensive"]
            await ctx.message.channel.send(data.lang["switchmod"].format(petkey,mod))

    @commands.check(check_haschar)
    @commands.cooldown(1,5,commands.BucketType.user)
    @pet.command(name="switchmod",aliases=["switchmode"])
    async def pet_switchmod(self,ctx,petkey):
        """**Player only**
        Switch the battle mod of one of your pet"""
        data = GenericCommandParameters(ctx)
        self.logger.log(logging.DEBUG+1,"/petswitchmod (%s / %s) in channel %d of server %d",data.char.key,petkey,ctx.message.channel.id,ctx.message.guild.id)
        await self._switchmod(ctx,data,data.char,petkey)

    @commands.check(check_chanmj)
    @pet.command(name="lvlup",aliases=["levelup"])
    async def pet_lvlup(self,ctx,char: CharacterConverter,petkey):
        """**GM/MJ only**
        Make level up the specified pet of the given character"""
        data = GenericCommandParameters(ctx)
        if petkey not in char.pet:
            await ctx.message.channel.send(data.lang["petnotfound"].format(petkey))
        else:
            self.logger.log(logging.DEBUG+1,"/petlevelup (%s / %s) in channel %d of server %d",char.key,petkey,ctx.message.channel.id,ctx.message.guild.id)
            char.pet[petkey].lvlup()
            embd = discord.Embed(title=char.pet[petkey].name,description=data.lang["lvlup"],colour=discord.Color(int('5B005B',16)))
            embd.set_footer(text="The Tale of Great Cosmos")
            embd.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.display_avatar.url)
            embd.set_thumbnail(url="https://www.thetaleofgreatcosmos.fr/wp-content/uploads/2019/11/TTGC_Text.png")
            embd.add_field(name=data.lang["lvl"].capitalize()+" :",value=str(char.pet[petkey].lvl),inline=True)
            if char.pet[petkey].lvl == 2:
                dice,dice2 = randint(1,10),randint(1,10)
                embd.add_field(name=data.lang["lvlup_bonus"],value=data.lang["lvlup_2"].format(str(dice),str(dice2)),inline=True)
                embd.add_field(name=data.lang["lvlup_current"].format(data.lang["force"]),value=str(char.pet[petkey].force),inline=True)
                embd.add_field(name=data.lang["lvlup_current"].format(data.lang["esprit"]),value=str(char.pet[petkey].esprit),inline=True)
                embd.add_field(name=data.lang["lvlup_current"].format(data.lang["charisme"]),value=str(char.pet[petkey].charisme),inline=True)
                embd.add_field(name=data.lang["lvlup_current"].format(data.lang["agilite"]),value=str(char.pet[petkey].agilite),inline=True)
                embd.add_field(name=data.lang["lvlup_current"].format(data.lang["precision"]),value=str(char.pet[petkey].precision),inline=True)
                embd.add_field(name=data.lang["lvlup_current"].format(data.lang["chance"]),value=str(char.pet[petkey].luck),inline=True)
            elif char.pet[petkey].lvl == 3:
                dice = randint(1,10)
                dic = {"force":char.pet[petkey].force,"esprit":char.pet[petkey].esprit,"charisme":char.pet[petkey].charisme,"agilite":char.pet[petkey].agilite,"precision":char.pet[petkey].precision,"chance":char.pet[petkey].luck}
                statmin = ("force",char.pet[petkey].force)
                for i,k in dic.items():
                    if k < statmin[1]: statmin = (i,k)
                embd.add_field(name=data.lang["lvlup_bonus"],value=data.lang["lvlup_3"].format(statmin[0],str(dice)),inline=True)
                embd.add_field(name=data.lang["lvlup_current"].format(data.lang[statmin[0]]),value=str(statmin[1]),inline=True)
                embd.add_field(name=data.lang["lvlup_next"].format(data.lang[statmin[0]]),value=str(statmin[1]+dice),inline=True)
            elif char.pet[petkey].lvl == 4:
                dice = randint(1,100)
                embd.add_field(name=data.lang["lvlup_bonus"],value=data.lang["lvlup_4"].format(str(dice)),inline=True)
                embd.add_field(name=data.lang["lvlup_current"].format(data.lang["PV"]),value=str(char.pet[petkey].PV)+"/"+str(char.pet[petkey].PVmax),inline=True)
                embd.add_field(name=data.lang["lvlup_current"].format(data.lang["PM"]),value=str(char.pet[petkey].PM)+"/"+str(char.pet[petkey].PMmax),inline=True)
            elif char.pet[petkey].lvl == 5:
                embd.add_field(name=data.lang["lvlup_bonus"],value=data.lang["lvlup_5"],inline=True)
                embd.add_field(name=data.lang["lvlup_current"].format(data.lang["force"]),value=str(char.pet[petkey].force),inline=True)
                embd.add_field(name=data.lang["lvlup_current"].format(data.lang["esprit"]),value=str(char.pet[petkey].esprit),inline=True)
                embd.add_field(name=data.lang["lvlup_current"].format(data.lang["charisme"]),value=str(char.pet[petkey].charisme),inline=True)
                embd.add_field(name=data.lang["lvlup_current"].format(data.lang["agilite"]),value=str(char.pet[petkey].agilite),inline=True)
                embd.add_field(name=data.lang["lvlup_current"].format(data.lang["precision"]),value=str(char.pet[petkey].precision),inline=True)
                embd.add_field(name=data.lang["lvlup_current"].format(data.lang["chance"]),value=str(char.pet[petkey].luck),inline=True)
            else:
                embd.add_field(name=data.lang["lvlup_bonus"],value=data.lang["lvlup_6"],inline=True)
                embd.add_field(name=data.lang["lvlup_current"].format(data.lang["PV"]),value=str(char.pet[petkey].PV)+"/"+str(char.pet[petkey].PVmax),inline=True)
                embd.add_field(name=data.lang["lvlup_current"].format(data.lang["PM"]),value=str(char.pet[petkey].PM)+"/"+str(char.pet[petkey].PMmax),inline=True)
                embd.add_field(name=data.lang["lvlup_current"].format(data.lang["force"]),value=str(char.pet[petkey].force),inline=True)
                embd.add_field(name=data.lang["lvlup_current"].format(data.lang["esprit"]),value=str(char.pet[petkey].esprit),inline=True)
                embd.add_field(name=data.lang["lvlup_current"].format(data.lang["charisme"]),value=str(char.pet[petkey].charisme),inline=True)
                embd.add_field(name=data.lang["lvlup_current"].format(data.lang["agilite"]),value=str(char.pet[petkey].agilite),inline=True)
                embd.add_field(name=data.lang["lvlup_current"].format(data.lang["precision"]),value=str(char.pet[petkey].precision),inline=True)
                embd.add_field(name=data.lang["lvlup_current"].format(data.lang["chance"]),value=str(char.pet[petkey].luck),inline=True)
            await ctx.message.channel.send(embed=embd)

    async def _petroll(self,ctx,data,char,petkey,stat,operator,expression):
        if petkey not in char.pet:
            await ctx.message.channel.send(data.lang["petnotfound"].format(petkey))
        else:
            parser = ParsePetRoll(data.lang,char,char.pet[petkey],stat,operator,expression)
            msg = parser.resolv()
            await ctx.message.channel.send(msg,tts=parser.tts)

    @commands.check(check_haschar)
    @pet.command(name="roll",aliases=["r"])
    async def pet_roll(self,ctx,petkey,stat,operator: typing.Optional[OperatorConverter] = "+",*,expression=None):
        """**Player only**
        Same as your character roll command, but for one of your pet"""
        data = GenericCommandParameters(ctx)
        self.logger.log(logging.DEBUG+1,"/petroll (%s / %s) in channel %d of server %d",data.char.key,petkey,ctx.message.channel.id,ctx.message.guild.id)
        await self._petroll(ctx,data,data.char,petkey,stat,operator,expression)

    async def _petinfo(self,ctx,data,char,petkey):
        if petkey not in char.pet:
            await ctx.message.channel.send(data.lang["petnotfound"].format(petkey))
        else:
            modd = data.lang["defensive"]
            if char.pet[petkey].mod == 0: modd = data.lang["offensive"]
            embd = discord.Embed(title=char.pet[petkey].name,description=data.lang["petbelong"].format(char.pet[petkey].espece,char.name),colour=discord.Color(randint(0,int('ffffff',16))),url="http://thetaleofgreatcosmos.fr/wiki/index.php?title="+char.name.replace(" ","_"))
            embd.set_footer(text="The Tale of Great Cosmos")
            embd.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.display_avatar.url)
            embd.set_thumbnail(url="https://www.thetaleofgreatcosmos.fr/wp-content/uploads/2019/11/TTGC_Text.png")
            embd.add_field(name=data.lang["PV"]+" :",value=str(char.pet[petkey].PV)+"/"+str(char.pet[petkey].PVmax),inline=True)
            embd.add_field(name=data.lang["PM"]+" :",value=str(char.pet[petkey].PM)+"/"+str(char.pet[petkey].PMmax),inline=True)
            embd.add_field(name=data.lang["lvl"].capitalize()+" :",value=str(char.pet[petkey].lvl),inline=True)
            embd.add_field(name=data.lang["instinct"].capitalize()+" :",value=str(char.pet[petkey].instinct),inline=True)
            embd.add_field(name=data.lang["force"].capitalize()+" :",value=str(char.pet[petkey].force),inline=True)
            embd.add_field(name=data.lang["esprit"].capitalize()+" :",value=str(char.pet[petkey].esprit),inline=True)
            embd.add_field(name=data.lang["charisme"].capitalize()+" :",value=str(char.pet[petkey].charisme),inline=True)
            embd.add_field(name=data.lang["agilite"].capitalize()+" :",value=str(char.pet[petkey].agilite),inline=True)
            embd.add_field(name=data.lang["precision"].capitalize()+" :",value=str(char.pet[petkey].precision),inline=True)
            embd.add_field(name=data.lang["chance"].capitalize()+" :",value=str(char.pet[petkey].luck),inline=True)
            embd.add_field(name=data.lang["karma"].capitalize()+" :",value=str(char.pet[petkey].karma),inline=True)
            embd.add_field(name=data.lang["mod"].capitalize()+" :",value=modd,inline=True)
            await ctx.message.channel.send(embed=embd)

    @commands.check(check_haschar)
    @commands.cooldown(1,10,commands.BucketType.user)
    @pet.command(name="info")
    async def pet_info(self,ctx,petkey):
        """**Player only**
        Show all information related to one of your pets"""
        data = GenericCommandParameters(ctx)
        self.logger.log(logging.DEBUG+1,"/petinfo (%s / %s) in channel %d of server %d",data.char.key,petkey,ctx.message.channel.id,ctx.message.guild.id)
        await self._petinfo(ctx,data,data.char,petkey)

    @commands.check(check_chanmj)
    @pet.command(name="setkarma")
    async def pet_setkarma(self,ctx,char: CharacterConverter,petkey,amount: int):
        """**GM/MJ only**
        Set the karma like character setkarma command for the given pet"""
        data = GenericCommandParameters(ctx)
        if petkey not in char.pet:
            await ctx.message.channel.send(data.lang["petnotfound"].format(petkey))
        else:
            char = char.pet[petkey].petset('kar',amount)
            got = data.lang["recovered"]
            if amount < 0: got = data.lang["lost"]
            embd = discord.Embed(title=char.pet[petkey].name,description=data.lang["get_karma"].format(got),colour=discord.Color(int('5B005B',16)))
            embd.set_footer(text="The Tale of Great Cosmos")
            embd.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.display_avatar.url)
            embd.set_thumbnail(url="https://www.thetaleofgreatcosmos.fr/wp-content/uploads/2019/11/TTGC_Text.png")
            embd.add_field(name=data.lang["get_karma_amount"].format(got),value=str(amount),inline=True)
            embd.add_field(name=data.lang["current_karma"],value=str(char.pet[petkey].karma),inline=True)
            self.logger.log(logging.DEBUG+1,"/petsetkarma (%s / %s) in channel %d of server %d",char.key,petkey,ctx.message.channel.id,ctx.message.guild.id)
            await ctx.message.channel.send(embed=embd)

    @commands.check(check_haschar)
    @commands.cooldown(1,10,commands.BucketType.user)
    @pet.command(name="stat")
    async def pet_stat(self,ctx,petkey):
        """**Player only**
        Show dice related statistics of one of your pets"""
        data = GenericCommandParameters(ctx)
        if petkey not in data.char.pet:
            await ctx.message.channel.send(data.lang["petnotfound"].format(petkey))
        else:
            embd = discord.Embed(title=data.lang["petstat"],description=data.char.pet[petkey].name,colour=discord.Color(randint(0,int('ffffff',16))),url="http://thetaleofgreatcosmos.fr/wiki/index.php?title="+data.char.name.replace(" ","_"))
        embd.set_footer(text="The Tale of Great Cosmos")
        embd.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.display_avatar.url)
        embd.set_thumbnail(url="https://www.thetaleofgreatcosmos.fr/wp-content/uploads/2019/11/TTGC_Text.png")
        embd.add_field(name=data.lang["dice_rolled"],value=str(data.char.pet[petkey].stat[0]),inline=True)
        embd.add_field(name=data.lang["super_critic_success"],value=str(data.char.pet[petkey].stat[1]),inline=True)
        embd.add_field(name=data.lang["critic_success"],value=str(data.char.pet[petkey].stat[2]),inline=True)
        embd.add_field(name=data.lang["success"],value=str(data.char.pet[petkey].stat[3]),inline=True)
        embd.add_field(name=data.lang["fail"],value=str(data.char.pet[petkey].stat[4]),inline=True)
        embd.add_field(name=data.lang["critic_fail"],value=str(data.char.pet[petkey].stat[5]),inline=True)
        embd.add_field(name=data.lang["super_critic_fail"],value=str(data.char.pet[petkey].stat[6]),inline=True)
        self.logger.log(logging.DEBUG+1,"/petstat (%s / %s) in channel %d of server %d",data.char.key,petkey,ctx.message.channel.id,ctx.message.guild.id)
        await ctx.message.channel.send(embed=embd)

    @commands.check(check_chanmj)
    @pet.command(name="damage",aliases=["dmg"])
    async def pet_damage(self,ctx,char: CharacterConverter,petkey,val: int):
        """**GM/MJ only**
        Inflict damage to a pet"""
        data = GenericCommandParameters(ctx)
        if petkey not in char.pet:
            await ctx.message.channel.send(data.lang["petnotfound"].format(petkey))
        else:
            val = abs(val)
            char = char.pet[petkey].petset('pv',-val)
            embd = discord.Embed(title=char.pet[petkey].name,description=data.lang["damaged"],colour=discord.Color(int('ff0000',16)))
            embd.set_footer(text="The Tale of Great Cosmos")
            embd.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.display_avatar.url)
            embd.set_thumbnail(url="https://www.thetaleofgreatcosmos.fr/wp-content/uploads/2019/11/TTGC_Text.png")
            embd.add_field(name=data.lang["damage_taken"],value=str(val),inline=True)
            embd.add_field(name=data.lang["remaining_pv"],value=str(char.pet[petkey].PV)+"/"+str(char.pet[petkey].PVmax),inline=True)
            self.logger.log(logging.DEBUG+1,"/petdmg (%s / %s) in channel %d of server %d",char.key,petkey,ctx.message.channel.id,ctx.message.guild.id)
            await ctx.message.channel.send(embed=embd)

    @commands.check(check_chanmj)
    @pet.command(name="heal",aliases=["cure"])
    async def pet_heal(self,ctx,char: CharacterConverter,petkey,val: int):
        """**GM/MJ only**
        Heal the given pet"""
        data = GenericCommandParameters(ctx)
        if petkey not in char.pet:
            await ctx.message.channel.send(data.lang["petnotfound"].format(petkey))
        else:
            val = abs(val)
            if char.pet[petkey].PV+ val > char.pet[petkey].PVmax: val = char.pet[petkey].PVmax-char.pet[petkey].PV
            char = char.pet[petkey].petset('pv',val)
            embd = discord.Embed(title=char.pet[petkey].name,description=data.lang["healed"],colour=discord.Color(int('00ff00',16)))
            embd.set_footer(text="The Tale of Great Cosmos")
            embd.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.display_avatar.url)
            embd.set_thumbnail(url="https://www.thetaleofgreatcosmos.fr/wp-content/uploads/2019/11/TTGC_Text.png")
            embd.add_field(name=data.lang["heal_amount"],value=str(val),inline=True)
            embd.add_field(name=data.lang["remaining_pv"],value=str(char.pet[petkey].PV)+"/"+str(char.pet[petkey].PVmax),inline=True)
            self.logger.log(logging.DEBUG+1,"/petheal (%s / %s) in channel %d of server %d",char.key,petkey,ctx.message.channel.id,ctx.message.guild.id)
            await ctx.message.channel.send(embed=embd)

    @commands.check(check_chanmj)
    @pet.command("getpm",aliases=["getmp"])
    async def pet_getpm(self,ctx,char: CharacterConverter,petkey,val: int):
        """**GM/MJ only**
        Set MP/PM for the given pet such as character getPM for characters does"""
        data = GenericCommandParameters(ctx)
        if petkey not in char.pet:
            await ctx.message.channel.send(data.lang["petnotfound"].format(petkey))
        else:
            if char.pet[petkey].PM + val < 0:
                await ctx.message.channel.send(data.lang["no_more_pm"].format(str(char.pet[petkey].PM)))
            else:
                if char.pet[petkey].PM+val > char.pet[petkey].PMmax: val = char.pet[petkey].PMmax - char.pet[petkey].PM
                char = char.pet[petkey].petset('pm',val)
            got = data.lang["recovered"]
            if val < 0: got = data.lang["lost"]
            embd = discord.Embed(title=char.pet[petkey].name,description=data.lang["get_pm"].format(got),colour=discord.Color(int('0000ff',16)))
            embd.set_footer(text="The Tale of Great Cosmos")
            embd.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.display_avatar.url)
            embd.set_thumbnail(url="https://www.thetaleofgreatcosmos.fr/wp-content/uploads/2019/11/TTGC_Text.png")
            embd.add_field(name=data.lang["get_pm_amount"].format(got),value=str(abs(val)),inline=True)
            embd.add_field(name=data.lang["remaining_pm"],value=str(char.pet[petkey].PM)+"/"+str(char.pet[petkey].PMmax),inline=True)
            self.logger.log(logging.DEBUG+1,"/petgetpm (%s / %s) in channel %d of server %d",char.key,petkey,ctx.message.channel.id,ctx.message.guild.id)
            await ctx.message.channel.send(embed=embd)
