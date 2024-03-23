#!usr/bin/env python3
#-*-coding:utf-8-*-

##    TtgcBot - a bot for discord
##    Copyright (C) 2017-2024  Thomas PIOT
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


from typing import Optional
from enum import StrEnum
import asyncio
from discord.ext import commands
from models import MemberDTO, ServerDTO, JdrDTO
from lang import Language


class ContextExtension:
    class _QueryableMembers(StrEnum):
        MEMBER = 'member'
        SERVER = 'server'
        JDR = 'jdr'

    def __init__(self, ctx: commands.Context) -> None:
        self._member = MemberDTO(ctx.author.id)
        self._server = ServerDTO(ctx.guild.id) # type: ignore
        self._jdr = JdrDTO(self._server.id, ctx.channel.id)
        self._tasks: dict[str, asyncio.Task] = {}

    def prepare(self) -> None:
        if not self._tasks:
            self._tasks[self._QueryableMembers.MEMBER] = asyncio.create_task(self._member.fetch())
            self._tasks[self._QueryableMembers.SERVER] = asyncio.create_task(self._server.fetch())
            self._tasks[self._QueryableMembers.JDR] = asyncio.create_task(self._jdr.fetch())

    async def _get_query_task[T](self, attr: _QueryableMembers) -> Optional[T]: # type: ignore
        if attr not in self._tasks:
            self.prepare()

        if not self._tasks[attr].done():
            res = await self._tasks[attr]

        return getattr(self, f'_{attr}') if res is not None else None

    @property
    def member(self) -> asyncio.Task[Optional[MemberDTO]]:
        return asyncio.create_task(
            self._get_query_task(self._QueryableMembers.MEMBER)
        )

    async def get_lang(self) -> Language:
        member = await self.member
        return member.lang if member else Language.get_default()

    @property
    def server(self) -> asyncio.Task[Optional[ServerDTO]]:
        return asyncio.create_task(
            self._get_query_task(self._QueryableMembers.SERVER)
        )

    @property
    def jdr(self) -> asyncio.Task[Optional[JdrDTO]]:
        return asyncio.create_task(
            self._get_query_task(self._QueryableMembers.JDR)
        )


class ExtendedContext(commands.Context):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.ext = ContextExtension(self)


def prepare_ctx(cmd: commands.Command) -> commands.Command:

    @cmd.before_invoke
    async def _before_cmd_invoke(cog: commands.Cog, ctx: ExtendedContext) -> None:
        ctx.ext.prepare()

    return cmd
