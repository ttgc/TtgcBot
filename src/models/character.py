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


from typing import Self, Optional, TYPE_CHECKING
from dataclasses import dataclass
from network.api import API
from network.httprequest import HTTP
from network.resources import pull_resource
from network.statuscode import HttpErrorCode
from network.exceptions import HTTPException
from config import Log
from utils.decorators import catch
from dpylib.common.user import extract_top_role
from .enumerations import fetch_gamemods, fetch_extensions
from .char_ident import CharacterIdentityDTO
from .member import MemberDTO


if TYPE_CHECKING:
    import discord
    from .enumerations import BaseGamemods, BaseRaces, BaseClasses, BaseExtensions, BaseOrganizations, BaseSymbionts
    from .jdr import JdrDTO


@dataclass(kw_only=True)
class CharacterStatsDTO:
    rolled: int = 0
    success: int = 0
    failures: int = 0
    crit_success: int = 0
    crit_failure: int = 0
    super_crit_success: int = 0
    super_crit_failure: int = 0

    @property
    def luck_rate(self) -> float:
        return ((self.super_crit_success * 2) + self.crit_success) / self.rolled if self.rolled else 0

    @property
    def unluck_rate(self) -> float:
        return ((self.super_crit_failure * 2) + self.crit_failure) / self.rolled if self.rolled else 0


