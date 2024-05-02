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


import discord
from discord.ext import commands
from config import Config, Log, Environment


def get_default_perms() -> discord.Permissions:
    perms = discord.Permissions.none()
    perms.add_reactions = True
    perms.attach_files = True
    perms.change_nickname = True
    perms.create_instant_invite = True
    perms.create_private_threads = True
    perms.create_public_threads = True
    perms.deafen_members = True
    perms.embed_links = True
    perms.manage_messages = True
    perms.manage_nicknames = True
    perms.manage_threads = True
    perms.mention_everyone = True
    perms.mute_members = True
    perms.read_message_history = True
    perms.read_messages = True
    perms.send_messages = True
    perms.send_messages_in_threads = True
    perms.send_tts_messages = True
    perms.use_application_commands = True
    return perms


class InviteLink:
    def __init__(
            self,
            client: commands.Bot, *,
            perms: discord.Permissions = get_default_perms(),
            dev_bypass: bool = True
    ) -> None:
        if dev_bypass and Config().env == Environment.DEV:
            perms = discord.Permissions.all()

        if not client.user:
            Log.error('Cannot get client ID. Invite link generation aborted')
            raise ValueError('') # TODO: better exception

        self.perms = perms
        self.url = discord.utils.oauth_url(client.user.id, permissions=perms)
        Log.info("Generated invite link : %s", self)

    def __str__(self) -> str:
        return self.url
