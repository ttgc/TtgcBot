#!usr/bin/env python3.4
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

import psycopg2 as sql
from INIfiles import *

class Database:
    def __init__(self):
        configfile = INI()
        configfile.load("token")
        self.connection = sql.connect(dbname=configfile.section["DATABASE"]["name"],
                                      user=configfile.section["DATABASE"]["user"],
                                      password=configfile.section["DATABASE"]["pwd"],
                                      host=configfile.section["DATABASE"]["IP"],
                                      port=configfile.section["DATABASE"]["port"])
        self.cur = None

    def execute(self,command,**kwargs):
        self.cur = self.connection.cursor()
        try:
            cur.execute(command,kwargs)
        except:
            self.connection.rollback()
            return
        self.connection.commit()
        return self.cur

    def call(self,proc,**kwargs):
        self.cur = self.connection.cursor()
        try:
            cur.callproc(proc,kwargs)
        except:
            self.connection.rollback()
            return
        self.connection.commit()
        return self.cur

    def getcursor(self):
        return self.cur

    def close(self):
        self.connection.close()

class DatabaseException(Exception):
    pass
        
