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


from typing import Optional, Self
from dataclasses import dataclass
from enum import IntEnum, auto
import discord
from utils import get_color
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
class EmbedIconTexttMeta:
    text: str
    icon_url: str

    def __len__(self) -> int:
        return len(self.text)


@dataclass
class EmbedAuthorMeta:
    name: str
    url: Optional[str]
    icon_url: Optional[str]

    def __len__(self) -> int:
        return len(self.name)


@dataclass
class EmbedFieldMeta:
    name: str
    content: str
    inlined: bool = True

    def truncate(self) -> Self:
        name = f'{self.name[:EmbedLimits.STANDARD_LENGTH - 3]}...' if len(self.name) > EmbedLimits.STANDARD_LENGTH else self.name
        content = f'{self.content[:EmbedLimits.FIELD_CONTENT_LENGTH - 3]}...' \
            if len(self.content) > EmbedLimits.FIELD_CONTENT_LENGTH else self.content
        return self.__class__(name, content, self.inlined)


@dataclass
class DiscordEmbedMeta:
    title: str
    color: str
    descr: Optional[str] = None
    link: Optional[str] = None
    img: Optional[str] = None
    thumbnail: Optional[str] = None
    author: Optional[str | EmbedAuthorMeta] = None
    footer: Optional[str | EmbedIconTexttMeta] = None
    fields: list[EmbedFieldMeta] = []

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
        embed = discord.Embed(color=get_color(self.color), title=self.title)
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
        elif isinstance(self.footer, EmbedIconTexttMeta):
            embed.set_footer(text=self.footer.text, icon_url=self.footer.icon_url)

        for field in self.fields:
            embed.add_field(name=field.name, value=field.content, inline=field.inlined)

        return embed
