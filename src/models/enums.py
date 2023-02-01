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

import typing
from enum import Enum, EnumMeta
from utils import SerializableEnum
from utils.decorators import singleton
from exceptions import APIException, RaisedExceptionCommandError
from network import RequestType
from datahandler.api import APIManager
from functools import partial

class Extension:
    def __init__(self, universe, world):
        self.universe = universe
        self.world = world

    def __repr__(self):
        return f"{self.universe}_{self.world}"

    def __str__(self):
        return f"{self.universe} : {self.world}"

    def __eq__(self, other):
        return self.universe == other.universe and self.world == other.world

    def __ne__(self, other):
        return not self.__eq__(other)

    def contained_in(self, universe):
        return self.universe == universe

class AttributeRule(Enum):
    """
    Attribute setter rules. When set the rule is applied receiving those parameters:
    x = value to set
    e = entity on which the set will be applied
    attr = attribute/tag that will be set
    """
    ASSIGN = lambda x, e, attr: x
    BOUNDED_6 = lambda x, e, attr: max(1, min(6, x))
    BOUNDED_100 = lambda x, e, attr: max(1, min(100, x))
    RANGE_M10_10 = lambda x, e, attr: max(-10, min(10, x))
    POSITIVE = lambda x, e, attr: max(0, x)
    REL_POSITIVE = lambda x, e, attr: max(0, x + attr.get_attribute(e))
    POSITIVE_STRICT = lambda x, e, attr: max(1, x)
    SUP_M1 = lambda x, e, attr: max(-1, x)
    REL_BOUNDED_CUSTOM = lambda x, e, attr, tag: max(0, min(AttributeTag[tag].get_attribute(e), x))
    REL_LIMITED_CUSTOM = lambda x, e, attr, tag: min(AttributeTag[tag].get_attribute(e), x)

