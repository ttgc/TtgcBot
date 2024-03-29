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
import typing
from random import randint,choice
from src.tools.Translator import *
from src.utils.config import *

class Other(commands.Cog):
    def __init__(self,bot,logger):
        self.bot = bot
        self.logger = logger

    @commands.cooldown(1,30,commands.BucketType.user)
    @commands.hybrid_command()
    async def ping(self,ctx):
        """~~Play ping-pong :ping_pong:~~
        Show the current ping of the bot"""
        data = GenericCommandParameters(ctx)
        ping = round(self.bot.latency * 1000)
        await ctx.send(data.lang["ping"].format(ping))
        self.logger.log(logging.DEBUG+1,"current ping : %d ms", ping)

    @commands.cooldown(1,60,commands.BucketType.user)
    @commands.hybrid_command(aliases=['setlanguage'])
    async def setlang(self,ctx,lg):
        """Define the language used by the bot for yourself
        the language chosen is used no matter on wich server you are.
        Currently only two language are available : `EN` and `FR`
        You can contribute to translation on GitHub : <https://ttgc.github.io/TtgcBot/>"""
        if lang_exist(lg):
            oldlg = getuserlang(str(ctx.message.author.id))
            setuserlang(str(ctx.message.author.id),lg)
            await ctx.send(get_lang(lg)["setlang"].format(lg))
            self.logger.info("user %s switched lang from %s to %s",str(ctx.message.author.id),oldlg,lg)
        else:
            data = GenericCommandParameters(ctx)
            await ctx.send(data.lang["setlang_notexist"].format(lg))

    @commands.hybrid_command(aliases=['invit'])
    async def invite(self,ctx):
        """Get the link to invite the bot on your server"""
        data = GenericCommandParameters(ctx)
        botaskperm = discord.Permissions().all()
        botaskperm.administrator = botaskperm.manage_channels = botaskperm.manage_guild = botaskperm.manage_webhooks = botaskperm.manage_emojis = botaskperm.manage_nicknames = botaskperm.move_members = False
        url = discord.utils.oauth_url(self.bot.user.id, permissions=botaskperm)
        embd = discord.Embed(title="TtgcBot",description=data.lang["invite"],colour=discord.Color(randint(0,int('ffffff',16))),url=url)
        embd.set_footer(text=data.lang["invite_author"].format(Config()["version"]),icon_url=self.bot.user.display_avatar.url)
        embd.set_image(url=self.bot.user.display_avatar.url)
        embd.set_author(name="Ttgc",icon_url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2018/08/avatar-2-perso.png",url=url)
        embd.set_thumbnail(url="https://www.thetaleofgreatcosmos.fr/wp-content/uploads/2019/11/TTGC_Text.png")
        embd.add_field(name=data.lang["invite_srv"],value=str(len(self.bot.guilds))+" servers",inline=True)
        await ctx.send(embed=embd)
        self.logger.info("Invite generated on channel %d from server %d by %d",ctx.message.channel.id,ctx.message.guild.id,ctx.message.author.id)

    @commands.cooldown(1,30,commands.BucketType.channel)
    @commands.hybrid_command()
    async def yay(self,ctx):
        """YAY !"""
        f = open("pictures/YAY.png","rb")
        await ctx.send("YAY !",file=discord.File(f))
        f.close()

    @commands.cooldown(1,30,commands.BucketType.channel)
    @commands.hybrid_command()
    async def choquedecu(self,ctx):
        """#ChoqueEtDecu"""
        f = open("pictures/choquedecu.png","rb")
        await ctx.send("#choquedecu",file=discord.File(f))
        f.close()

    @commands.cooldown(1,30,commands.BucketType.channel)
    @commands.hybrid_command()
    async def onichan(self,ctx):
        """Onichaaaaaaaaaaaaaaaaaan !"""
        f = open("pictures/onichan.jpg","rb")
        await ctx.send(file=discord.File(f))
        f.close()

    @commands.cooldown(1,30,commands.BucketType.channel)
    @commands.hybrid_command()
    async def pi(self,ctx):
        """3,14... do you know what are the next decimals ?"""
        await ctx.send("3,141 592 653 589 793 238 462 643 383 279 502 884 197 169 399 375 105 820 974 944 592 307 816 406 286 208 998 628 034 825 342 117 0679...\nhttp://www.nombrepi.com/")

    @commands.cooldown(7,30,commands.BucketType.channel)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.hybrid_command()
    async def tell(self,ctx,*,msg):
        """I can talk for you"""
        self.logger.info("%s (%d) said on channel %d from server %d through /tell : %s",ctx.message.author,ctx.message.author.id,ctx.message.channel.id,ctx.message.guild.id,msg)
        await ctx.send(msg)
        await ctx.message.delete()

    @commands.cooldown(3,30,commands.BucketType.channel)
    @commands.has_permissions(send_tts_messages=True)
    @commands.bot_has_permissions(manage_messages=True,send_tts_messages=True)
    @commands.hybrid_command(aliases=['telltts'])
    async def ttstell(self,ctx,*,msg):
        """**tts permission needed**
        I can really talk for you with the tts option !"""
        self.logger.info("%s (%d) said on channel %d from server %d through /ttstell : %s",ctx.message.author,ctx.message.author.id,ctx.message.channel.id,ctx.message.guild.id,msg)
        await ctx.send(msg,tts=True)
        await ctx.message.delete()

    # @commands.cooldown(5,30,commands.BucketType.channel)
    # @commands.cooldown(1,10,commands.BucketType.user)
    # @commands.command()
    # async def joke(self,ctx,lang: typing.Optional[str] = "FR"):
    #     """Funny jokes (only in french currently)"""
    #     if lang in ["FR", "EN"]:
    #         with open("{}/joke-{}.txt".format(Config()["directories"]["jokes"], lang),encoding="utf-8") as f:
    #             jokelist = f.readlines()
    #             if len(jokelist) > 0:
    #                 await ctx.message.channel.send(choice(jokelist).replace("\\n","\n"))
    #             else:
    #                 data = GenericCommandParameters(ctx)
    #                 await ctx.message.channel.send(data.lang["nojoke"].format(lang))
    #     else:
    #         data = GenericCommandParameters(ctx)
    #         await ctx.message.channel.send(data.lang["nojoke"].format(lang))
