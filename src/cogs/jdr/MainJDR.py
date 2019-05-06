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
from src.parsingdice import *
import requests

class MainJDR(commands.Cog):
    def __init__(self,bot,logger):
        self.bot = bot
        self.logger = logger

    @commands.cooldown(1,2,commands.BucketType.user)
    @commands.command(aliases=["rollindep","r","rolldice"])
    async def roll(self,ctx,*,expression):
        data = GenericCommandParameters(ctx)
        parser = ParseRoll(expression)
        final_result,final_expression = parser.resolv()
        await ctx.message.channel.send(data.lang["rollindep"].format(final_result,final_expression))

    @commands.check(check_admin)
    @commands.cooldown(1,30,commands.BucketType.guild)
    @commands.command()
    async def setmjrole(self,ctx,mjrole: discord.Role):
        data = GenericCommandParameters(ctx)
        data.srv.setmjrole(str(mjrole.id))
        await ctx.message.channel.send(data.lang["setmjrole"].format(mjrole.mention))

    @commands.check(check_chanmj)
    @commands.cooldown(1,5,commands.BucketType.guild)
    @commands.command()
    async def apart(self,ctx,nomute: commands.Greedy[discord.Member]):
        data = GenericCommandParameters(ctx)
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
                        if i in nomute or i == message.author:
                            await i.edit(i,mute=False,deafen=False)
                        else:
                            await i.edit(i,mute=True,deafen=True)

    @commands.cooldown(1,1,commands.BucketType.channel)
    async def wiki(self,ctx,*,query):
        data = GenericCommandParameters(ctx)
        query = query.replace(" ","_")
        info = requests.get("http://thetaleofgreatcosmos.fr/wiki/api.php?action=parse&page="+query+"&format=json&redirects=true")
        exist_test = requests.get("http://thetaleofgreatcosmos.fr/wiki/index.php?title="+query)
        if exist_test.status_code != 200:
            yield from client.send_message(ctx.message.channel,data.lang["wiki_unexisting"].format(str(exist_test.status_code)))
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
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        if len(info.json()["parse"]["redirects"]) != 0:
            embd.add_field(name=lang["wiki_redirect"],value=info.json()["parse"]["redirects"][0]["from"],inline=True)
        await ctx.message.channel.send(embed=embd)

    @commands.command(aliases=['jointtgc','ttgc'])
    async def jointhegame(self,ctx):
        inv = await self.bot.get_channel(326648561976737792).create_invite(max_age=3600)
        await ctx.message.channel.send("Rejoignez le serveur officiel The Tale of Great Cosmos (serveur FR) : \n{}".format(str(inv.url)))

    @commands.group(invoke_without_command=False)
    async def jdr(self,ctx): pass

    @commands.check(check_mj)
    @commands.cooldown(1,60,commands.BucketType.user)
    @jdr.command(name="start",aliases=["create"])
    async def jdr_start(self,ctx,chan: discord.TextChannel):
        data = GenericCommandParameters(data)
        try:
            data.srv.getJDR(str(chan.id))
            await ctx.message.channel.send(data.lang["jdr_exist"].format(chan.mention))
        except:
            data.srv.jdrstart(str(chan.id),str(ctx.message.author.id))
            await ctx.message.channel.send(data.lang["jdr_start"].format(chan.mention,ctx.message.author.mention))

    @commands.check(check_admin)
    @commands.cooldown(1,60,commands.BucketType.user)
    @jdr.command(name="delete")
    async def jdr_delete(self,ctx,chan: discord.TextChannel):
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
            await ctx.message.channel.send(data.lang["jdr_delete"].format(chan.mention))

    @commands.check(check_admin)
    @commands.check(check_mj)
    @commands.cooldown(1,60,commands.BucketType.user)
    @jdr.command(name="copy")
    async def jdr_copy(self,ctx,src: discord.TextChannel, dest: discord.TextChannel):
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
                await ctx.message.channel.send(data.lang["jdrcopy"])

    @commands.check(check_admin)
    @commands.check(check_mj)
    @commands.cooldown(1,5,commands.BucketType.user)
    @jdr.command(name="extend")
    async def jdr_extend(self,ctx,src: discord.TextChannel, dest: discord.TextChannel):
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
                    srv.getJDR(str(dest.id)).delete()
                except: pass
                srv.getJDR(str(src.id)).extend(str(dest.id))
                await ctx.message.channel.send(data.lang["jdrextend"])

    @commands.check(check_admin)
    @commands.cooldown(1,5,commands.BucketType.user)
    @jdr.command(name="unextend")
    async def jdr_unextend(self,ctx,src: discord.TextChannel, dest: discord.TextChannel):
        data = GenericCommandParameters(ctx)
        if src.guild.id != ctx.message.guild.id or src.guild.id != dest.guild.id:
            await ctx.message.channel.send(data.lang["jdrcopy_serverror"])
        else:
            srv.getJDR(str(src.id)).unextend(str(dest.id))
            await ctx.message.channel.send(data.lang["jdrunextend"])

    @commands.check(check_admin)
    @commands.cooldown(1,5,commands.BucketType.user)
    @jdr.command(name="unextendall")
    async def jdr_unextendall(self,ctx,src: discord.TextChannel):
        data = GenericCommandParameters(ctx)
        srv.getJDR(str(src.id)).unextend_all()
        await ctx.message.channel.send(data.lang["jdrunextend"])