class AttributeTag(Enum):
    ######    = (id             , valtype, langkey    , dbkey        , charset, petset, charupdate, petupdate, rule)
    NAME      = ('name'         , str    , 'name'     , 'name'       , True   , True  , False     , False    , None)
    PV        = ('PV'           , int    , 'PV'       , 'pv'         , False  , False , True      , True     , partial(AttributeRule.REL_LIMITED_CUSTOM.value, tag='PV_MAX'))
    PM        = ('PM'           , int    , 'PM'       , 'pm'         , False  , False , True      , True     , partial(AttributeRule.REL_BOUNDED_CUSTOM.value, tag='PM_MAX'))
    PV_MAX    = ('PVmax'        , int    , 'PVmax'    , 'pv'         , True   , True  , False     , False    , AttributeRule.POSITIVE_STRICT.value)
    PM_MAX    = ('PMmax'        , int    , 'PMmax'    , 'pm'         , True   , True  , False     , False    , AttributeRule.POSITIVE.value)
    STR       = ('force'        , int    , 'force'    , 'strength'   , True   , True  , False     , False    , AttributeRule.BOUNDED_100.value)
    SPR       = ('esprit'       , int    , 'esprit'   , 'spirit'     , True   , True  , False     , False    , AttributeRule.BOUNDED_100.value)
    CHA       = ('charisme'     , int    , 'charisme' , 'charisma'   , True   , True  , False     , False    , AttributeRule.BOUNDED_100.value)
    AGI       = ('agilite'      , int    , 'agilite'  , 'agility'    , True   , True  , False     , False    , AttributeRule.BOUNDED_100.value)
    PREC      = ('precision'    , int    , 'precision', 'precision'  , True   , True  , False     , False    , AttributeRule.BOUNDED_100.value)
    LUCK      = ('luck'         , int    , 'chance'   , 'luck'       , True   , True  , False     , False    , AttributeRule.BOUNDED_100.value)
    INTUITION = ('intuition'    , int    , 'intuition', 'intuition'  , True   , False , False     , False    , AttributeRule.BOUNDED_6.value)
    MENTAL    = ('mental'       , int    , 'mental'   , 'mental'     , True   , False , True      , False    , AttributeRule.POSITIVE.value)
    KARMA     = ('karma'        , int    , 'karma'    , 'karma'      , False  , False , True      , False    , AttributeRule.RANGE_M10_10.value)
    DEF_KARMA = ('default_karma', int    , 'dkarma'   , 'karma'      , True   , True  , False     , False    , AttributeRule.RANGE_M10_10.value)
    DEF_GM    = ('default_mod'  , str    , 'dmod'     , 'gamemod'    , True   , True  , False     , False    , None)
    MONEY     = ('money'        , int    , 'money'    , 'money'      , True   , True  , True      , False    , AttributeRule.POSITIVE.value)
    PILOT_A   = ('astral_pilot' , int    , 'pilot_a'  , 'pilot'      , True   , False , False     , False    , AttributeRule.SUP_M1.value)
    PILOT_P   = ('planet_pilot' , int    , 'pilot_p'  , 'pilot'      , True   , False , False     , False    , AttributeRule.SUP_M1.value)
    INSTINCT  = ('instinct'     , int    , 'instinct' , 'instinct'   , False  , True  , False     , False    , AttributeRule.BOUNDED_6.value)
    SPECIES   = ('espece'       , str    , 'espece'   , 'species'    , False  , True  , False     , False    , None)
    LP        = ('lp'           , int    , 'lp'       , 'light_point', False  , False , True      , False    , AttributeRule.REL_POSITIVE.value)
    DP        = ('dp'           , int    , 'dp'       , 'dark_point' , False  , False , True      , False    , AttributeRule.REL_POSITIVE.value)

    def __init__(self, id, valtype, langkey, dbkey, charset, petset, charupdate, petupdate, rule):
        self.id = id
        self.valtype = valtype
        self.langkey = langkey
        self.dbkey = dbkey
        self.charset = charset
        self.petset = petset
        self.charupdate = charupdate
        self.petupdate = petupdate
        self.rule = partial(rule if rule is not None else AttributeRule.ASSIGN.value, attr=self)

    def translate(self, lang=None):
        return lang[self.langkey] if lang else self.id.replace('_', ' ').capitalize()

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    def isnumeric(self):
        return self.valtype is int or self.valtype is float

    def isstring(self):
        return self.valtype is str

    def get_attribute_or_default(self, entity, default_value=None, *, throw=False):
        if throw and not hasattr(entity, self.id):
            raise RaisedExceptionCommandError(AttributeError(f"Entity {entity} of type {type(entity).__name__} does not have attribute {self.id}"))
        return getattr(entity, self.id, default_value)

    get_attribute = partial(get_attribute_or_default, default_value=None, throw=True)

    def set_attribute(self, entity, value):
        setattr(entity, self.id, self.rule(value, entity))

    @classmethod
    def to_dict(cls, lang=None, filter=lambda x: True):
        return {i.id: i.translate(lang) for i in cls if filter(i)}

    @classmethod
    def get_charset(cls, lang=None, with_num=True, with_str=True):
        return cls.to_dict(lang, lambda x: x.charset and ((with_num and x.isnumeric()) or (with_str and x.isstring())))

    @classmethod
    def get_petset(cls, lang=None, with_num=True, with_str=True):
        return cls.to_dict(lang, lambda x: x.petset and ((with_num and x.isnumeric()) or (with_str and x.isstring())))

    @classmethod
    def get_charupdate(cls, lang=None, with_num=True, with_str=True):
        return cls.to_dict(lang, lambda x: x.charupdate and ((with_num and x.isnumeric()) or (with_str and x.isstring())))

    @classmethod
    def get_petupdate(cls, lang=None, with_num=True, with_str=True):
        return cls.to_dict(lang, lambda x: x.petupdate and ((with_num and x.isnumeric()) or (with_str and x.isstring())))

