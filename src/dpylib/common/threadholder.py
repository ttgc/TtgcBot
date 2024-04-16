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


from enum import IntEnum
from typing import Optional
import discord
from utils.aliases import JdrChannelThreads


class ThreadArchiveDuration(IntEnum):
    MIN = 60
    DAY = 1440
    THREE_DAYS = 4320
    WEEK = 10080


class DiscordThreadHolder[T: JdrChannelThreads]:
    def __init__(
            self,
            src_channel: T, *,
            thread_only: bool = False,
            auto_archive: bool = True,
            auto_lock: bool = True,
            private: bool = True,
            auto_archive_duration: ThreadArchiveDuration = ThreadArchiveDuration.MIN
    ) -> None:
        self.src = src_channel
        self.thread_only = thread_only
        self.auto_archive = auto_archive
        self.auto_lock = auto_lock
        self.private = private
        self.auto_archive_duration = auto_archive_duration
        self.dest: JdrChannelThreads = self.src

    @property
    def needs_message(self) -> bool:
        return not self.private and isinstance(self.src, discord.TextChannel)

    @property
    def needs_post(self) -> bool:
        return isinstance(self.src, discord.ForumChannel)

    @property
    def channel(self) -> Optional[discord.Thread | discord.VoiceChannel]:
        return self.dest if isinstance(self.dest, discord.Thread) or isinstance(self.dest, discord.VoiceChannel) else None

    async def spawn(
            self,
            thread_name: str, *,
            origin_msg: Optional[discord.Message] = None,
            post_content: str = '',
            **post_params
    ) -> discord.Thread | discord.VoiceChannel:
        if isinstance(self.src, discord.TextChannel):
            if self.needs_message and origin_msg:
                msg = await self.src.fetch_message(origin_msg.id)
                self.dest = await msg.create_thread(
                    name=thread_name,
                    auto_archive_duration=self.auto_archive_duration # type: ignore
                )
            else:
                self.dest = await self.src.create_thread(
                    name=thread_name,
                    auto_archive_duration=self.auto_archive_duration, # type: ignore
                    type=discord.ChannelType.private_thread if self.private else discord.ChannelType.public_thread,
                    invitable=False
                )
        elif isinstance(self.src, discord.Thread):
            await self.src.edit(archived=False, locked=False)
        elif isinstance(self.src, discord.ForumChannel) and origin_msg:
            self.dest, _ = await self.src.create_thread(
                name=thread_name,
                auto_archive_duration=self.auto_archive_duration, # type: ignore
                content=post_content,
                **post_params
            )
        elif not isinstance(self.src, discord.VoiceChannel) or self.thread_only:
            raise Exception('TEMP') # TODO: proper exception

        if not self.channel:
            raise Exception('TEMP') # TODO: proper exception

        return self.channel

    async def close(self) -> None:
        if isinstance(self.dest, discord.Thread):
            await self.dest.edit(archived=self.auto_archive, locked=self.auto_lock)
