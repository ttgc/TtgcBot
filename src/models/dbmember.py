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

from enum import Enum
from datahandler.api import APIManager
from exceptions import APIException
from network import RequestType

class MemberPermGrantable(Enum):
    MANAGER = "manager"
    PREMIUM = "premium"

class DBMember:
    def __init__(self, ID):
        self.ID = ID
        self.api = APIManager()
        self.perm = None
        self.lang = "EN"
        self.fulllangname = "English"
        self.blacklisted = False
        self.blacklistReason = ""

    @classmethod
    async def pull(cls, ID):
        member = cls(ID)
        info = await member.api(RequestType.GET, "Member/{}".format(member.ID), resource="MEMBER://{}".format(member.ID), requesterID=member.ID)

        if info.status // 100 != 2:
            raise APIException("Unable to find the requested member", member=member.ID, code=info.status)

        member.perm = info.result.get("permissions", None)
        if member.perm == "None": member.perm = None
        member.lang = info.result.get("language", {}).get("langcode", "EN")
        member.fulllangname = info.result.get("language", {}).get("name", "English") if member.lang != "EN" else "English"
        member.blacklisted = info.result.get("blacklisted", {}).get("isBlacklisted", False)
        member.blacklistReason = info.result.get("blacklisted", {}).get("reason", "")
        return member

    def is_owner(self):
        return self.perm.lower() == "owner"

    def is_manager(self):
        return (self.perm.lower() == "manager" or self.is_owner())

    def is_premium(self):
        return self.perm is not None

    def is_blacklisted(self):
        return self.blacklisted, self.blacklistReason

    async def unblacklist(self, requester):
        if not self.is_blacklisted()[0]: return
        info = await self.api(RequestType.DELETE, "Member/{}/unblacklist".format(self.ID), resource="MEMBER://{}".format(self.ID), requesterID=requester)

        if info.status // 100 != 2:
            raise APIException("Member unblacklist error", member=self.ID, code=info.status)

    @classmethod
    async def blacklist(cl, memberid, requester, reason=None):
        api = APIManager()
        info = await api(RequestType.PUT, "Member/{}/blacklist".format(memberid), resource="MEMBER://{}".format(memberid),
            requesterID=requester, body={} if reason is None else {"reason": reason})

        if info.status // 100 != 2 and info.status != 409:
            raise APIException("Member blacklist error", member=memberid, code=info.status)

        return cl(memberid)

    @staticmethod
    async def grantuser(memberid, perm, requester):
        api = APIManager()
        info = await api(RequestType.PUT, "Member/{}/grant/{}".format(memberid, perm.value), resource="MEMBER://{}".format(memberid), requesterID=requester)

        if info.status // 100 != 2:
            raise APIException("Member grant error", member=memberid, perm=perm.value, code=info.status)

    @staticmethod
    async def setuserlang(memberid, lang):
        api = APIManager()
        info = await api(RequestType.PUT, "Member/{}/setlang/{}".format(memberid, lang), resource="MEMBER://{}".format(memberid), requesterID=memberid)

        if info.status // 100 != 2:
            raise APIException("Member setlang error", member=memberid, lang=lang, code=info.status)

    @classmethod
    async def getuserlang(cl, memberid):
        try:
            mb = await cl(memberid)
            return mb.lang
        except APIException as e:
            if e["code"] != 404:
                raise e
            return "EN"
