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


from typing import Self, Optional, Type, Union, Callable, Awaitable, Any, override, TYPE_CHECKING
from dataclasses import dataclass
import discord
from discord import ui
from utils.aliases import AsyncCallable, UserType
from utils.emojis import Emoji
from lang import ILocalizable

from .button import button, Button
from .view import LayoutView

if TYPE_CHECKING:
    from ...common.contextext import ExtendedContext


@dataclass(frozen=True, kw_only=True, eq=False)
class Media:
    file: str | discord.File | discord.UnfurledMediaItem
    description: Optional[str] = None
    spoiler: bool = False

    def __eq__(self, value: Self) -> bool:
        return self.file == value.file

    def __ne__(self, value: Self) -> bool:
        return not self.__eq__(value)

    def edit(self, *, description: Optional[str] = None, spoiler: Optional[bool] = None) -> Self:
        descr = description if description is not None else self.description
        return Media(
            file=self.file,
            description=descr if descr is not '' else None,
            spoiler=spoiler if spoiler is not None else self.spoiler,
        )

    def to_discord_type(self) -> discord.MediaGalleryItem:
        return discord.MediaGalleryItem(
            self.file,
            description=self.description,
            spoiler=self.spoiler
        )

    @classmethod
    def from_attachment(
        cls,
        name: str, *,
        description: Optional[str] = None,
        spoiler: bool = False
    ) -> Self:
        return cls(file=f'attachment://{name}', description=description, spoiler=spoiler)


class MediaGallery(ui.MediaGallery):
    def __init__(
        self,
        *items: Media,
        id: Optional[int] = None,
    ) -> None:
        super().__init__(*[x.to_discord_type() for x in items], id=id)

    def __add__(self, item: Media) -> Self:
        self.add_item(item.to_discord_type())
        return self

    def __iadd__(self, item: Media) -> Self:
        self.add_item(item.to_discord_type())
        return self

    def __sub__(self, item: Media) -> Self:
        self.remove_item(item.to_discord_type())
        return self

    def __isub__(self, item: Media) -> Self:
        self.remove_item(item.to_discord_type())
        return self

    def insert(self, index: int, item: Media) -> None:
        self.insert_item_at(index, media=item.file, description=item.description, spoiler=item.spoiler)
