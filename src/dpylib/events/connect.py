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
from config import Config, Log, Environment
from utils.decorators import call_once, catch
from utils.exceptions import AlreadyCalledFunctionException
from utils import ExitCode
from ..cogs import BotManage


@catch(AlreadyCalledFunctionException,
       logger=functools.partial(Log.critical, kill_code=ExitCode.UNREGISTERED_COGS),
       asynchronous=True)
@call_once(raise_error=True, asynchronous=True)
async def _add_cogs(client: commands.Bot) -> None:
    Log.debug_v4('Registering V4 cogs')
    await client.add_cog(BotManage(client))
    Log.debug_v4('End of registering V4 cogs')


def _generate_invite_link(client: commands.Bot) -> str:
    # TODO: move this under appropriate cog
    if Config().env == Environment.DEV:
        botaskperm = discord.Permissions.all()
    else:
        botaskperm = discord.Permissions().none()
        botaskperm.add_reactions = True
        botaskperm.attach_files = True
        botaskperm.change_nickname = True
        botaskperm.create_instant_invite = True
        botaskperm.create_private_threads = True
        botaskperm.create_public_threads = True
        botaskperm.deafen_members = True
        botaskperm.embed_links = True
        botaskperm.manage_messages = True
        botaskperm.manage_nicknames = True
        botaskperm.manage_threads = True
        botaskperm.mention_everyone = True
        botaskperm.mute_members = True
        botaskperm.read_message_history = True
        botaskperm.read_messages = True
        botaskperm.send_messages = True
        botaskperm.send_messages_in_threads = True
        botaskperm.send_tts_messages = True
        botaskperm.use_application_commands = True

    if not client.user:
        Log.error('Cannot get client ID. Invite link generation aborted')
        return ''

    url = discord.utils.oauth_url(client.user.id, permissions=botaskperm)
    Log.info("Generated invite link : %s", url)
    return url


async def on_connect(client: commands.Bot) -> None:
    if len(client.cogs) > 0:
        return

    Log.info("Successful connected. Initializing bot system")
    await _add_cogs(client)
    _generate_invite_link(client)

    if (test_guild := Config()['discord']['test-guild']):
        Log.debug_v4("Test guild provided. Copying global command to test guild.")
        client.tree.copy_global_to(guild=discord.Object(id=test_guild))

    await client.tree.sync()
    Log.debug_v4('on_connect first sync done')


async def on_resumed() -> None:
    Log.info("Resumed session")
