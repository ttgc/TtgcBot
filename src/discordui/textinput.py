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

class TextInput(discord.ui.TextInput):
    """Discord UI TextInput Widget"""

    def __init__(self, ctx, view, label, *, style=discord.TextStyle.short, id=None, placeholder=None, default=None, required=True, minlen=None, maxlen=None, row=None):
        """
        TextInput(ctx, view, label, *options)

        Parameters:
            ctx: command context object
            view: discord ui modal view object where the textinput will be displayed
            label: label used by the textinput
            ----
            style: textinput style (default: discord.TextStyle.short)
            id: textinput id. If None, the id will be automatically generated (default: None)
            placeholder: the placeholder to display in the textinput when nothing is typed (default: None)
            default: default text value to insert in the textinput on display (default: None)
            required: whether the textinput is required or not (default: True)
            minlen: the minimum length for the text typed in to be considered as valid. Use None for no minimum (default: None)
            maxlen: the maximum length for the text typed in to be considered as valid. Use None for no maximum (default: None)
            row: the row where to display the button inside the view. Should be between 0 and 4 included. If None, the display will be automatically adjusted (default: None)
        """
        if id is not None:
            super().__init__(label=label, style=style, custom_id=id, placeholder=placeholder, default=default, required=required, min_length=minlen, max_length=maxlen, row=row)
        else:
            super().__init__(label=label, style=style, placeholder=placeholder, default=default, required=required, min_length=minlen, max_length=maxlen, row=row)

        view.add_item(self)
        self._view = view

    @property
    def view(self):
        """Get the view where the textinput belongs to"""
        return self._view
