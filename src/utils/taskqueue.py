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

import asyncio

class TaskQueue:
    def __init__(self):
        self._queue = set()
        self._lock = asyncio.Lock()

    async def queue(self, coroutine, *, task_name=None):
        async with self._lock:
            index = len(self._queue)
            task = asyncio.create_task(coroutine(), name=task_name)
            self._queue.add(task)

    async def _get_task(self, task_name):
        async with self._lock:
            for task in self._queue:
                if task.get_name() == task_name:
                    return task
        return None

    async def is_pending(self, task_name):
        task = await self._get_task(task_name)
        return task is not None and not task.done() and not task.cancelled()

    async def wait_for(self, task_name, *, default_return_value=None):
        to_wait = await self._get_task(task_name)

        if to_wait is not None:
            if not to_wait.done() and not to_wait.cancelled():
                await to_wait
            return to_wait.result()
        return default_return_value
