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
from src.tools.parsingdice import *
import requests

class MainJDR(commands.Cog, name="JDR"):
    def __init__(self,bot,logger):
        self.bot = bot
        self.logger = logger

    @commands.cooldown(1,2,commands.BucketType.user)
    @commands.command(aliases=["rollindep","r","rolldice"])
    async def roll(self,ctx,*,expression):
        """Roll dice and perform operations (supported symbols and operations : `*,+,-,/,()`) if given in the expression field.
        For rolling a dice, you have to use the litteral expression `xdy` where `x` is the number of dice rolled,  `d` the letter `d` and `y` the number of side of the dice (`1d100` will roll 1 dice with 100 sides for example).
        You can also roll special dice with your own values by writing them between brackets as following : `1d{red,blue,yellow,green}`.
        Full example : `/rollindep (10+1d100)*(2d10-5d8)` will return the result of the following expression : `(10+(1 dice with 100 sides))*((2 dice with 10 sides)-(5 dice with 8 sides))` <br/>
        Special dice example : `/rollindep 1d{1,2,3,4,5,6,7,8,9,10,Jack,Queen,King}+1d{Clubs,Diamonds,Hearts,Spades}` will return a single card with its value and its color (example : Queen of Spades)"""
        data = GenericCommandParameters(ctx)
        parser = ParseRoll(expression)
        final_result,final_expression = parser.resolv()
        self.logger.log(logging.DEBUG+1,"roll %d (%s) in channel %d of server %d",final_result,final_expression,ctx.message.channel.id,ctx.message.guild.id)
        await ctx.message.channel.send(data.lang["rollindep"].format(final_result,final_expression))

    @commands.check(check_admin)
    @commands.cooldown(1,30,commands.BucketType.guild)
    @commands.command(aliases=["setgmrole"])
    async def setmjrole(self,ctx,mjrole: discord.Role):
        """**Admin only**
        Define the GM/MJ role for the whole server. All people having this role will be able to create and manage RM/JDR"""
        data = GenericCommandParameters(ctx)
        data.srv.setmjrole(str(mjrole.id))
        self.logger.log(logging.DEBUG+1,"set mj role to %d in server %d",mjrole.id,ctx.message.guild.id)
        await ctx.message.channel.send(data.lang["setmjrole"].format(mjrole.mention))

    @commands.check(check_chanmj)
    @commands.cooldown(1,5,commands.BucketType.guild)
    @commands.command()
    async def apart(self,ctx,nomute: commands.Greedy[discord.Member]):
        """**GM/MJ only**
        Mute and deafen every players that are not mentioned. You have to be in a vocal channel.
        Members are considered as player only if they are linked to a character. Finally, even if you don't mention yourself, this command won't mute/deafen you."""
        data = GenericCommandParameters(ctx)
        self.logger.log(logging.DEBUG+1,"appart launched by %d in channel %d of server %d",ctx.message.author.id,ctx.message.channel.id,ctx.message.guild.id)
        if ctx.message.author.voice.channel is not None:
            linked = []
            for i in data.charbase:
                if i.linked is not None: linked.append(i.linked)
            ls = list(ctx.message.author.voice.channel.members)
            if len(nomute) == 0:
                for i in ls:
                    if str(i.id) in linked or i == ctx.message.author:
                        await i.edit(mute=False,deafen=False)
            else:
                for i in ls:
                    if str(i.id) in linked or i == ctx.message.author:
                        if i in nomute or i == ctx.message.author:
                            await i.edit(mute=False,deafen=False)
                        else:
                            await i.edit(mute=True,deafen=True)

    @commands.cooldown(1,1,commands.BucketType.channel)
    @commands.command()
    async def wiki(self,ctx,*,query):
        """Make a quick search on The Tale of Great Cosmos wiki"""
        data = GenericCommandParameters(ctx)
        query = query.replace(" ","_")
        info = requests.get("http://thetaleofgreatcosmos.fr/wiki/api.php?action=parse&page="+query+"&format=json&redirects=true")
        exist_test = requests.get("http://thetaleofgreatcosmos.fr/wiki/index.php?title="+query)
        if exist_test.status_code != 200:
            await ctx.message.channel.send(data.lang["wiki_unexisting"].format(str(exist_test.status_code)))
            return
        descrip = info.json()["parse"]["text"]["*"]
        descrip = descrip.split("</p>")[0]
        while descrip.find("<") != -1:
            descrip = descrip[:descrip.find("<")]+descrip[descrip.find(">")+1:]
        if info.json()["parse"]["text"]["*"].find("<img") == -1:
            img = None
        else:
            pos = info.json()["parse"]["text"]["*"].find("<img")
            temp = info.json()["parse"]["text"]["*"]
            temp = temp[pos+1:]
            temp = temp[:temp.find("/>")]
            temp = temp[temp.find("src=")+5:]
            img = "http://thetaleofgreatcosmos.fr"+temp.split('"')[0]
        embd = discord.Embed(title=info.json()["parse"]["title"],description=descrip,url="http://thetaleofgreatcosmos.fr/wiki/index.php?title="+query,colour=discord.Color(randint(0,int('ffffff',16))))
        embd.set_footer(text="The Tale of Great Cosmos - Wiki")
        if img is not None:
            embd.set_image(url=img)
        embd.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.avatar_url,url="http://thetaleofgreatcosmos.fr/wiki/index.php?title="+query)
        embd.set_thumbnail(url="https://www.thetaleofgreatcosmos.fr/wp-content/uploads/2019/11/TTGC_Text.png")
        if len(info.json()["parse"]["redirects"]) != 0:
            embd.add_field(name=data.lang["wiki_redirect"],value=info.json()["parse"]["redirects"][0]["from"],inline=True)
        self.logger.log(logging.DEBUG+1,"wiki query (%s) in channel %d of server %d",query,ctx.message.channel.id,ctx.message.guild.id)
        await ctx.message.channel.send(embed=embd)

    @commands.command(aliases=['jointtgc','ttgc'])
    async def jointhegame(self,ctx):
        """Get a link to the discord of The Tale of Great Cosmos"""
        inv = await self.bot.get_channel(326648561976737792).create_invite(max_age=3600)
        self.logger.log(logging.DEBUG+1,"invite for TTGC generated for %d in channel %d on server %d",ctx.message.author.id,ctx.message.channel.id,ctx.message.guild.id)
        await ctx.message.channel.send("Rejoignez le serveur officiel The Tale of Great Cosmos (serveur FR) : \n{}".format(str(inv.url)))

    @commands.group(invoke_without_command=False,aliases=["rp"])
    async def jdr(self,ctx): pass

    @commands.check(check_mj)
    @commands.cooldown(1,60,commands.BucketType.user)
    @jdr.command(name="start",aliases=["create"])
    async def jdr_start(self,ctx,chan: discord.TextChannel):
        """**GM/MJ role Only**
        Start a RP/JDR in the mentioned channel"""
        data = GenericCommandParameters(ctx)
        try:
            data.srv.getJDR(str(chan.id))
            await ctx.message.channel.send(data.lang["jdr_exist"].format(chan.mention))
        except:
            data.srv.jdrstart(str(chan.id),str(ctx.message.author.id))
            self.logger.log(logging.DEBUG+1,"JDR created in channel %d of server %d",chan.id,ctx.message.guild.id)
            await ctx.message.channel.send(data.lang["jdr_start"].format(chan.mention,ctx.message.author.mention))

    @commands.check(check_admin)
    @commands.cooldown(1,60,commands.BucketType.user)
    @jdr.command(name="delete")
    async def jdr_delete(self,ctx,chan: discord.TextChannel):
        """**Admin only**
        Delete the RP/JDR in the mentioned channel. This cannot be undone once performed and all data related to it will be lost forever and ever."""
        data = GenericCommandParameters(ctx)
        curjdr = data.srv.getJDR(str(chan.id))
        await ctx.message.channel.send(data.lang["jdr_delete_confirm"].format(chan.mention))
        chk = lambda m: m.author == ctx.message.author and m.channel == ctx.message.channel and m.content.lower() == 'confirm'
        try: answer = await self.bot.wait_for('message',check=chk,timeout=60)
        except asyncio.TimeoutError: answer = None
        if answer is None:
            await ctx.message.channel.send(data.lang["timeout"])
        else:
            curjdr.delete()
            self.logger.log(logging.DEBUG+1,"JDR deleted in channel %d of server %d",chan.id,ctx.message.guild.id)
            await ctx.message.channel.send(data.lang["jdr_delete"].format(chan.mention))

    @commands.check(check_admin)
    @commands.check(check_mj)
    @commands.cooldown(1,60,commands.BucketType.user)
    @jdr.command(name="copy")
    async def jdr_copy(self,ctx,src: discord.TextChannel, dest: discord.TextChannel):
        """**Admin and GM/MJ role only**
        Copy all the data of a RP/JDR from a channel to one other."""
        data = GenericCommandParameters(ctx)
        if src.guild.id != ctx.message.guild.id or src.guild.id != dest.guild.id:
            await ctx.message.channel.send(data.lang["jdrcopy_serverror"])
        else:
            await ctx.message.channel.send(data.lang["jdrcopy_confirm"].format(src.mention,dest.mention))
            chk = lambda m: m.author == ctx.message.author and m.channel == ctx.message.channel and m.content.lower() == 'confirm'
            try: answer = await self.bot.wait_for('message',check=chk,timeout=60)
            except asyncio.TimeoutError: answer = None
            if answer is None:
                await ctx.message.channel.send(data.lang["timeout"])
            else:
                data.srv.getJDR(str(src.id)).copy(str(dest.id))
                self.logger.log(logging.DEBUG+1,"JDR copy from channel %d to %d in server %d",src.id,dest.id,ctx.message.guild.id)
                await ctx.message.channel.send(data.lang["jdrcopy"])

    @commands.check(check_admin)
    @commands.check(check_mj)
    @commands.cooldown(1,5,commands.BucketType.user)
    @jdr.command(name="extend")
    async def jdr_extend(self,ctx,src: discord.TextChannel, dest: discord.TextChannel):
        """**Admin and GM/MJ role only**
        Extend a RP/JDR from a channel to another. By extending, all data of the game will be avalaible on both channels."""
        data = GenericCommandParameters(ctx)
        if src.guild.id != ctx.message.guild.id or src.guild.id != dest.guild.id:
            await ctx.message.channel.send(data.lang["jdrcopy_serverror"])
        else:
            await ctx.message.channel.send(data.lang["jdrextend_confirm"].format(src.mention,dest.mention))
            chk = lambda m: m.author == ctx.message.author and m.channel == ctx.message.channel and m.content.lower() == 'confirm'
            try: answer = await self.bot.wait_for('message',check=chk,timeout=60)
            except asyncio.TimeoutError: answer = None
            if answer is None:
                await ctx.message.channel.send(data.lang["timeout"])
            else:
                try:
                    data.srv.getJDR(str(dest.id)).delete()
                except: pass
                data.srv.getJDR(str(src.id)).extend(str(dest.id))
                self.logger.log(logging.DEBUG+1,"JDR extend from channel %d to %d in server %d",src.id,dest.id,ctx.message.guild.id)
                await ctx.message.channel.send(data.lang["jdrextend"])

    @commands.check(check_admin)
    @commands.cooldown(1,5,commands.BucketType.user)
    @jdr.command(name="unextend")
    async def jdr_unextend(self,ctx,src: discord.TextChannel, dest: discord.TextChannel):
        """**Admin only**
        Remove an extension between two channels for a RP/JDR. The data will be only avalaible in the source/origin channel after performing this"""
        data = GenericCommandParameters(ctx)
        if src.guild.id != ctx.message.guild.id or src.guild.id != dest.guild.id:
            await ctx.message.channel.send(data.lang["jdrcopy_serverror"])
        else:
            data.srv.getJDR(str(src.id)).unextend(str(dest.id))
            self.logger.log(logging.DEBUG+1,"JDR unextended from channel %d to %d in server %d",src.id,dest.id,ctx.message.guild.id)
            await ctx.message.channel.send(data.lang["jdrunextend"])

    @commands.check(check_admin)
    @commands.cooldown(1,5,commands.BucketType.user)
    @jdr.command(name="unextendall")
    async def jdr_unextendall(self,ctx,src: discord.TextChannel):
        """**Admin only**
        Remove all extensions for a RP/JDR. The data will be only avalaible in the source/origin channel after performing this"""
        data = GenericCommandParameters(ctx)
        data.srv.getJDR(str(src.id)).unextend_all()
        self.logger.log(logging.DEBUG+1,"JDR unextended all from channel %d in server %d",src.id,ctx.message.guild.id)
        await ctx.message.channel.send(data.lang["jdrunextend"])

    @commands.check(check_admin)
    @commands.cooldown(1,30,commands.BucketType.user)
    @jdr.command(name="list")
    async def jdr_list(self,ctx):
        """**Admin only**
        Show the list of all RP/JDR on the server"""
        data = GenericCommandParameters(ctx)
        ls = data.srv.jdrlist()
        embd = discord.Embed(title=data.lang["jdrlist_title"],description=data.lang["jdrlist"],colour=discord.Color(int('0000ff',16)))
        embd.set_footer(text=str(ctx.message.created_at))
        embd.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.avatar_url)
        embd.set_thumbnail(url="https://www.thetaleofgreatcosmos.fr/wp-content/uploads/2019/11/TTGC_Text.png")
        for i in ls:
            info = data.lang["jdrlist_info"].format(discord.utils.get(ctx.message.guild.members,id=int(i[3])).mention,str(i[2]),str(i[1]))
            embd.add_field(name="#{} :".format(str(discord.utils.get(ctx.message.guild.channels,id=int(i[0])))),value=info,inline=True)
        self.logger.log(logging.DEBUG+1,"JDR list shown in channel %d in server %d",ctx.message.channel.id,ctx.message.guild.id)
        await ctx.message.channel.send(embed=embd)
