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

from datahandler.database import Database
from utils.decorators import deprecated
from exceptions import DatabaseException

@deprecated("Old feature using DatabaseManager")
def retrieveCharacterOrigins(cl):
    db = Database()
    cur = db.execute("SELECT classe.nom,race.nom FROM classe INNER JOIN race ON classe.id_race = race.id_race WHERE id_classe = %(ID)s",ID=cl)
    if cur is None:
        db.close(True)
        raise DatabaseException("Class ID not found")
    row = cur.fetchone()
    db.close()
    return row[1],row[0]

@deprecated("Old feature using DatabaseManager")
def retrieveClassID(rcid,clname):
    db = Database()
    cur = db.execute("SELECT id_classe FROM classe WHERE lower(nom) = %(name)s AND id_race = %(rc)s",name=clname.lower(),rc=rcid)
    if cur is None:
        db.close(True)
        raise DatabaseException("Class Name not found")
    row = cur.fetchone()
    db.close()
    return row

@deprecated("Old feature using DatabaseManager")
def retrieveRaceID(rcname):
    db = Database()
    cur = db.execute("SELECT id_race FROM race WHERE lower(nom) = %(name)s",name=rcname.lower())
    if cur is None:
        db.close(True)
        raise DatabaseException("Race Name not found")
    row = cur.fetchone()
    db.close()
    return row

@deprecated("Old feature using DatabaseManager")
def retrieveRaceName(rcid):
    if rcid is None: return None
    db = Database()
    cur = db.execute("SELECT nom FROM race WHERE id_race = %(rc)s",rc=rcid)
    if cur is None:
        db.close(True)
        raise DatabaseException("Race Name not found")
    row = cur.fetchone()
    db.close()
    return row[0]

@deprecated("Old feature using DatabaseManager")
def retrieveSymbiontID(sbname):
    db = Database()
    cur = db.execute("SELECT id_symbiont FROM symbiont WHERE lower(nom) = %(name)s",name=sbname.lower())
    if cur is None:
        db.close(True)
        raise DatabaseException("Symbiont Name not found")
    row = cur.fetchone()
    db.close()
    return row

@deprecated("Old feature using DatabaseManager")
def retrieveSymbiontName(sbid):
    if sbid is None: return None
    db = Database()
    cur = db.execute("SELECT nom FROM symbiont WHERE id_symbiont = %(sb)s",sb=sbid)
    if cur is None:
        db.close(True)
        raise DatabaseException("Race Name not found")
    row = cur.fetchone()
    db.close()
    return row[0]

@deprecated("Old feature using DatabaseManager")
def retrieveOrganization(orgid):
    db = Database()
    cur = db.execute("SELECT nom FROM organizations WHERE id_org = %(id)s",id=orgid)
    if cur is None:
        db.close()
        return None
    row = cur.fetchone()
    db.close()
    return row[0] if row is not None else None

@deprecated("Old feature using DatabaseManager")
def isOrganizationHidden(orgname):
    db = Database()
    cur = db.execute("SELECT hidden FROM organizations WHERE nom = %(org)s", org=orgname)
    if cur is None:
        db.close()
        return False
    row = cur.fetchone()
    db.close()
    return row[0] if row is not None else False

@deprecated("Old feature using DatabaseManager")
def organizationExists(orgname):
    db = Database()
    cur = db.execute("SELECT COUNT(*) FROM organizations WHERE nom = %(org)s",org=orgname)
    if cur is None:
        db.close(True)
        raise DatabaseException("Error when fetching organization table")
    nbr = cur.fetchone()[0]
    db.close()
    return nbr > 0

@deprecated("Old feature using DatabaseManager")
def retrieveOrganizationSkill(orgname):
    db = Database()
    cur = db.call("get_orgskills",org=orgname)
    if cur is None:
        db.close()
        return []
    ls = []
    for i in row:
        ls.append(Skill(i[0]))
    db.close()
    return ls

@deprecated("Old feature using DatabaseManager")
def retrieveRaceSkill(racename):
    db = Database()
    cur = db.call("get_raceskills",racename=racename)
    if cur is None:
        db.close()
        return []
    ls = []
    for i in row:
        ls.append(Skill(i[0]))
    db.close()
    return ls
