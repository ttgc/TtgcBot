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


from typing import Optional, Self, override
from dataclasses import dataclass, field as datafield
from enum import IntEnum, auto
import discord
from dpylib.common.contextext import ExtendedContext
from utils import get_color, get_random_color
from lang import LocalizedStr, ILocalizable
from .exceptions import DiscordLimitOverflowException


class EmbedConversionPolicy(IntEnum):
    RAISE_ERROR = auto()
    TRUNCATE = auto()
    IGNORE_LIMITS = auto()


class EmbedLimits(IntEnum):
    FIELDS_COUNT = 25
    STANDARD_LENGTH = 256
    FIELD_CONTENT_LENGTH = 1024
    DESCRIPTION_LENGTH = 4096
    FOOTER_LENGTH = 2048


class LocalImageAttachment:
    def __init__(self, image_name: str, image_path: str) -> None:
        self._name = image_name
        self._path = image_path
        self._file = discord.File(fp=self.path, filename=self.name)

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value
        self._file.filename = value

    @property
    def path(self) -> str:
        return self._path

    @path.setter
    def path(self, value: str) -> None:
        self._path = value
        self._file = discord.File(fp=self.path, filename=self.name)

    @property
    def discord_file(self) -> discord.File:
        return self._file

    @property
    def attachment_link(self) -> str:
        return f'attachment://{self.name}'

    def __str__(self) -> str:
        return self.attachment_link


@dataclass
class EmbedIconTextMeta(ILocalizable[str]):
    text: str
    icon_url: str

    def __len__(self) -> int:
        return len(self.text)

    @override
    async def localize(self, ctx: ExtendedContext, *args, **kwargs) -> str:
        if isinstance(self.text, LocalizedStr):
            self.text = await self.text.localize(ctx, *args, **kwargs)
        return self.text


@dataclass
class EmbedAuthorMeta(ILocalizable[str]):
    name: str
    url: Optional[str] = None
    icon_url: Optional[str] = None

    def __len__(self) -> int:
        return len(self.name)

    @override
    async def localize(self, ctx: ExtendedContext, *args, **kwargs) -> str:
        if isinstance(self.name, LocalizedStr):
            self.name = await self.name.localize(ctx, *args, **kwargs)
        return self.name


@dataclass
class EmbedFieldMeta(ILocalizable[None]):
    name: str
    content: str
    inlined: bool = True

    def truncate(self) -> Self:
        name = f'{self.name[:EmbedLimits.STANDARD_LENGTH - 3]}...' if len(self.name) > EmbedLimits.STANDARD_LENGTH else self.name
        content = f'{self.content[:EmbedLimits.FIELD_CONTENT_LENGTH - 3]}...' \
            if len(self.content) > EmbedLimits.FIELD_CONTENT_LENGTH else self.content
        return self.__class__(name, content, self.inlined)

    @override
    async def localize(self, ctx: ExtendedContext, *args, **kwargs) -> None:
        if isinstance(self.name, LocalizedStr):
            self.name = await self.name.localize(ctx, *args, **kwargs)
        if isinstance(self.content, LocalizedStr):
            self.content = await self.content.localize(ctx, *args, **kwargs)


