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
import logging,asyncio,time
import discord
import typing
from src.Translator import *

class Other(commands.Cog):
    def __init__(self,bot,logger):
        self.bot = bot
        self.logger = logger

    @commands.cooldown(1,30,BucketType.user)
    @commands.command()
    async def ping(self,ctx):
        data = GenericCommandParameters(ctx)
        tps_start = time.clock()
        await ctx.message.channel.send(":ping_pong: pong ! :ping_pong:")
        tps_end = time.clock()
        ping = round((tps_end-tps_start)*1000)
        await ctx.message.channel.send(data.lang["ping"].format(ping))
        self.logger.log(logging.DEBUG+1,"current ping : %d ms",ping)

    @commands.cooldown(1,60,commands.BucketType.user)
    @commands.command(aliases=['setlanguage'])
    async def setlang(self,ctx,lg):
        if lang_exist(lg):
            oldlg = getuserlang(str(ctx.message.author.id))
            setuserlang(str(ctx.message.author.id),lg)
            await ctx.message.channel.send(get_lang(lg)["setlang"].format(lg))
            self.logger.info("user %s switched lang from %s to %s",str(ctx.message.author.id),oldlg,lg)
        else:
            data = GenericCommandParameters(ctx)
            await ctx.message.channel.send(data.lang["setlang_notexist"].format(lg))

    @commands.command(aliases=['invit'])
    async def invite(self,ctx):
        data = GenericCommandParameters(ctx)
        botaskperm = discord.Permissions().all()
        botaskperm.administrator = botaskperm.manage_channels = botaskperm.manage_guild = botaskperm.manage_webhooks = botaskperm.manage_emojis = botaskperm.manage_nicknames = botaskperm.move_members = False
        url = discord.utils.oauth_url(str(client.user.id),botaskperm)
        embd = discord.Embed(title="TtgcBot",description=lang["invite"],colour=discord.Color(randint(0,int('ffffff',16))),url=url)
        embd.set_footer(text=lang["invite_author"],icon_url=client.user.avatar_url)
        embd.set_image(url=client.user.avatar_url)
        embd.set_author(name="Ttgc",icon_url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2018/08/avatar-2-perso.png",url=url)
        embd.set_thumbnail(url="http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2017/06/cropped-The_Tale_of_Great_Cosmos.png")
        embd.add_field(name=lang["invite_srv"],value=str(len(client.guilds))+" servers",inline=True)
        await ctx.message.channel.send(embed=embd)
        self.logger.info("Invite generated on channel %d from server %d by %d",ctx.message.channel.id,ctx.message.guild.id,ctx.message.author.id)

    @commands.cooldown(1,30,commands.BucketType.channel)
    @commands.command()
    async def yay(self,ctx):
        f = open("pictures/YAY.png","rb")
        await ctx.message.channel.send("YAY !",file=discord.File(f))
        f.close()

    @commands.cooldown(1,30,commands.BucketType.channel)
    @commands.command()
    async def choquedecu(self,ctx):
        f = open("pictures/choquedecu.png","rb")
        await ctx.message.channel.send("#choquedecu",file=discord.File(f))
        f.close()

    @commands.cooldown(1,30,commands.BucketType.channel)
    @commands.command()
    async def onichan(self,ctx):
        f = open("pictures/onichan.jpg","rb")
        await ctx.message.channel.send(file=discord.File(f))
        f.close()

    @commands.cooldown(1,30,commands.BucketType.channel)
    @commands.command()
    async def pi(self,ctx):
        await ctx.message.channel.send("3,141 592 653 589 793 238 462 643 383 279 502 884 197 169 399 375 105 820 974 944 592 307 816 406 286 208 998 628 034 825 342 117 0679...\nhttp://www.nombrepi.com/")

    @commands.cooldown(7,30,commands.BucketType.channel)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.command()
    async def tell(self,ctx,*,msg):
        self.logger.info("%s (%d) said on channel %d from server %d through /tell : %s",ctx.message.author,ctx.message.author.id,ctx.message.channel.id,ctx.message.guild.id,msg)
        await ctx.message.channel.send(msg)
        await ctx.message.delete()

    @commands.cooldown(3,30,commands.BucketType.channel)
    @commands.bot_has_permissions(manage_messages=True,send_tts_messages=True)
    @commands.command(aliases=['telltts'])
    async def ttstell(self,ctx,*,msg):
        self.logger.info("%s (%d) said on channel %d from server %d through /ttstell : %s",ctx.message.author,ctx.message.author.id,ctx.message.channel.id,ctx.message.guild.id,msg)
        await ctx.message.channel.send(msg,tts=True)
        await ctx.message.delete()

    # @commands.check(check_admin)
    # @commands.cooldown(1,30,commands.BucketType.default)
    # @commands.command(aliases=['prefix'])
    # async def setprefix(self,ctx,pref):
    #     data = GenericCommandParameters(ctx)
    #     data.srv.setprefix(pref)
    #     self.logger.info("Changing command prefix on server %s into '%s'",str(ctx.message.guild.id),pref)
    #     await ctx.message.channel.send(data.lang["setprefix"].format(pref))
    #
    # @commands.check(check_admin)
    # @commands.cooldown(1,60,commands.commands.BucketType.default)
    # @commands.command(aliases=['adminrole'])
    # async def setadminrole(self,ctx,role: discord.Role):
    #     data = GenericCommandParameters(ctx)
    #     data.srv.setadminrole(str(role.id))
    #     self.logger.info("Changing adminrole on server %s",str(ctx.message.guild.id))
    #     await ctx.message.channel.send(data.lang["setadmin"].format(role.mention))
    #
    # @commands.check(check_admin)
    # @commands.command()
    # async def contentban(self,ctx,ctban):
    #     data = GenericCommandParameters(ctx)
    #     if len(data.srv.wordblocklist()) < 20 or check_premium(ctx):
    #         if ctban.startswith(ctx.prefix):
    #             await ctx.message.channel.send(data.lang["contentban_prefix"])
    #         else:
    #             data.srv.blockword(ctban)
    #             self.logger.info("'%s' banned on server %s",ctban,str(ctx.message.guild.id))
    #             await ctx.message.channel.send(data.lang["contentban"].format(ctban))
    #     else:
    #         await ctx.message.channel.send(data.lang["contentban_limit"])
    #
    # @commands.check(check_admin)
    # @commands.command()
    # async def contentunban(self,ctx,ctban):
    #     data = GenericCommandParameters(ctx)
    #     data.srv.unblockword(ctban)
    #     self.logger.info("'%s' unbanned on server %s",ctban,str(ctx.message.guild.id))
    #     await ctx.message.channel.send(data.lang["contentunban"].format(ctban))
    #
    # @commands.check(check_admin)
    # @commands.bot_has_permissions(manage_roles=True,ban_members=True,kick_members=True)
    # @commands.command()
    # async def warn(self,ctx,members: commands.Greedy[discord.Member],*,reason):
    #     data = GenericCommandParameters(ctx)
    #     embd = discord.Embed(title="WARN",description=reason,colour=discord.Color(int('ff0000',16)))
    #     embd.set_footer(text=str(ctx.message.created_at))
    #     embd.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.avatar_url)
    #     embd.set_thumbnail(url="https://www.ggte.unicamp.br/ea/img/iconalerta.png")
    #     cfg = data.srv.get_warnconfig()
    #     for memb in members:
    #         data.srv.warnuser(str(memb.id))
    #         self.logger.info("Member %s warned on server %s",str(memb.id),str(ctx.message.guild.id))
    #         try: nbr = data.srv.get_warnnbr(DBMember(str(memb.id)))
    #         except: nbr = 0
    #         punish = data.lang["none"]
    #         for k in cfg:
    #             if nbr > k[0]:
    #                 lgcodetarget = getuserlang(str(ctx.message.author.id))
    #                 if not lang_exist(lgcodetarget): lgcodetarget = "EN"
    #                 langtarget = get_lang(lgcodetarget)
    #                 if k[1] == "kick":
    #                     await memb.kick(reason="Too many warnings")
    #                     punish = data.lang["warn_kick"].format(memb.mention)
    #                     self.logger.info("Member %s was kicked from %s due to high warn number",str(memb.id),str(ctx.message.guild.id))
    #                     await memb.send(langtarget["warn_kick_user"].format(ctx.message.guild.name))
    #                 elif k[1] == "ban":
    #                     await memb.ban(reason="Too many warnings",delete_message_days=0)
    #                     punish = data.lang["warn_ban"].format(memb.mention)
    #                     self.logger.info("Member %s was banned from %s due to high warn number",str(memb.id),str(ctx.message.guild.id))
    #                     await memb.send(langtarget["warn_ban_user"].format(ctx.message.guild.name))
    #                 else:
    #                     rl = None
    #                     for j in ctx.message.guild.roles:
    #                         if str(j.id) == k[1]:
    #                             rl = j
    #                             break
    #                     if rl is not None:
    #                         await memb.add_roles(rl,reason="Too many warnings")
    #                         punish = data.lang["warn_assign"].format(i.mention,rl.mention)
    #                         self.logger.info("Member %s has got role %s on server %s due to high warn number",str(memb.id),str(rl.id),str(ctx.message.guild.id))
    #                 break
    #         embd.add_field(name=str(memb),value="Total warn : {}\n{} : {}".format(nbr,data.lang['punish'],punish))
    #     await ctx.message.channel.send(embed=embd)
    #
    # @commands.check(check_admin)
    # @commands.command()
    # async def unwarn(self,ctx,members: commands.Greedy[discord.Member]):
    #     data = GenericCommandParameters(ctx)
    #     embd = discord.Embed(title="UNWARN",colour=discord.Color(int('00ff00',16)))
    #     embd.set_footer(text=str(ctx.message.created_at))
    #     embd.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.avatar_url)
    #     embd.set_thumbnail(url="https://cdn1.iconfinder.com/data/icons/interface-elements/32/accept-circle-512.png")
    #     for memb in members:
    #         data.srv.unwarnuser(str(memb.id))
    #         self.logger.info("Member %s warned on server %s",str(memb.id),str(ctx.message.guild.id))
    #         try: nbr = data.srv.get_warnnbr(DBMember(str(memb.id)))
    #         except: nbr = 0
    #         embd.add_field(name=str(memb),value="Total warn : {}".format(nbr),inline=True)
    #     await ctx.message.channel.send(embed=embd)
    #
    # @commands.check(check_admin)
    # @commands.command()
    # async def configwarn(self,ctx,value: int,sanction,rl: typing.Optional[discord.Role]):
    #     data = GenericCommandParameters(ctx)
    #     if sanction.lower() == "assign" and rl is not None:
    #         data.srv.warnconfig(value,str(rl.id))
    #         await ctx.message.channel.send(data.lang["cfgwarn_assign"].format(rl.mention,str(value)))
    #         sanction += " {}".format(rl.id)
    #     elif sanction.lower() == "kick":
    #         data.srv.warnconfig(value,"kick")
    #         await ctx.message.channel.send(data.lang["cfgwarn_kick"].format(str(value)))
    #     elif sanction.lower() == "ban":
    #         data.srv.warnconfig(value,"ban")
    #         await ctx.message.channel.send(data.lang["cfgwarn_ban"].format(str(value)))
    #     elif sanction.lower() == "remove":
    #         data.srv.warnconfig(value,"disable")
    #         await ctx.message.channel.send(data.lang["cfgwarn_none"].format(str(value)))
    #     else:
    #         await ctx.message.channel.send(data.lang["cfgwarn_unknown"])
    #     self.logger.info("set configwarn %s for %d warnings on server %s",sanction,value,str(ctx.message.guild.id))
    #
    # @commands.check(check_admin)
    # @commands.command(aliases=['warnls'])
    # async def warnlist(self,ctx):
    #     data = GenericCommandParameters(ctx)
    #     ls = data.srv.get_warned()
    #     embd = discord.Embed(title="Warned list",description=data.lang["warnlist"],colour=discord.Color(int('ff0000',16)))
    #     embd.set_footer(text=str(ctx.message.created_at))
    #     embd.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.avatar_url)
    #     for i in ls:
    #         user = await self.bot.fetch_user(int(i[0]))
    #         embd.add_field(name=str(user)+" :",value=str(i[1])+" warning(s)",inline=True)
    #     await ctx.message.channel.send(embed=embd)
    #
    # @commands.check(check_admin)
    # @commands.command(aliases=['warnconfigls','warncfgls','warncfglist'])
    # async def warnconfiglist(self,ctx):
    #     data = GenericCommandParameters(ctx)
    #     ls = data.srv.get_warnconfig()
    #     embd = discord.Embed(title=data.lang["punishlist"],description=data.lang["warncfglist"],colour=discord.Color(int('ff0000',16)))
    #     embd.set_footer(text=str(ctx.message.created_at))
    #     embd.set_author(name=ctx.message.author.name,icon_url=ctx.message.author.avatar_url)
    #     for i in ls:
    #         if i[1] == "kick":
    #             sanction = "Kick"
    #         elif i[1] == "ban":
    #             sanction = "Ban"
    #         else:
    #             sanction = data.lang["warncfglist_assign"].format(discord.utils.get(ctx.message.guild.roles,id=int(i[1])).mention)
    #         embd.add_field(name=str(i[0])+" warnings :",value=sanction,inline=True)
    #     await ctx.message.channel.send(embed=embd)
    #
    # @commands.check(check_admin)
    # @commands.command()
    # async def userblock(self,ctx,usr):
    #     data = GenericCommandParameters(ctx)
    #     data.srv.blockusername(usr)
    #     self.logger.info("username %s blocked on server %s",usr,str(ctx.message.guild.id))
    #     await ctx.message.channel.send(data.lang["userblock"].format(usr))
    #
    # @commands.check(check_admin)
    # @commands.command()
    # async def userunblock(self,ctx,usr):
    #     data = GenericCommandParameters(ctx)
    #     if not data.srv.unblockusername(usr):
    #         await ctx.message.channel.send(data.lang["userunblock_notexist"].format(usr))
    #     else:
    #         self.logger.info("username %s unblocked on server %s",usr,str(ctx.message.guild.id))
    #         await ctx.message.channel.send(data.lang["userunblock"].format(usr))
