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


import asyncio
import discord
import discord.ext.commands
from utils.decorators import call_once, catch
from config import Config
from .common.contextext import ExtendedContext

from .events.connect import on_connect as on_connect_internal
from .events.connect import on_resumed as on_resumed_internal


class Bot(discord.ext.commands.Bot):
    async def get_context(self, message, *, cls=ExtendedContext) -> ExtendedContext:
        return await super().get_context(message, cls=cls)


@call_once()
def get_client() -> Bot:
    client = Bot(
        Config()['discord']['default-prefix'],
        case_insensitive=True,
        activity=discord.Game(name=Config()['discord']['default-game']),
        intents=discord.Intents.all()
    )

    client.wait_for = catch(asyncio.TimeoutError, error_value=None, asynchronous=True)(client.wait_for)
    return client


_client = get_client()


@_client.check
def no_dm(ctx: discord.ext.commands.Context) -> bool:
    return ctx.guild is not None


@_client.check
def no_bot(ctx: discord.ext.commands.Context) -> bool:
    return not ctx.author.bot


@_client.event
async def on_connect():
    await on_connect_internal(get_client())


@_client.event
async def on_resumed():
    await on_resumed_internal()


@_client.before_invoke
async def before_invoke(ctx: discord.ext.commands.Context) -> None:
    await ctx.defer()


del _client
