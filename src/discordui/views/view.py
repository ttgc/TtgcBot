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

import discord.ui as ui
from discordui.views import ViewResult, DefaultViewResults

class View(ui.View):
    """Discord UI default view wrapper"""

    def __init__(self, ctx, *, check_callback=None, timeout=None, authorize_everyone=False):
        """
        View(ctx, *options)

        Parameters:
            ctx: command context object
            ----
            check_callback: callback function to determine whether an interaction should be answered or not (default: None)
            timeout: timeout in seconds after which the view will timeout and be closed. If None, the view will never timeout (default: None)
            authorize_everyone: should everyone be authorized to interact with view? (default: False)

        Callback def:
            def check_callback(ctx: discord.ext.commands.Context, interaction: discord.Interaction) -> bool
        """
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.check_callback = None
        self.authorize_everyone = authorize_everyone
        self._timeout_callback = None
        self._result = DefaultViewResults.NONE

    async def interaction_check(self, interaction):
        """
        Override interaction_check from base class
        Triggered when someone interacts with the view

        params:
            interaction: the selection interaction that triggered the callback

        returns:
            bool: wheter or not the interaction will be processed
        """
        author_check = self.authorize_everyone or interaction.user == self.ctx.author
        custom_check = self.check_callback is None or self.check_callback(self.ctx, self.interaction)
        return author_check and custom_check

    @property
    def timeout_callback(self):
        """Get timeout callback"""
        return self._timeout_callback if self.timeout is not None else None

    @timeout_callback.setter
    def timeout_callback(self, callback):
        """
        Set timeout callback
        Callback def: async def timeout_callback(self: View) -> None
        """
        if self.timeout is not None:
            self._timeout_callback = callback

    @property
    def result(self):
        """Get view result"""
        return self._result

    @result.setter
    def result(self, value):
        """
        Set view result
        value should be either ViewResult, DefaultViewResults or int
        """
        if isinstance(value, ViewResult):
            self._result = value
        elif isinstance(value, DefaultViewResults):
            self._result = value.value
        elif isinstance(value, int):
            self._result = ViewResult(value)
        else:
            raise TypeError(f"view result must be a ViewResult, DefaultViewResults or int but not {type(value)}")

    async def on_timeout(self):
        """
        Override on_timeout from base class
        Triggered when the view has timed out
        """
        if self.timeout_callback is not None:
            await self.timeout_callback(self)
        await super().on_timeout()
