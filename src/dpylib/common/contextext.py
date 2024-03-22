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


from enum import StrEnum
import asyncio
from discord.ext import commands
from models import MemberDTO


class ContextExtension:
    class _QueryableMembers(StrEnum):
        MEMBER = 'member'

    def __init__(self, ctx: commands.Context) -> None:
        self._member = MemberDTO(ctx.author.id)
        self._tasks: dict[str, asyncio.Task] = {}

    def prepare(self) -> None:
        if not self._tasks:
            self._tasks[self._QueryableMembers.MEMBER] = asyncio.create_task(self._member.fetch())

    async def _get_query_task[T](self, attr: _QueryableMembers) -> T: # type: ignore
        if attr not in self._tasks:
            self.prepare()

        if not self._tasks[attr].done():
            await self._tasks[attr]

        return getattr(self, f'_{attr}')

    @property
    def member(self) -> asyncio.Task[MemberDTO]:
        return asyncio.create_task(
            self._get_query_task(self._QueryableMembers.MEMBER)
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
