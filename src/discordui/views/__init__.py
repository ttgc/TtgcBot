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
discordui.views sub-package:
    A short wrapper for discord.ui views of discord.py lib

Contains:
    View: Discord UI default view wrapper
    ViewResult: Wrapper to determines a view's result
    DefaultViewResults: Enumeration for default view's results
    ButtonGroup: A standardized view for grouping multiple action buttons
    Modal: Discord UI modal view wrapper
"""

from discordui.views.viewresult import ViewResult, DefaultViewResults
from discordui.views.view import View
from discordui.views.modal import Modal
from discordui.views.buttongroup import ButtonGroup
