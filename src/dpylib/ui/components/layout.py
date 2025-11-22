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
import discord
from discord import ui
from utils.aliases import AsyncCallable, UserType
from utils.emojis import Emoji
from lang import ILocalizable

from .button import button, Button
from .view import LayoutView

if TYPE_CHECKING:
    from ...common.contextext import ExtendedContext


class LayoutSection(ui.Section, ILocalizable[None]):
    def __init__(
        self,
        *children: Union[ui.Item, str],
        accessory: ui.Item,
        id: Optional[int] = None,
    ) -> None:
        super().__init__(*children, accessory=accessory, id=id)

    def __len__(self) -> int:
        return self.content_length()

    def __add__(self, item: ui.Item) -> Self:
        self.add_item(item)
        return self

    def __iadd__(self, item: ui.Item) -> Self:
        self.add_item(item)
        return self

    def __sub__(self, item: ui.Item) -> Self:
        self.remove_item(item)
        return self

    def __isub__(self, item: ui.Item) -> Self:
        self.remove_item(item)
        return self

    def find_item_by_custom_id(self, custom_id: str) -> Optional[ui.Item]:
        for child in self.walk_children():
            if hasattr(child, 'custom_id') and child.custom_id == custom_id:
                return child
        return None

    @override
    def find_item(self, id: int | str) -> Optional[ui.Item]:
        if isinstance(id, int):
            return super().find_item(id)
        elif isinstance(id, str):
            return self.find_item_by_custom_id(id)
        return None

    @override
    async def localize(self, ctx: 'ExtendedContext', *args, **kwargs) -> None:
        for child in self.walk_children():
            if isinstance(child, ILocalizable):
                await child.localize(ctx, *args, **kwargs)


class LayoutActionSection(ui.ActionRow, ILocalizable[None]):
    def __init__(
        self,
        *children: ui.Item,
        id: Optional[int] = None,
    ) -> None:
        super().__init__(*children, id=id)

    def __len__(self) -> int:
        return self.content_length()

    def __add__(self, item: ui.Item) -> Self:
        self.add_item(item)
        return self

    def __iadd__(self, item: ui.Item) -> Self:
        self.add_item(item)
        return self

    def __sub__(self, item: ui.Item) -> Self:
        self.remove_item(item)
        return self

    def __isub__(self, item: ui.Item) -> Self:
        self.remove_item(item)
        return self

    def find_item_by_custom_id(self, custom_id: str) -> Optional[ui.Item]:
        for child in self.walk_children():
            if hasattr(child, 'custom_id') and child.custom_id == custom_id:
                return child
        return None

    @override
    def find_item(self, id: int | str) -> Optional[ui.Item]:
        if isinstance(id, int):
            return super().find_item(id)
        elif isinstance(id, str):
            return self.find_item_by_custom_id(id)
        return None

    @override
    async def localize(self, ctx: 'ExtendedContext', *args, **kwargs) -> None:
        for child in self.walk_children():
            if isinstance(child, ILocalizable):
                await child.localize(ctx, *args, **kwargs)

    @override
    def button(
        self,
        *,
        label: Optional[str] = None,
        custom_id: Optional[str] = None,
        disabled: bool = False,
        style: discord.ButtonStyle = discord.ButtonStyle.secondary,
        emoji: Optional[Emoji] = None,
        id: Optional[int] = None,
    ) -> Callable[[AsyncCallable[Any]], Callable[..., Button]]:
        return button(
            style=style,
            label=label,
            custom_id=custom_id,
            disabled=disabled,
            emoji=emoji,
            id=id
        )


class LayoutBuilder:
    def __init__(
        self, *,
        timeout: Optional[float] = None,
        owner: Optional[UserType] = None,
        checks: list[Callable[[Self, discord.Interaction], bool]] = None, # type: ignore
        on_timeout: Optional[Callable[[Self], Awaitable[None]]] = None,
        on_error: Optional[Callable[[Self, discord.Interaction, Exception, ui.Item], Awaitable[None]]] = None
    ) -> None:
        self.view = LayoutView(
            timeout=timeout,
            owner=owner,
            checks=checks,
            on_timeout=on_timeout,
            on_error=on_error
        )
        self.current_id = 0

    async def __call__(self, ctx: 'ExtendedContext', *args, **kwargs) -> LayoutView:
        await self.view.localize(ctx, *args, **kwargs)
        return self.view

    def add_section(self) -> int:
        self.view.add_item(LayoutSection(id=self.current_id))
        self.current_id += 1
        return self.current_id - 1

    def add_action_section(self) -> int:
        self.view.add_item(LayoutActionSection(id=self.current_id))
        self.current_id += 1
        return self.current_id - 1

    def add_separator(self, spacing: discord.SeparatorSpacing = discord.SeparatorSpacing.small) -> int:
        self.view.add_item(ui.Separator(spacing=spacing, id=self.current_id))
        self.current_id += 1
        return self.current_id - 1

    def __getitem__(self, id: int) -> Optional[ui.Item]:
        return self.view.find_item(id)

    def add_component_to(self, section_id: int, component: ui.Item) -> int:
        if not (section := self.view[section_id]) or not isinstance(section, (LayoutSection, LayoutActionSection)):
            raise ValueError(f'Section with ID {section_id} does not exist or is not a LayoutSection/LayoutActionSection')

        component.id = self.current_id
        self.current_id += 1
        section.add_item(component)
        return self.current_id - 1

    def get_section(self, section_id: int, *, match_cls: Optional[Type[LayoutSection | LayoutActionSection | ui.Separator]] = None) -> LayoutSection | LayoutActionSection | ui.Separator:
        if not (section := self.view[section_id]):
            raise ValueError(f'Section with ID {section_id} does not exist')
        if not isinstance(section, (LayoutSection, LayoutActionSection, ui.Separator)):
            raise ValueError(f'Componenet with ID {section_id} is not a section or separator')
        if match_cls and not isinstance(section, match_cls):
            raise ValueError(f'Section with ID {section_id} is not matching type {match_cls.__name__}')
        return section