@singleton
class AutoPopulatedEnums:
    def __init__(self):
        self._gm: typing.Optional[_Gamemods] = None
        self._ext: dict[str, list[Extension]] = {}
        self._races: dict[Extension, EnumMeta] = {}
        self._sb: dict[Extension, EnumMeta] = {}
        self._orgs: dict[Extension, EnumMeta] = {}
        self.api = APIManager()

    def purge(self):
        self._gm = None
        self._ext = {}
        self._races = {}
        self._sb = {}
        self._orgs = {}

    async def get_gamemods(self):
        if self._gm is None:
            info = await self.api(RequestType.GET, "JDR/gamemods")
            values = {'UNDEFINED': (-1, 'undefined', '', False)}

            if info.status // 100 != 2:
                raise APIException("Get gamemods error", code=info.status)

            for i, gm in enumerate(info.result.get('gamemods', [])):
                values[gm.get('name').upper()] = (i, gm.get('name').lower(), gm.get('code'), gm.get('is_system_only', False))

            self._gm = _Gamemods('Gamemods', values)
        return self._gm

    async def get_extensions(self, *, universe=None):
        if not self._ext:
            info = await self.api(RequestType.GET, "JDR/extensions")

            if info.status // 100 != 2:
                raise APIException("Get extensions error", code=info.status)

            for ext_data in info.result.get('extensions', []):
                ext = Extension(ext_data.get('universe'), ext_data.get('world'))
                if ext.universe in self._ext:
                    self._ext[ext.universe].append(ext)
                else:
                    self._ext[ext.universe] = [ext]

        return self._ext if universe is None else self._ext[universe]

    async def get_races(self, extension):
        if extension not in self._races:
            info = await self.api(RequestType.GET, f"JDR/{extension.universe}/{extension.world}/races")

            if info.status // 100 != 2:
                raise APIException("Get races error", code=info.status, extension=extension)

            clName = f'Race_{extension.universe}_{extension.world}'
            self._races[extension] = _Race(clName, {race.upper(): race.lower() for race in info.result.get('list', [])})
        return self._races.get(extension)

    async def get_symbionts(self, extension):
        if extension not in self._sb:
            info = await self.api(RequestType.GET, f"JDR/{extension.universe}/{extension.world}/symbionts")

            if info.status // 100 != 2:
                raise APIException("Get symbionts error", code=info.status, extension=extension)

            clName = f'Symbiont_{extension.universe}_{extension.world}'
            self._sb[extension] = SerializableEnum(clName, {sb.upper(): sb.lower() for sb in info.result.get('list', [])})
        return self._sb.get(extension)

    async def get_orgs(self, extension):
        if extension not in self._orgs:
            info = await self.api(RequestType.GET, f"JDR/{extension.universe}/{extension.world}/organizations")

            if info.status // 100 != 2:
                raise APIException("Get symbionts error", code=info.status, extension=extension)

            clName = f'Organization_{extension.universe}_{extension.world}'
            values = {org.get('Organization').upper(): (org.get('Organization').lower(), org.get('Hidden')) for org in info.result.get('list', [])}
            self._orgs[extension] = _Org(clName, values)
        return self._orgs.get(extension)

class _Gamemods(Enum):
    def __int__(self):
        return self.index

    def __str__(self):
        return self.name

    @property
    def index(self):
        return self.value[0]

    @property
    def name(self):
        return self.value[1]

    @property
    def charcode(self):
        return self.value[2]

    @property
    def is_system_only(self):
        return self.value[3]

    @classmethod
    def from_str(cl, name):
        for gm in cl:
            if str(gm) == name: return gm
        return cl.UNDEFINED

    @classmethod
    def from_int(cl, value):
        for gm in cl:
            if int(gm) == value: return gm
        return cl.UNDEFINED

    @classmethod
    def from_charcode(cl, charcode):
        for gm in cl:
            if gm.charcode == charcode: return gm
        return cl.UNDEFINED

class _Race(SerializableEnum):
    def __init__(self):
        self._classes: EnumMeta = None

    async def get_classes(self, extension):
        if self._classes is None:
            info = await self.api(RequestType.GET, f"JDR/{extension.universe}/{extension.world}/{self}/classes")

            if info.status // 100 != 2:
                raise APIException("Get classes error", code=info.status, extension=extension, race=str(self))

            clName = f'Classe_{extension.universe}_{extension.world}_{self}'
            self._classes = SerializableEnum(clName, {cl.upper(): cl.lower() for cl in info.result.get('list', [])})
        return self._classes

    @classmethod
    def to_dict(cls, filter=lambda x: True):
        result = {}
        for race in cls:
            if filter(race):
                result[race.name] = race.value

        return result

class _Org(SerializableEnum):
    def __init__(self, name, hidden=False):
        self._value_ = name
        self._hidden = hidden

    @property
    def hidden(self):
        return self._hidden
