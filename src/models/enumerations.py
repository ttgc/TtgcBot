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


from enum import Enum, StrEnum
from typing import Self, Type
from network.api import API
from network.httprequest import HTTP
from network.resources import pull_resource
from network.statuscode import HttpErrorCode
from network.exceptions import HTTPException
from config import Log
from utils import snake_to_pascal_case
from utils.decorators import catch


class BaseExtBoundEnum(StrEnum):
    def __init__(self, value: str, extension: 'BaseExtensions') -> None:
        object.__init__(self)
        self.ext = extension


class BaseClasses(BaseExtBoundEnum):
    def __init__(self, value: str, race: 'BaseRaces') -> None:
        BaseExtBoundEnum.__init__(self, value, race.ext)
        self.race = race


class BaseOrganizations(BaseExtBoundEnum):
    def __init__(self, value: str, extension: 'BaseExtensions', hidden: bool) -> None:
        BaseExtBoundEnum.__init__(self, value, extension)
        self.hidden = hidden

    def __bool__(self) -> bool:
        return not self.hidden


class BaseSymbionts(BaseExtBoundEnum):
    pass


class BaseRaces(BaseExtBoundEnum):
    def __init__(self, value: str, extension: 'BaseExtensions') -> None:
        BaseExtBoundEnum.__init__(self, value, extension)
        self.fetch_classes = pull_resource(f'RACE://{value}/classes', ttl=168)(self.fetch_classes)

    @catch(HTTPException, error_value=None, logger=Log.error, asynchronous=True)
    async def fetch_classes(self) -> Type[BaseClasses]:
        async with API(f'/api/jdr/{self.ext.universe}/{self.ext.world}/{self}/classes') as api:
            response = await api(HTTP.GET, f'/api/jdr/{self.ext.universe}/{self.ext.world}/{self}/classes')
            response.whitelist(HttpErrorCode.NOT_FOUND).raise_errors()

        enum_name = snake_to_pascal_case(f'{self.ext.name}_{self.name}_Classes')

        if response.status.ok and response.result and isinstance(response.result, dict):
            values = {x.strip().replace(' ', '_').upper(): (x, self) for x in response.result.get('list', [])}
            return BaseClasses(value=enum_name, names=values) # type: ignore

        return BaseClasses(value=enum_name, names={}) # type: ignore


