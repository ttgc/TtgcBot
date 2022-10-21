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

import discord
from discordui.views import View, DefaultViewResults

class Dropdown(discord.ui.Select):
    """Discord UI Select/Dropdown Widget"""

    def __init__(self, ctx, view, *, id=None, placeholder=None, minval=1, maxval=1, disabled=False, row=None, onselection=None, options=[], **kargs):
        """
        Dropdown(ctx, view, *options)

        Parameters:
            ctx: command context object
            view: discord ui view object where the button will be displayed
            ----
            id: dropdown id. If None, the id will be automatically generated (default: None)
            placeholder: the placeholder to display in the dropdown when no item is selected (default: None)
            minval: the minimum value to select in the dropdown (default: 1)
            maxval: the maximum value that can be selected at the same time in the dropdown (default: 1)
            disabled: whether the dropdown should be disabled (default: False)
            row: the row where to display the dropdown inside the view. Should be between 0 and 4 included. If None, the display will be automatically adjusted (default: None)
            onselection: async callback called on item selection (default: None)
            options: list of dropdown's options to display (default: [])
            **kargs: list of dropdown's options to display. When passed as kwargs the option will be displayed as the karg's value and the returned value will be the kwarg's key

        Callback def:
            async def onselection(self: Dropdown, interaction: discord.Interaction) -> None
        """
        self.ctx = ctx
        opt = [discord.SelectOption(label=i) for i in options]
        opt += [discord.SelectOption(label=k, value=i) for i, k in kargs.items()]
        if id is not None:
            super().__init__(custom_id=id, placeholder=placeholder, min_values=minval, max_values=maxval, options=opt, disabled=disabled, row=row)
        else:
            super().__init__(placeholder=placeholder, min_values=minval, max_values=maxval, options=opt, disabled=disabled, row=row)
        view.add_item(self)
        self._view = view
        self._onselection = onselection

    def __iadd__(self, item):
        """
        Add an item to the dropdown
        Added item should be either a discord.ui.SelectOption or a stringiifiable object
        """
        if isinstance(item, discord.ui.SelectOption):
            self.append_option(item)
        else:
            self.add_option(label=str(item))

        return self

    @property
    def view(self):
        """Get the view where the dropdown belongs to"""
        return self._view

    @property
    def value(self):
        """Get the first selected value. Usefull when minval and maxval are set to 1"""
        return self.values[0] if len(self.values) > 0 else None

    @property
    def onselection(self):
        """Get onselection callback"""
        return self._onselection

    @onselection.setter
    def onselection(self, value):
        """
        Set onselection callback
        Callback def: async def onselection(self: Dropdown, interaction: discord.Interaction) -> None
        """
        self._onselection = value

    async def callback(self, interaction):
        """
        Override callback from base class
        Triggered when an item in the dropdown is selected

        params:
            interaction: the selection interaction that triggered the callback
        """
        if self.onselection is not None:
            await self.onselection(self, interaction)
        else:
            await interaction.response.defer()

    def add_multiple_options(self, *args, **kwargs):
        """
        Add multiple options to the dropdown
        *args are added through += operator while **kwargs are added through add_option method
        When passed as **kwargs option will be displayed as the kwarg's value and the returned value will be the kwarg's key
        """
        for i in args:
            self += i
        for i, k in kwargs.items():
            self.add_option(label=k, value=i)