@dataclass
class DiscordEmbedMeta(ILocalizable[None]):
    title: str
    color: Optional[str] = None
    descr: Optional[str] = None
    link: Optional[str] = None
    img: Optional[str] = None
    thumbnail: Optional[str] = None
    author: Optional[str | EmbedAuthorMeta] = None
    footer: Optional[str | EmbedIconTextMeta] = None
    fields: list[EmbedFieldMeta] = datafield(default_factory=list)

    def __iadd__(self, field: EmbedFieldMeta) -> Self:
        self.fields.append(field)
        return self

    def add_fields(self, *fields: EmbedFieldMeta) -> Self:
        self.fields += list(fields)
        return self

    @property
    def max_field_title(self) -> int:
        return max([len(x.name) for x in self.fields])

    @property
    def max_field_content(self) -> int:
        return max([len(x.content) for x in self.fields])

    @property
    def has_too_many_fields(self) -> bool:
        return len(self.fields) > EmbedLimits.FIELDS_COUNT

    def get_error(self) -> Optional[DiscordLimitOverflowException]:
        """Returns if there is any issue with the embed (limit exceeded)"""
        if (val := len(self.fields)) > EmbedLimits.FIELDS_COUNT:
            return DiscordLimitOverflowException('Embed field count', val, EmbedLimits.FIELDS_COUNT)
        if (val := self.max_field_title) > EmbedLimits.STANDARD_LENGTH:
            return DiscordLimitOverflowException('Embed field title length', val, EmbedLimits.STANDARD_LENGTH)
        if (val := self.max_field_content) > EmbedLimits.FIELD_CONTENT_LENGTH:
            return DiscordLimitOverflowException('Embed field content length', val, EmbedLimits.FIELD_CONTENT_LENGTH)
        if (val := len(self.title)) > EmbedLimits.STANDARD_LENGTH:
            return DiscordLimitOverflowException('Embed title length', val, EmbedLimits.STANDARD_LENGTH)
        if self.descr and (val := len(self.descr)) > EmbedLimits.DESCRIPTION_LENGTH:
            return DiscordLimitOverflowException('Embed description length', val, EmbedLimits.DESCRIPTION_LENGTH)
        if self.author and (val := len(self.author)) > EmbedLimits.STANDARD_LENGTH:
            return DiscordLimitOverflowException('Embed author length', val, EmbedLimits.STANDARD_LENGTH)
        if self.footer and (val := len(self.footer)) > EmbedLimits.FOOTER_LENGTH:
            return DiscordLimitOverflowException('Embed footer length', val, EmbedLimits.FOOTER_LENGTH)
        return None

    def _apply_policy(self, policy: EmbedConversionPolicy) -> None:
        if (exc := self.get_error()):
            match policy:
                case EmbedConversionPolicy.RAISE_ERROR:
                    raise exc
                case EmbedConversionPolicy.TRUNCATE:
                    if len(self.fields) > EmbedLimits.FIELDS_COUNT:
                        self.fields = self.fields[:EmbedLimits.FIELDS_COUNT]

                    self.fields = [x.truncate() for x in self.fields]

                    if len(self.title) > EmbedLimits.STANDARD_LENGTH:
                        self.title = f'{self.title[:EmbedLimits.STANDARD_LENGTH - 3]}...'
                    if self.descr and len(self.descr) > EmbedLimits.DESCRIPTION_LENGTH:
                        self.descr = f'{self.descr[:EmbedLimits.DESCRIPTION_LENGTH - 3]}...'
                    if self.author and len(self.author) > EmbedLimits.STANDARD_LENGTH:
                        if isinstance(self.author, str):
                            self.author = f'{self.author[:EmbedLimits.STANDARD_LENGTH - 3]}...'
                        else:
                            self.author.name = f'{self.author.name[:EmbedLimits.STANDARD_LENGTH - 3]}...'
                    if self.footer and len(self.footer) > EmbedLimits.FOOTER_LENGTH:
                        if isinstance(self.footer, str):
                            self.footer = f'{self.footer[:EmbedLimits.FOOTER_LENGTH - 3]}...'
                        else:
                            self.footer.text = f'{self.footer.text[:EmbedLimits.FOOTER_LENGTH - 3]}...'

    def convert(self, *, policy: EmbedConversionPolicy = EmbedConversionPolicy.RAISE_ERROR) -> discord.Embed:
        self._apply_policy(policy)
        color = get_color(self.color) if self.color else get_random_color()
        embed = discord.Embed(color=color, title=self.title)
        embed.description = self.descr
        embed.url = self.link
        embed.set_image(url=self.img)
        embed.set_thumbnail(url=self.thumbnail)

        if isinstance(self.author, str):
            embed.set_author(name=self.author)
        elif isinstance(self.author, EmbedAuthorMeta):
            embed.set_author(name=self.author.name, url=self.author.url, icon_url=self.author.icon_url)

        if isinstance(self.footer, str):
            embed.set_footer(text=self.footer)
        elif isinstance(self.footer, EmbedIconTextMeta):
            embed.set_footer(text=self.footer.text, icon_url=self.footer.icon_url)

        for field in self.fields:
            embed.add_field(name=field.name, value=field.content, inline=field.inlined)

        return embed

    @override
    async def localize(self, ctx: ExtendedContext, *args, **kwargs) -> None:
        if isinstance(self.title, LocalizedStr):
            self.title = await self.title.localize(ctx, *args, **kwargs)
        if isinstance(self.descr, LocalizedStr):
            self.descr = await self.descr.localize(ctx, *args, **kwargs)

        if isinstance(self.author, LocalizedStr):
            self.author = await self.author.localize(ctx, *args, **kwargs)
        elif isinstance(self.author, EmbedAuthorMeta):
            await self.author.localize(ctx, *args, **kwargs)

        if isinstance(self.footer, LocalizedStr):
            self.footer = await self.footer.localize(ctx, *args, **kwargs)
        elif isinstance(self.footer, EmbedIconTextMeta):
            await self.footer.localize(ctx, *args, **kwargs)

        for field in self.fields:
            await field.localize(ctx, *args, **kwargs)
