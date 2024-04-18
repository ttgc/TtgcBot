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


from typing import TYPE_CHECKING
from discord.ext import commands
from utils.aliases import JdrChannelThreads

if TYPE_CHECKING:
    from ..workflow.iworkflow import IWorkflow


class DiscordLimitOverflowException(commands.CommandInvokeError):
    def __init__(self, limit: str, got: int, expected: int) -> None:
        self.limit = limit
        self.got = int(got)
        self.expected = int(expected)
        super().__init__(self)

    def __str__(self) -> str:
        return f'DiscordLimitOverflow: {self.limit} overflow. Got {self.got}. Expected {self.expected}'


class DiscordWorkflowException(commands.CommandInvokeError):
    def __init__(self, workflow: 'IWorkflow', msg: str) -> None:
        self.name = workflow.__class__.__name__
        self._instance = workflow
        self.msg = msg
        super().__init__(self)

    def __str__(self) -> str:
        return f'{self.__class__.__name__} on workflow {self.name}: {self.msg}'


class WorkflowAlreadyStartedException(DiscordWorkflowException):
    def __init__(self, workflow: 'IWorkflow') -> None:
        super().__init__(workflow, 'Workflow was already started and can only be started once')


class UnsupportedThread(commands.CommandInvokeError):
    def __init__(self, channel: JdrChannelThreads, msg: str) -> None:
        self.channel = channel
        self.msg = msg
        super().__init__(self)

    def __str__(self) -> str:
        return f'Unsupported channel #{self.channel.name} for threads: {self.msg}'
