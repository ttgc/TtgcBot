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
from src.tools.Translator import *

class Moderation(commands.Cog):
    def __init__(self,bot,logger):
        self.bot = bot
        self.logger = logger

    @commands.check(check_admin)
    @commands.cooldown(1,30,commands.BucketType.guild)
    @commands.command(aliases=['prefix'])
    async def setprefix(self,ctx,pref):
        data = GenericCommandParameters(ctx)
        data.srv.setprefix(pref)
        self.logger.info("Changing command prefix on server %s into '%s'",str(ctx.message.guild.id),pref)
        await ctx.message.channel.send(data.lang["setprefix"].format(pref))

    @commands.check(check_admin)
    @commands.cooldown(1,60,commands.BucketType.guild)
    @commands.command(aliases=['adminrole'])
    async def setadminrole(self,ctx,role: discord.Role):
        data = GenericCommandParameters(ctx)
        data.srv.setadminrole(str(role.id))
        self.logger.info("Changing adminrole on server %s",str(ctx.message.guild.id))
        await ctx.message.channel.send(data.lang["setadmin"].format(role.mention))

    @commands.check(check_admin)
    @commands.command()
    async def contentban(self,ctx,ctban):
        data = GenericCommandParameters(ctx)
        if len(data.srv.wordblocklist()) < 20 or check_premium(ctx):
            if ctban.startswith(ctx.prefix):
                await ctx.message.channel.send(data.lang["contentban_prefix"])
            else:
                data.srv.blockword(ctban)
                self.logger.info("'%s' banned on server %s",ctban,str(ctx.message.guild.id))
                await ctx.message.channel.send(data.lang["contentban"].format(ctban))
        else:
            await ctx.message.channel.send(data.lang["contentban_limit"])

    @commands.check(check_admin)
    @commands.command()
    async def contentunban(self,ctx,ctban):
        data = GenericCommandParameters(ctx)
        data.srv.unblockword(ctban)
        self.logger.info("'%s' unbanned on server %s",ctban,str(ctx.message.guild.id))
        await ctx.message.channel.send(data.lang["contentunban"].format(ctban))

    @commands.check(check_admin)
    @commands.bot_has_permissions(manage_roles=True,ban_members=True,kick_members=True)
    @commands.command()
    async def warn(self,ctx,members: commands.Greedy[discord.Member],*,reason):
        data = GenericCommandParameters(ctx)
        embd = discord.Embed(title="WARN",description=reason,colour=discord.Color(int('ff0000',16)))
        embd.set_footer(text=str(ctx.message.created_at))
        embd.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.avatar_url)
        embd.set_thumbnail(url="https://www.ggte.unicamp.br/ea/img/iconalerta.png")
        cfg = data.srv.get_warnconfig()
        for memb in members:
            data.srv.warnuser(str(memb.id))
            self.logger.info("Member %s warned on server %s",str(memb.id),str(ctx.message.guild.id))
            try: nbr = data.srv.get_warnnbr(DBMember(str(memb.id)))
            except: nbr = 0
            punish = data.lang["none"]
            for k in cfg:
                if nbr > k[0]:
                    lgcodetarget = getuserlang(str(ctx.message.author.id))
                    if not lang_exist(lgcodetarget): lgcodetarget = "EN"
                    langtarget = get_lang(lgcodetarget)
                    if k[1] == "kick":
                        await memb.kick(reason="Too many warnings")
                        punish = data.lang["warn_kick"].format(memb.mention)
                        self.logger.info("Member %s was kicked from %s due to high warn number",str(memb.id),str(ctx.message.guild.id))
                        await memb.send(langtarget["warn_kick_user"].format(ctx.message.guild.name))
                    elif k[1] == "ban":
                        await memb.ban(reason="Too many warnings",delete_message_days=0)
                        punish = data.lang["warn_ban"].format(memb.mention)
                        self.logger.info("Member %s was banned from %s due to high warn number",str(memb.id),str(ctx.message.guild.id))
                        await memb.send(langtarget["warn_ban_user"].format(ctx.message.guild.name))
                    else:
                        rl = None
                        for j in ctx.message.guild.roles:
                            if str(j.id) == k[1]:
                                rl = j
                                break
                        if rl is not None:
                            await memb.add_roles(rl,reason="Too many warnings")
                            punish = data.lang["warn_assign"].format(i.mention,rl.mention)
                            self.logger.info("Member %s has got role %s on server %s due to high warn number",str(memb.id),str(rl.id),str(ctx.message.guild.id))
                    break
            embd.add_field(name=str(memb),value="Total warn : {}\n{} : {}".format(nbr,data.lang['punish'],punish))
        await ctx.message.channel.send(embed=embd)

    @commands.check(check_admin)
    @commands.command()
    async def unwarn(self,ctx,members: commands.Greedy[discord.Member]):
        data = GenericCommandParameters(ctx)
        embd = discord.Embed(title="UNWARN",colour=discord.Color(int('00ff00',16)))
        embd.set_footer(text=str(ctx.message.created_at))
        embd.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.avatar_url)
        embd.set_thumbnail(url="https://cdn1.iconfinder.com/data/icons/interface-elements/32/accept-circle-512.png")
        for memb in members:
            data.srv.unwarnuser(str(memb.id))
            self.logger.info("Member %s warned on server %s",str(memb.id),str(ctx.message.guild.id))
            try: nbr = data.srv.get_warnnbr(DBMember(str(memb.id)))
            except: nbr = 0
            embd.add_field(name=str(memb),value="Total warn : {}".format(nbr),inline=True)
        await ctx.message.channel.send(embed=embd)

    @commands.check(check_admin)
    @commands.command()
    async def configwarn(self,ctx,value: int,sanction,rl: typing.Optional[discord.Role]):
        data = GenericCommandParameters(ctx)
        if sanction.lower() == "assign" and rl is not None:
            data.srv.warnconfig(value,str(rl.id))
            await ctx.message.channel.send(data.lang["cfgwarn_assign"].format(rl.mention,str(value)))
            sanction += " {}".format(rl.id)
        elif sanction.lower() == "kick":
            data.srv.warnconfig(value,"kick")
            await ctx.message.channel.send(data.lang["cfgwarn_kick"].format(str(value)))
        elif sanction.lower() == "ban":
            data.srv.warnconfig(value,"ban")
            await ctx.message.channel.send(data.lang["cfgwarn_ban"].format(str(value)))
        elif sanction.lower() == "remove":
            data.srv.warnconfig(value,"disable")
            await ctx.message.channel.send(data.lang["cfgwarn_none"].format(str(value)))
        else:
            await ctx.message.channel.send(data.lang["cfgwarn_unknown"])
        self.logger.info("set configwarn %s for %d warnings on server %s",sanction,value,str(ctx.message.guild.id))

    @commands.check(check_admin)
    @commands.command(aliases=['warnls'])
    async def warnlist(self,ctx):
        data = GenericCommandParameters(ctx)
        ls = data.srv.get_warned()
        embd = discord.Embed(title="Warned list",description=data.lang["warnlist"],colour=discord.Color(int('ff0000',16)))
        embd.set_footer(text=str(ctx.message.created_at))
        embd.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.avatar_url)
        for i in ls:
            user = await self.bot.fetch_user(int(i[0]))
            embd.add_field(name=str(user)+" :",value=str(i[1])+" warning(s)",inline=True)
        await ctx.message.channel.send(embed=embd)

    @commands.check(check_admin)
    @commands.command(aliases=['warnconfigls','warncfgls','warncfglist'])
    async def warnconfiglist(self,ctx):
        data = GenericCommandParameters(ctx)
        ls = data.srv.get_warnconfig()
        embd = discord.Embed(title=data.lang["punishlist"],description=data.lang["warncfglist"],colour=discord.Color(int('ff0000',16)))
        embd.set_footer(text=str(ctx.message.created_at))
        embd.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.avatar_url)
        for i in ls:
            if i[1] == "kick":
                sanction = "Kick"
            elif i[1] == "ban":
                sanction = "Ban"
            else:
                sanction = data.lang["warncfglist_assign"].format(discord.utils.get(ctx.message.guild.roles,id=int(i[1])).mention)
            embd.add_field(name=str(i[0])+" warnings :",value=sanction,inline=True)
        await ctx.message.channel.send(embed=embd)

    @commands.check(check_admin)
    @commands.command()
    async def userblock(self,ctx,usr):
        data = GenericCommandParameters(ctx)
        data.srv.blockusername(usr)
        self.logger.info("username %s blocked on server %s",usr,str(ctx.message.guild.id))
        await ctx.message.channel.send(data.lang["userblock"].format(usr))

    @commands.check(check_admin)
    @commands.command()
    async def userunblock(self,ctx,usr):
        data = GenericCommandParameters(ctx)
        if not data.srv.unblockusername(usr):
            await ctx.message.channel.send(data.lang["userunblock_notexist"].format(usr))
        else:
            self.logger.info("username %s unblocked on server %s",usr,str(ctx.message.guild.id))
            await ctx.message.channel.send(data.lang["userunblock"].format(usr))
