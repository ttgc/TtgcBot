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
import os,time

class Finalize(commands.Cog, name="Finalize (RP/JDR)"):
    def __init__(self,bot,logger):
        self.bot = bot
        self.logger = logger

    async def _finalizing_vocalstart(self,ctx,data):
        self.logger.log(logging.DEBUG+1,"[finalize] _finalizing_vocalstart begin (%d, %d)",ctx.message.channel.id,ctx.message.guild.id)
        vsys = self.bot.get_cog("Vocal").vocalcore
        vc = vsys.getvocal(str(ctx.message.guild.id))
        if vc is not None and vc.vocal and os.access("Music/never_give_up_tsfh.mp3",os.F_OK):
            playable = True
            if len(vc.queue) > 0: await ctx.message.channel.send(data.lang["finalize_notemptyqueue"])
            startTimer = time.clock()
            while len(vc.queue) > 0:
                curTimer = time.clock()-startTimer
                if curTimer > 10:
                    await ctx.message.channel.send(data.lang["finalize_emptyqueue_timeout"])
                    playable = False
                    break
                await vc.skip(True)
            if playable: await vc.append("Music/never_give_up_tsfh.mp3",yt=False,no_output=True)
        self.logger.log(logging.DEBUG+1,"[finalize] _finalizing_vocalstart end (%d, %d)",ctx.message.channel.id,ctx.message.guild.id)
        return vsys,vc

    def _finalizing_generateinfo(self,ctx,data):
        def sum_ls(ls1,ls2):
            lsf = ls1[:]
            for i in range(len(lsf)):
                lsf[i] += ls2[i]
            return lsf

        self.logger.log(logging.DEBUG+1,"[finalize] _finalizing_generateinfo begin (%d, %d)",ctx.message.channel.id,ctx.message.guild.id)
        msg = [("The Tale of Great Cosmos","Created by Ttgc\nAn original adventure in the world of Terae and the multiverse")]
        msg += [("Game Master (GM) :",str(discord.utils.get(ctx.message.guild.members,id=int(data.jdr.mj))))]
        ct = ""
        ctdead = ""
        luck = []
        unluck = []
        rolled = []
        gstat = [0,0,0,0,0,0,0]
        for i in data.charbase:
            gstat = sum_ls(gstat,i.stat)
            rolled.append(i.stat[0])
            luck.append(100*((2*i.stat[1])+i.stat[2])/max(i.stat[0],1))
            unluck.append(100*((2*i.stat[-1])+i.stat[-2])/max(i.stat[0],1))
            if i.dead:
                ctdead += "{}\n".format(i.name)
            elif i.linked is not None:
                ct += "{} as {}\n".format(str(discord.utils.get(ctx.message.guild.members,id=str(i.linked))),i.name)
        if ctdead == "": ctdead = "No player dead"
        lucky = data.charbase[luck.index(max(luck))]
        ctlucky = lucky.name
        if lucky.linked is not None: ctlucky += " ({})".format(str(discord.utils.get(ctx.message.guild.members,id=int(lucky.linked))))
        unlucky = data.charbase[unluck.index(max(unluck))]
        ctunlucky = unlucky.name
        if unlucky.linked is not None: ctunlucky += " ({})".format(str(discord.utils.get(ctx.message.guild.members,id=int(unlucky.linked))))
        mostroll = data.charbase[rolled.index(max(rolled))]
        ctmostroll = mostroll.name
        if mostroll.linked is not None: ctmostroll += " ({})".format(str(discord.utils.get(ctx.message.guild.members,id=int(mostroll.linked))))
        msg += [("Players (PC) :",ct),
                ("Deads Players during the adventure :",ctdead),
                ("Most Lucky PC :",ctlucky),
                ("Most Unlucky PC :",ctunlucky),
                ("Most dice rolled PC :",ctmostroll),
                ("Global statistics :","{} dices rolled\n{} super critic success\n{} super critic fails\n{} critic success\n{} critic fails\n{} success (without critic)\n{} fails (without critic)".format(gstat[0],gstat[1],gstat[-1],gstat[2],gstat[-2],gstat[3],gstat[-3]))]
        for i in data.charbase:
            msg += [("{} statistics".format(i.name),
                    "{} dices rolled\n{} super critic success\n{} super critic fails\n{} critic success\n{} critic fails\n{} success (without critic)\n{} fails (without critic)".format(i.stat[0],i.stat[1],i.stat[-1],i.stat[2],i.stat[-2],i.stat[3],i.stat[-3]))]
        msg += data.jdr.get_finalizer()
        msg += [("The Tale of Great Cosmos","Find more information on the official website/wiki\nJoin the community on the official discord"),
                ("The Tale of Great Cosmos","Thank you for playing The Tale of Great Cosmos\nA chapter is closing, a new one is opening\nSee you soon in a new adventure")]
        self.logger.log(logging.DEBUG+1,"[finalize] _finalizing_generateinfo end (%d, %d)",ctx.message.channel.id,ctx.message.guild.id)
        return msg

    async def _finalizing_sendinfo(self,ctx,msg):
        self.logger.log(logging.DEBUG+1,"[finalize] _finalizing_sendinfo begin (%d, %d)",ctx.message.channel.id,ctx.message.guild.id)
        for i in msg:
            titl = i[0]
            cont = i[1]
            embd = discord.Embed(title=titl,description=cont,colour=discord.Color(int("5B005B",16)))
            embd.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.avatar_url)
            embd.set_footer(text=time.asctime())
            await ctx.message.channel.send(embed=embd)
            await asyncio.sleep(10)
        self.logger.log(logging.DEBUG+1,"[finalize] _finalizing_sendinfo end (%d, %d)",ctx.message.channel.id,ctx.message.guild.id)

    async def _finalizing_sendthanks(self,ctx,data):
        self.logger.log(logging.DEBUG+1,"[finalize] _finalizing_sendthanks begin (%d, %d)",ctx.message.channel.id,ctx.message.guild.id)
        thanksmsg = await ctx.message.channel.send("Thanks for playing **The Tale of Great Cosmos** !")
        try:
            await thanksmsg.add_reaction("\U0001F4AF")
            await thanksmsg.add_reaction("\U0001F51A")
            await thanksmsg.add_reaction("\U0001F1EA")
            await thanksmsg.add_reaction("\U0001F1F3")
            await thanksmsg.add_reaction("\U0001F1E9")
        except discord.Forbidden: pass
        await ctx.message.channel.send(data.lang["finalize_end"])
        self.logger.log(logging.DEBUG+1,"[finalize] _finalizing_sendthanks end (%d, %d)",ctx.message.channel.id,ctx.message.guild.id)

    async def _finalizing_operation(self,ctx,data):
        self.logger.log(logging.DEBUG+1,"[finalize] _finalizing_operation begin (%d, %d)",ctx.message.channel.id,ctx.message.guild.id)
        await ctx.message.channel.send(data.lang["finalize_start"])
        vsys,vc = await self._finalizing_vocalstart(ctx,data)
        await asyncio.sleep(2)
        embd = discord.Embed(title="The Tale of Great Cosmos",colour=discord.Color(int("5B005B",16)))
        embd.set_image(url="https://cdn.discordapp.com/attachments/254997041858478080/317324181542928395/The_Tale_of_Great_Cosmos.png")
        embd.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.avatar_url)
        embd.set_footer(text=time.asctime())
        await ctx.message.channel.send(embed=embd)
        await asyncio.sleep(5)
        msg = self._finalizing_generateinfo(ctx,data)
        await self._finalizing_sendinfo(ctx,msg)
        await self._finalizing_sendthanks(ctx,data)
        data.jdr.delete()
        self.logger.log(logging.DEBUG+1,"[finalize] _finalizing_operation end (%d, %d)",ctx.message.channel.id,ctx.message.guild.id)

    @commands.check(check_chanmj)
    @commands.group(invoke_without_command=True)
    async def finalize(self,ctx):
        """**GM/MJ only**
        This action conclude a RP/JDR. When using it, all data related to it will be deleted, some fun statistics will be shown and credits will be displaying.
        If you have activated vocal before this command, the bot will also play the credits song
        Current song : 'Never Give Up On Your Dreams' by Two Steps From Hell
        All rights for the music go to their owners"""
        data = GenericCommandParameters(ctx)
        await ctx.message.channel.send(data.lang["finalize"])
        chk = lambda m: m.author == ctx.message.author and m.channel == ctx.message.channel and m.content.lower() == 'confirm finalize'
        try: answer = await self.bot.wait_for('message',check=chk,timeout=60)
        except asyncio.TimeoutError: answer = None
        if answer is None:
            await ctx.message.channel.send(data.lang["finalize_timeout"])
        else:
            self.logger.log(logging.DEBUG+1,"begin finalize in %d channel of %d server",ctx.message.channel.id,ctx.message.guild.id)
            await self._finalizing_operation(ctx,data)
            self.logger.log(logging.DEBUG+1,"end of finalize in %d channel of %d server",ctx.message.channel.id,ctx.message.guild.id)

    @commands.check(check_chanmj)
    @finalize.command(name="set")
    async def finalize_set(self,ctx,*,title):
        """**GM/MJ only**
        Set a credit field for the finalize command."""
        data = GenericCommandParameters(ctx)
        await ctx.message.channel.send(data.lang["set_finalizer_ask"].format(title))
        chk = lambda m: m.author == ctx.message.author and m.channel == ctx.message.channel
        try: ct = await self.bot.wait_for('message',check=chk,timeout=120)
        except asyncio.TimeoutError: ct = None
        if ct is None:
            await ctx.message.channel.send(data.lang["timeout"])
        else:
            data.jdr.set_finalizer_field(title,ct)
            self.logger.log(logging.DEBUG+1,"add finalize field %s in %d channel of %d server",title,ctx.message.channel.id,ctx.message.guild.id)
            await ctx.message.channel.send(data.lang["finalizer_add"].format(title,ct.content))

    @commands.check(check_chanmj)
    @finalize.command(name="delete",aliases=["del","-","remove","rm"])
    async def finalize_delete(self,ctx,*,title):
        """**GM/MJ only**
        remove a credit field from the finalize command."""
        data = GenericCommandParameters(ctx)
        data.jdr.del_finalizer_field(title)
        self.logger.log(logging.DEBUG+1,"remove finalize field %s in %d channel of %d server",title,ctx.message.channel.id,ctx.message.guild.id)
        await ctx.message.channel.send(data.lang["finalizer_del"].format(title))
