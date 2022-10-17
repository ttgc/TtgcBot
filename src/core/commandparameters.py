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

import discord
from utils.translator import get_lang, lang_exist
from utils.checks import is_jdrchannel
from utils.taskqueue import TaskQueue
from models import DBMember, DBServer
from async_property import async_cached_property

class GenericCommandParameters:
    def __new__(cl, ctx, min_query=False):
        if not hasattr(ctx, 'data') or ctx.data is None:
            ctx.data = super().__new__(cl)
        return ctx.data

    def __init__(self, ctx, min_query=False):
        self._populated = False
        self.ID = ctx.message.id
        self.srv = None
        self.lang = None
        self._jdr = None
        self._charbase = None
        self._char = None
        self._jdrlist = None
        self._queue = TaskQueue()

    @async_cached_property
    async def jdr(self):
        if self._jdr is None:
            await self._queue.wait_for(f'{self.ID}-jdr')
        return self._jdr

    @async_cached_property
    async def charbase(self):
        if self._charbase is None:
            await self._queue.wait_for(f'{self.ID}-chars')
        return self._charbase

    @async_cached_property
    async def char(self):
        if self._char is None:
            await self._queue.wait_for(f'{self.ID}-chars')
        return self._char

    @async_cached_property
    async def jdrlist(self):
        if self._jdrlist is None:
            await self._queue.wait_for(f'{self.ID}-jdr')
        return self._jdrlist

    async def populate(self, ctx):
        async def _populate_jdr():
            async def _populate_characters():
                self._charbase = await self.jdr.charlist()
                for i in self._charbase.get("linked", []):
                    if i.get("member", -1) == ctx.author.id and i.get("selected", False):
                        self._char = await self.jdr.get_character(i.get("charkey", ""))
                        break

            role = discord.utils.get(ctx.author.roles, id=self.srv.mjrole)
            if role is None:
                role = discord.utils.get(ctx.author.roles, id=self.srv.adminrole)

            self._jdrlist = await self.srv.jdrlist(ctx.author.id, role.id if role is not None else None)
            if is_jdrchannel(self._jdrlist, ctx.channel.id):
                self._jdr = await self.srv.getJDR(ctx.channel.id, ctx.author.id, role.id if role is not None else None)
                await self._queue.queue(_populate_characters, task_name=f'{self.ID}-chars')

        if not self._populated:
            self.srv = await DBServer(ctx.guild.id)
            lgcode = await DBMember.getuserlang(ctx.author.id)
            self.lang = get_lang(lgcode if lang_exist(lgcode) else "EN")
            await self._queue.queue(_populate_jdr, task_name=f'{self.ID}-jdr')
            self._populated = True

    @classmethod
    async def get_from_context(cls, ctx):
        data = cls(ctx)
        await data.populate(ctx)
        return data
