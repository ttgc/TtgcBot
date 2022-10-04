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

class Modal(ui.Modal):
    """Discord UI modal view wrapper"""

    def __init__(self, ctx, title, *, check_callback=None, timeout=None, id=None, onsubmit=None):
        """
        Modal(ctx, title, *options)

        Parameters:
            ctx: command context object
            title: the modal title
            ----
            check_callback: callback function to determine whether an interaction should be answered or not (default: None)
            timeout: timeout in seconds after which the view will timeout and be closed. If None, the view will never timeout (default: None)
            id: the modal id
            onsubmit: callback function to call when the modal is closed and submitted

        Callback def:
            def check_callback(ctx: discord.ext.commands.Context, interaction: discord.Interaction) -> bool
            async def onsubmit(self: Dropdown, interaction: discord.Interaction) -> None
        """
        super().__init__(title=title, timeout=timeout, custom_id=id if id is not None else title)
        self.ctx = ctx
        self.check_callback = None
        self._timeout_callback = None
        self._onsubmit = onsubmit

    async def interaction_check(self, interaction):
        """
        Override interaction_check from base class
        Triggered when someone interacts with the view

        params:
            interaction: the selection interaction that triggered the callback

        returns:
            bool: wheter or not the interaction will be processed
        """
        return interaction.user == self.ctx.author and (self.check_callback is None or self.check_callback(self.ctx, self.interaction))

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
    def onsubmit(self):
        """Get onsubmit callback"""
        return self._onsubmit

    @onsubmit.setter
    def onsubmit(self, callback):
        """
        Set onsubmit callback
        Callback def: async def onsubmit(self: Dropdown, interaction: discord.Interaction) -> None
        """
        if self.onsubmit is not None:
            self._onsubmit = callback

    async def on_submit(self, interaction, /):
        """
        Override on_submit from base class
        Triggered when the modal is submitted

        params:
            interaction: the selection interaction that triggered the callback
        """
        await super().on_submit(interaction)
        if self.onsubmit is not None:
            await self.onsubmit(self, interaction)
        else:
            await interaction.response.defer()
        self.stop()

    async def on_timeout(self):
        """
        Override on_timeout from base class
        Triggered when the view has timed out
        """
        if self.timeout_callback is not None:
            await self.timeout_callback(self)
        await super().on_timeout()
