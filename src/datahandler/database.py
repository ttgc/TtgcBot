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

import psycopg2 as sql
from setup.config import Config
from utils.decorators import deprecated

@deprecated("Old database manager", raise_error=True)
class Database:
    def __init__(self):
        config = Config()
        self.connection = sql.connect(dbname=config["database"]["name"],
                                      user=config["database"]["user"],
                                      password=config["database"]["password"],
                                      host=config["database"]["host"],
                                      port=config["database"]["port"])
        self.cur = None

    def execute(self,command,**kwargs):
        self.cur = self.connection.cursor()
        try:
            self.cur.execute(command,kwargs)
        except:
            return
        return self.cur

    def call(self,proc,**kwargs):
        self.cur = self.connection.cursor()
        try:
            self.cur.callproc(proc,kwargs)
        except:
            return
        return self.cur

    def getcursor(self):
        return self.cur

    def close(self,rollback=False):
        if self.cur is not None:
            self.cur.close()
            self.cur = None
        if rollback:
            self.connection.rollback()
        else:
            self.connection.commit()
        self.connection.close()
