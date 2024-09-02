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


import functools
import discord
from discord.ext import commands
from config import Config, Log
from utils.decorators import call_once, catch
from utils.exceptions import AlreadyCalledFunctionException
from utils import ExitCode
from models import ServerDTO
from ..common.invite import InviteLink


async def on_guild_join(client: commands.Bot, guild: discord.Guild) -> None:
    Log.info('Guild %s (%d) joined. Registering it...', str(guild), guild.id)
    success = await ServerDTO(guild.id).join()

    if success:
        Log.info('Guild %s (%d) registerd', str(guild), guild.id)
    else:
        Log.warn('Unable to register guild %s (%d)', str(guild), guild.id)


async def on_guild_removed(client: commands.Bot, guild: discord.Guild) -> None:
    Log.info('Guild %s (%d) removed. Unregistering it...', str(guild), guild.id)
    success = await ServerDTO(guild.id).leave()

    if success:
        Log.info('Guild %s (%d) unregisterd', str(guild), guild.id)
    else:
        Log.error('Unable to unregister guild %s (%d)', str(guild), guild.id)
