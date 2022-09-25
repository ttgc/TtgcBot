#!usr/bin/env python3
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

# import discord
from utils.translator import get_lang, lang_exist

class GenericCommandParameters:
    def __new__(cl, ctx, min_query=False):
        if not hasattr(ctx, 'data') or ctx.data is None:
            ctx.data = super().__new__(cl)
        return ctx.data

    def __init__(self, ctx, min_query=False):
        self._populated = False
        self.ID = ctx.message.id
        # self.srv = await DBServer(ctx.message.guild.id)
        # role = discord.utils.get(ctx.author.roles, id=srv.mjrole)
        # if role is None: role = discord.utils.get(ctx.author.roles, id=srv.adminrole)
        lgcode = "EN" #await DBMember.getuserlang(ctx.message.author.id)
        self.lang = get_lang(lgcode if lang_exist(lgcode) else "EN")
        self.jdr = None
        self.charlist = None
        self.charbase = None
        self.char = None
        # self.jdrlist = await self.srv.jdrlist(ctx.author.id, role.id if role is not None else None)
        # jdrchannel = await check_jdrchannel(ctx)
        # if jdrchannel:
        #     self.jdr = await self.srv.getJDR(ctx.message.channel.id, ctx.author.id, role.id if role is not None else None)
        #     self.charbase = await self.jdr.charlist()
        #     for i in self.charbase.get("linked", []):
        #         if i.get("member", -1) == ctx.message.author.id and i.get("selected", False):
        #             self.char = await self.jdr.get_character(i.get("charkey", ""))
        #             break

    async def populate(self, ctx):
        if not self._populated:
            self._populated = True

    @classmethod
    async def get_from_context(cls, ctx):
        data = cls(ctx)
        await data.populate(ctx)
        return data