@dataclass(init=False)
class CharacterDTO(CharacterIdentityDTO):
    srv_id: int
    chan_id: int
    name: str
    pvmax: int
    pmmax: int
    pv: int
    pm: int
    force: int
    esprit: int
    charisme: int
    agilite: int
    precision: int
    chance: int
    karma: int
    default_karma: int
    money: int
    stats: CharacterStatsDTO
    lp: int
    dp: int
    mod: Optional[BaseGamemods]
    default_mod: Optional[BaseGamemods]
    intuition: int
    mental: int
    lvl: int
    inventory: None # TODO: inventory DTO
    pets: dict[str, None] # TODO: pet DTO
    skills: list[None] # TODO: skill DTO
    ext: Optional[BaseExtensions]
    race: Optional[BaseRaces]
    classe: Optional[BaseClasses]
    jdr: Optional[JdrDTO]
    xp: int
    affiliation: Optional[BaseOrganizations]
    hybrid_race: Optional[BaseRaces]
    symbiont: Optional[BaseSymbionts]
    planet_pilot: int
    astral_pilot: int

    def __init__(self, charkey: str, srv_id: int, chan_id: int, **kwargs) -> None:
        self.charkey = charkey
        self.srv_id = srv_id
        self.chan_id = chan_id
        self.fetch = pull_resource(f'CHARACTER://{self.srv_id}/{self.chan_id}/{self.charkey}', ttl=24)(self.fetch)

        self.name = kwargs.get('name', charkey)
        self.pvmax = kwargs.get('pvmax', 1)
        self.pmmax = kwargs.get('pmmax', 0)
        self.pv = kwargs.get('pv', 1)
        self.pm = kwargs.get('pm', 0)
        self.force = kwargs.get('force', 50)
        self.esprit = kwargs.get('esprit', 50)
        self.charisme = kwargs.get('charisme', 50)
        self.agilite = kwargs.get('agilite', 50)
        self.precision = kwargs.get('precision', 50)
        self.chance = kwargs.get('chance', 50)
        self.karma = kwargs.get('karma', 0)
        self.default_karma = kwargs.get('default_karma', 0)
        self.money = kwargs.get('money', 0)
        self.stats = kwargs.get('stats', CharacterStatsDTO())
        self.lp = kwargs.get('lp', 0)
        self.dp = kwargs.get('dp', 0)
        self.mod = kwargs.get('mod', None)
        self.default_mod = kwargs.get('default_mod', None)
        self.intuition = kwargs.get('intuition', 3)
        self.mental = kwargs.get('mental', 100)
        self.lvl = kwargs.get('lvl', 1)
        self.member = kwargs.get('linked', None)
        self.selected = kwargs.get('selected', False)
        self.inventory = kwargs.get('inventory', None) # TODO: inventory DTO
        self.pets = kwargs.get('pets', {})
        self.skills = kwargs.get('skills', [])
        self.dead = kwargs.get('dead', False)
        self.ext = kwargs.get('ext', None)
        self.race = kwargs.get('race', None)
        self.classe = kwargs.get('classe', None)
        self.jdr = kwargs.get('jdr', None)
        self.xp = kwargs.get('xp', 0)
        self.affiliation = kwargs.get('affiliation', None)
        self.hybrid_race = kwargs.get('hybrid_race', None)
        self.symbiont = kwargs.get('symbiont', None)
        self.planet_pilot = kwargs.get('planet_pilot', -1)
        self.astral_pilot = kwargs.get('astral_pilot', -1)

    @catch(HTTPException, error_value=None, logger=Log.error, asynchronous=True)
    async def fetch(self) -> Optional[Self]:
        async with API('/api/character/{serverID}/{channelID}/{charkey}') as api:
            response = await api(HTTP.GET, f'/api/character/{self.srv_id}/{self.chan_id}/{self.charkey}')
            response.whitelist(HttpErrorCode.NOT_FOUND)
            response.raise_errors()

        if response.status.ko:
            Log.warn('HTTP character fetch failure (%d) for id=%d/%d/%s', response.error_code, self.srv_id, self.chan_id, self.charkey)
            return None
        if not response.result or not isinstance(response.result, dict):
            Log.error('HTTP character fetch unexpected result produced for id=%d/%d/%s: %s', self.srv_id, self.chan_id, self.charkey, response.result)
            return None

        Gamemods = await fetch_gamemods()
        Extensions = await fetch_extensions()

        self.name = response.result.get('Nom', self.name)
        self.pvmax = response.result.get('Pvmax', self.pvmax)
        self.pmmax = response.result.get('Pmmax', self.pmmax)
        self.pv = response.result.get('Pv', self.pv)
        self.pm = response.result.get('Pm', self.pm)
        self.force = response.result.get('Strength', self.force)
        self.esprit = response.result.get('Spirit', self.esprit)
        self.charisme = response.result.get('Charisma', self.charisme)
        self.agilite = response.result.get('Agility', self.agilite)
        self.precision = response.result.get('Prec', self.precision)
        self.chance = response.result.get('Luck', self.chance)
        self.karma = response.result.get('Karma', self.karma)
        self.default_karma = response.result.get('Defaultkarma', self.default_karma)
        self.money = response.result.get('Argent', self.money)
        self.stats = CharacterStatsDTO(
            rolled=response.result.get('RolledDice', self.stats.rolled),
            success=response.result.get('Succes', self.stats.success),
            failures=response.result.get('Fail', self.stats.failures),
            crit_success=response.result.get('CriticSuccess', self.stats.crit_success),
            crit_failure=response.result.get('CriticFail', self.stats.crit_failure),
            super_crit_success=response.result.get('SuperCriticSuccess', self.stats.super_crit_success),
            super_crit_failure=response.result.get('SuperCriticFail', self.stats.super_crit_failure)
        )
        self.lp = response.result.get('LightPoints', self.lp)
        self.dp = response.result.get('DarkPoints', self.dp)
        self.mod = Gamemods.from_name(response.result.get('Gm', 'Defensive'))
        self.default_mod = Gamemods.from_name(response.result.get('GmDefault', 'Defensive'))
        self.intuition = response.result.get('Intuition', self.intuition)
        self.mental = response.result.get('Mental', self.mental)
        self.lvl = response.result.get('Lvl', self.lvl)
        self.member = response.result.get('IdMember', None)
        self.selected = response.result.get('Linked', self.selected)
        self.dead = response.result.get('Dead', self.dead)
        _universe = response.result.get('Extension', {}).get('universe', 'Cosmorigins')
        _world = response.result.get('Extension', {}).get('world', 'Terae')
        self.ext = Extensions.find(_universe, _world)

        Races = await self.ext.fetch_races()
        Organizations = await self.ext.fetch_organizations()
        Symbionts = await self.ext.fetch_symbionts()
        self.race = Races.from_name(response.result.get('Race', 'Human'))
        Classes = await self.race.fetch_classes()

        self.classe = Classes.from_name(response.result.get('Classe', None))
        self.xp = response.result.get('Xp', self.xp)
        _org = response.result.get('AffiliatedWith', {}).get('Organization', None)
        self.affiliation = Organizations.from_name(_org) if _org else None
        self.hybrid_race = Races.from_name(response.result.get('HybridRace')) if response.result.get('HybridRace', None) else None
        self.symbiont = Symbionts.from_name(response.result.get('Symbiont')) if response.result.get('Symbiont', None) else None
        self.planet_pilot = response.result.get('PilotA', self.planet_pilot)
        self.astral_pilot = response.result.get('PilotP', self.astral_pilot)
        return self

    @property
    def linked(self) -> Optional[MemberDTO]:
        return MemberDTO(self.member) if self.member else None

    def bind(self, jdr: JdrDTO) -> None:
        if not self.jdr:
            self.jdr = jdr

    @classmethod
    async def find_active_character(cls, jdr: JdrDTO, member_id: int) -> Optional[Self]:
        charlist = await jdr.get_character_list()
        for member, char in charlist.active_characters.items():
            if member == member_id:
                full_char = cls(
                    char.charkey,
                    jdr.srv_id,
                    jdr.chan_id,
                    member=member_id,
                    selected=char.selected,
                    dead=char.dead
                )
                full_char.bind(jdr)
                return full_char
        return None
