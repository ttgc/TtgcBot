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

"""
discordui package:
    A short wrapper for discord.ui module of discord.py lib

Contains:
    Button: Discord UI Button Widget
    DefaultButtons: Enumeration for standardized default Buttons
    Dropdown: Discord UI Select/Dropdown Widget
    StandaloneDropdown: Shortcut class to easily creates view with a single dropdown in it
    send_dropdown: Shortcut function to create a StandaloneDropdown, display it, respond to the user interaction and return
    TextInput: Discord UI TextInput Widget
    view: Subpackage containing view's logic
"""

from discordui.button import Button, DefaultButtons
from discordui.dropdown import Dropdown, StandaloneDropdown, send_dropdown, send_dropdown_custom_submit
from discordui.textinput import TextInput