class StandaloneDropdown(Dropdown):
    """Shortcut class to easily creates view with a single dropdown in it"""

    def __init__(self, ctx, *, id=None, placeholder=None, minval=1, maxval=1, disabled=False, row=None, onselection=None, check_callback=None, timeout=None, options=[], **kargs):
        """
        StandaloneDropdown(ctx, *options)

        Parameters:
            ctx: command context object
            ----
            id: dropdown id. If None, the id will be automatically generated (default: None)
            placeholder: the placeholder to display in the dropdown when no item is selected (default: None)
            minval: the minimum value to select in the dropdown (default: 1)
            maxval: the maximum value that can be selected at the same time in the dropdown (default: 1)
            disabled: whether the dropdown should be disabled (default: False)
            row: the row where to display the dropdown inside the view. Should be between 0 and 4 included. If None, the display will be automatically adjusted (default: None)
            onselection: async callback called on item selection (default: None)
            check_callback: view check callback for interactions received (default: None)
            timeout: view's timeout (default: None)
            options: list of dropdown's options to display (default: [])
            **kargs: list of dropdown's options to display. When passed as kwargs the option will be displayed as the karg's value and the returned value will be the kwarg's key

        Callback defs:
            async def onselection(self: Dropdown, interaction: discord.Interaction) -> None
            def check_callback(ctx: discord.ext.commands.Context, interaction: discord.Interaction) -> bool
        """

        view = View(ctx, check_callback=check_callback, timeout=timeout)
        super().__init__(ctx, view, id=id, placeholder=placeholder, minval=minval, maxval=maxval, disabled=disabled, row=row, onselection=onselection, options=options, **kargs)

    async def wait(self):
        """Wait until an interaction is received and answered"""
        result = await self.view.wait()
        return result

    async def callback(self, interaction):
        """
        Override callback from base class
        Triggered when an item in the dropdown is selected

        params:
            interaction: the selection interaction that triggered the callback
        """
        await super().callback(interaction)
        self.view.stop()


async def send_dropdown(ctx, *, placeholder=None, check_callback=None, timeout=None, options=[], select_msg="{}", timeout_msg="timeout", format_msg=True, format_args_before=[], format_args_after=[]):
    """
    send_dropdown(ctx, *options) -> bool, string
    Create a StandaloneDropdown, display it, respond to the user interaction and return.
    Shortcut for creating easily dropdowns with single selection and standard response to interactions

    Parameters:
        ctx: command context object
        ----
        placeholder: the placeholder to display in the dropdown when no item is selected (default: None)
        check_callback: view check callback for interactions received (default: None)
        timeout: view's timeout (default: None)
        options: list or dict of dropdown's options to display (default: [])
        select_msg: the message to display when an item is selected (default: '{}')
        timeout_msg: the message to display when the view has timeout (default: 'timeout')
        format_msg: whether to format or not the select_msg string with at least the selected value (default: True)
        format_args_before: the list of arguments to insert in the select_msg string before the selected value (default: [])
        format_args_after: the list of arguments to insert in the select_msg string after the selected value (default: [])

    returns:
        bool: whether (or not) the view has not timeout and succeeded
        string: the selected option in the dropdown (or None if no option where selected)
    """
    async def _on_select(dropdown, interaction):
        final_select_msg = select_msg

        if format_msg:
            format_args = format_args_before + [dropdown.value] + format_args_after
            final_select_msg = select_msg.format(*format_args)

        await interaction.response.edit_message(content=final_select_msg, view=None)
        dropdown.view.result = DefaultViewResults.SUBMIT

    timeout, selection = await send_dropdown_custom_submit(ctx, placeholder=placeholder, check_callback=check_callback, timeout=timeout, options=options, on_submit=_on_select, timeout_msg=timeout_msg)
    return timeout, selection


async def send_dropdown_custom_submit(ctx, *, placeholder=None, check_callback=None, timeout=None, options=[], on_submit=None, timeout_msg="timeout"):
    """
    send_dropdown(ctx, *options) -> bool, string
    Create a StandaloneDropdown, display it, respond to the user interaction and return.
    Shortcut for creating easily dropdowns with single selection and standard response to interactions

    Parameters:
        ctx: command context object
        ----
        placeholder: the placeholder to display in the dropdown when no item is selected (default: None)
        check_callback: view check callback for interactions received (default: None)
        timeout: view's timeout (default: None)
        options: list or dict of dropdown's options to display (default: [])
        on_submit: submit (selection) callback (default: None)
        timeout_msg: the message to display when the view has timeout (default: 'timeout')

    returns:
        bool: whether (or not) the view has not timeout and succeeded
        string: the selected option in the dropdown (or None if no option where selected)

    Callback def:
        async def on_submit(self: Dropdown, interaction: discord.Interaction) -> None
    """
    dropdown = StandaloneDropdown(ctx, placeholder=placeholder, check_callback=check_callback, timeout=timeout, onselection=on_submit)
    if isinstance(options, dict):
        dropdown.add_multiple_options(**options)
    else:
        dropdown.add_multiple_options(*options)

    msg = await ctx.send(view=dropdown.view, reference=ctx.message)
    timeout = await dropdown.wait()

    if timeout:
        await msg.edit(content=timeout_msg, view=None)

    return not timeout and dropdown.view.result.is_success, dropdown.value