class BaseExtensions(Enum):
    def __new__(cls, universe: str, world: str) -> Self:
        self = object.__new__(cls)
        self._value_ = f'{universe} : {world}'
        return self

    def __init__(self, universe: str, world: str) -> None:
        object.__init__(self)
        self._world = world
        self._universe = universe
        self.fetch_races = pull_resource(f'EXT://{self.value}/races', ttl=168)(self.fetch_races)
        self.fetch_organizations = pull_resource(f'EXT://{self.value}/orgs', ttl=168)(self.fetch_organizations)
        self.fetch_symbionts = pull_resource(f'EXT://{self.value}/symbionts', ttl=168)(self.fetch_symbionts)

    @property
    def world(self) -> str:
        return self._world

    @property
    def universe(self) -> str:
        return self._universe

    def __str__(self) -> str:
        return self.value

    @catch(HTTPException, error_value=None, logger=Log.error, asynchronous=True)
    async def fetch_races(self) -> Type[BaseRaces]:
        async with API(f'/api/jdr/{self.universe}/{self.world}/races') as api:
            response = await api(HTTP.GET, f'/api/jdr/{self.universe}/{self.world}/races')
            response.whitelist(HttpErrorCode.NOT_FOUND).raise_errors()

        enum_name = snake_to_pascal_case(f'{self.name}_Races')

        if response.status.ok and response.result and isinstance(response.result, dict):
            values = {x.strip().replace(' ', '_').upper(): (x, self) for x in response.result.get('list', [])}
            return BaseRaces(value=enum_name, names=values) # type: ignore

        return BaseRaces(value=enum_name, names={}) # type: ignore

    @catch(HTTPException, error_value=None, logger=Log.error, asynchronous=True)
    async def fetch_organizations(self) -> Type[BaseOrganizations]:
        async with API(f'/api/jdr/{self.universe}/{self.world}/organizations') as api:
            response = await api(HTTP.GET, f'/api/jdr/{self.universe}/{self.world}/organizations')
            response.whitelist(HttpErrorCode.NOT_FOUND).raise_errors()

        enum_name = snake_to_pascal_case(f'{self.name}_Organizations')

        if response.status.ok and response.result and isinstance(response.result, dict):
            values = {}

            for x in response.result.get('list', []):
                key = x['Organization'].strip().replace(' ', '_').upper()
                values[key] = (x['Organization'], self, x['Hidden'])

            return BaseOrganizations(value=enum_name, names=values) # type: ignore

        return BaseOrganizations(value=enum_name, names={}) # type: ignore

    @catch(HTTPException, error_value=None, logger=Log.error, asynchronous=True)
    async def fetch_symbionts(self) -> Type[BaseSymbionts]:
        async with API(f'/api/jdr/{self.universe}/{self.world}/symbionts') as api:
            response = await api(HTTP.GET, f'/api/jdr/{self.universe}/{self.world}/symbionts')
            response.whitelist(HttpErrorCode.NOT_FOUND).raise_errors()

        enum_name = snake_to_pascal_case(f'{self.name}_Symbionts')

        if response.status.ok and response.result and isinstance(response.result, dict):
            values = {x.strip().replace(' ', '_').upper(): (x, self) for x in response.result.get('list', [])}
            return BaseSymbionts(value=enum_name, names=values) # type: ignore

        return BaseSymbionts(value=enum_name, names={}) # type: ignore

    @classmethod
    def find(cls, universe: str, world: str) -> Self:
        for ext in cls:
            if ext.universe == universe and ext.world == world:
                return ext
        raise ValueError(f"Unable to find extension for universe '{universe}' and world '{world}'")

    @classmethod
    def from_name(cls, name: str) -> Self:
        for ext in cls:
            if ext.name == name:
                return ext
        raise ValueError(f"Unable to find extension named '{name}")


class BaseGamemods(StrEnum):
    def __init__(self, value: str, system_only: bool) -> None:
        object.__init__(self)
        self.system_only = system_only

    def __bool__(self) -> bool:
        return not self.system_only

    @classmethod
    def from_name(cls, name: str) -> Self:
        for gm in cls:
            if gm == name:
                return gm
        raise ValueError(f'Invalid gamemod name {name}')


@catch(HTTPException, error_value=BaseExtensions(value='Extensions', names={}), logger=Log.error, asynchronous=True)
@pull_resource('EXT://...', ttl=168)
async def fetch_extensions() -> Type[BaseExtensions]:
    async with API('/api/jdr/extensions') as api:
        response = await api(HTTP.GET, '/api/jdr/extensions')
        response.raise_errors()

    if response.status.ok and response.result and isinstance(response.result, dict):
        values = {}
        for x in response.result.get('extensions', []):
            name = f"{x['universe']}_{x['world']}".strip().replace(' ', '_').upper()
            values[name] = (x['universe'], x['world'])
        return BaseExtensions(value='Extensions', names=values)

    return BaseExtensions(value='Extensions', names={}) # type: ignore


@catch(HTTPException, error_value=BaseGamemods(value='Gamemods', names={}), logger=Log.error, asynchronous=True)
@pull_resource('GM://...', ttl=168)
async def fetch_gamemods() -> Type[BaseGamemods]:
    async with API('/api/jdr/gamemods') as api:
        response = await api(HTTP.GET, '/api/jdr/gamemods')
        response.raise_errors()

    if response.status.ok and response.result and isinstance(response.result, dict):
        values = {x['code']: (x['name'], x['is_system_only']) for x in response.result.get('gamemods', [])}
        return BaseGamemods(value='Gamemods', names=values)

    return BaseGamemods(value='Gamemods', names={}) # type: ignore
