#!usr/bin/env python3
#-*-coding:utf-8-*-

##    TtgcBot - a bot for discord
##    Copyright (C) 2017-2026  Thomas PIOT
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


from typing import TYPE_CHECKING, Any, Optional, Type, override
import discord
from lang import LocalizedStr, LocalizeStrCase, localize
from utils.emojis import Emoji
from utils.aliases import UserType
from models import fetch_extensions, BaseExtensions, BaseRaces, BaseClasses
from dices import DiceCombinator, Dice
from ..common.embed import DiscordEmbedMeta, EmbedAuthorMeta, EmbedFieldMeta
from ..common.threadholder import DiscordThreadHolder
from ..ui.components import Dropdown, DropdownOption, View, Button, Modal, TextInput, button, dropdown, modal
from ..ui.embed import EmbedView, EmbedBrowserSelectorView
from .iworkflow import IWorkflow, setup_view


if TYPE_CHECKING:
    from ..common.contextext import ExtendedContext


class InventoryWorkflow(IWorkflow[None]): # TODO: Change return type
    class ViewID(IWorkflow.ViewID):
        BROWSING = 'browsing'
        USE_ITEM = 'use'

    def __init__(self, ctx: 'ExtendedContext') -> None:
        super().__init__()
        self.ctx = ctx
        self.character = None # TODO: ctx.character
