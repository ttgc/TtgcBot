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

from ..cogs import BotManage, Utilities
from ..cogs.jdr import Jdr

# test cog - REMOVE before release
from ..cogs.tcog import TCog


@catch(AlreadyCalledFunctionException,
       logger=functools.partial(Log.critical, kill_code=ExitCode.UNREGISTERED_COGS),
       asynchronous=True)
@call_once(raise_error=True, asynchronous=True)
async def _add_cogs(client: commands.Bot) -> None:
    Log.debug_v4('Registering V4 cogs')
    await client.add_cog(BotManage(client))
    await client.add_cog(Utilities(client))
    await client.add_cog(Jdr(client))
    await client.add_cog(TCog(client))
    Log.debug_v4('End of registering V4 cogs')


async def _register_missed_servers(client: commands.Bot, registered_srv_list: list[ServerDTO]) -> None:
    Log.info('Looking for servers that joined during inactivity period...')
    current_srv = set(x.id for x in client.guilds)
    diff = current_srv.difference(set(x.id for x in registered_srv_list))

    if diff:
        Log.info('Found %d servers that joined during inactivity period', len(diff))
        for srv in diff:
            full_guild = client.get_guild(srv)
            Log.info('Registering server %s (%d)...', str(full_guild), srv)
            success = await ServerDTO(srv).join()

            if success:
                Log.info('Registered server %s (%d)', str(full_guild), srv)
            else:
                Log.warn('Unable to register server %s (%d)', str(full_guild), srv)
    else:
        Log.info('No new server to register found')


async def _unregister_missed_servers(client: commands.Bot, registered_srv_list: list[ServerDTO]) -> None:
    Log.info('Looking for servers that left during inactivity period...')
    current_srv = set(x.id for x in client.guilds)
    diff = set(x.id for x in registered_srv_list).difference(current_srv)

    if diff:
        Log.info('Found %d servers that left during inactivity period', len(diff))
        for srv in diff:
            Log.info('Unregistering server %d...', srv)
            success = await ServerDTO(srv).leave()

            if success:
                Log.info('Unregistered server %d', srv)
            else:
                Log.warn('Unable to unregister server %d', srv)
    else:
        Log.info('No new server to unregister found')


async def _handle_servers(client: commands.Bot) -> None:
    purged = await ServerDTO.purge(30)
    Log.info('Purged %d servers that left over than 30 days', purged)
    servers = await ServerDTO.get_server_list()
    await _unregister_missed_servers(client, servers)
    await _register_missed_servers(client, servers)


async def on_connect(client: commands.Bot) -> None:
    if len(client.cogs) > 0:
        return

    Log.info("Successful connected. Initializing bot system")
    await _add_cogs(client)
    InviteLink(client)

    if (test_guild := Config()['discord']['test-guild']):
        Log.debug_v4("Test guild provided. Copying global command to test guild.")
        client.tree.copy_global_to(guild=discord.Object(id=test_guild))

    await client.tree.sync()
    Log.debug_v4('on_connect first sync done')
    await _handle_servers(client)


async def on_resumed(client: commands.Bot) -> None:
    await _handle_servers(client)
    Log.info("Resumed session")
