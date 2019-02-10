#!usr/bin/env python3.4
#-*-coding:utf-8-*-
#logfile manager

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

import os,time

def singleton(classe_definie):
    instances = {} # Dictionnaire de nos instances singletons
    def get_instance():
        if classe_definie not in instances:
            # On crée notre premier objet de classe_definie
            instances[classe_definie] = classe_definie()
        return instances[classe_definie]
    return get_instance

@singleton
class LogSystem:
    def __init__(self):
        self.limit = -1 #limit = -1 = no limit
        self.directory = ""

    def clean(self):
        if not os.access(self.directory,os.F_OK): os.mkdir(self.directory)
        if len(os.listdir(self.directory)) >= self.limit:
            ls = os.listdir(self.directory)
            fdel = ls[0]
            for i in os.listdir(self.directory):
                if os.stat(self.directory+"/"+i).st_ctime < os.stat(self.directory+"/"+fdel).st_ctime:
                    fdel = i
            os.remove(self.directory+"/"+fdel)

class Logfile:
    def __init__(self,name,system):
        self.name = name
        self.sys = system
        self.file = None

    def start(self):
        self.sys.clean()
        self.file = open(self.sys.directory+"/"+self.name+".log",'w+')
        self.append("OPENING","Starting using the file log")

    def restart(self):
        self.file = open(self.sys.directory+"/"+self.name+".log",'a')

    def append(self,title,msg):
        tps = time.localtime()
        self.file.write("["+str(tps.tm_mday)+"/"+str(tps.tm_mon)+"/"+str(tps.tm_year)+"_"+str(tps.tm_hour)+":"+str(tps.tm_min)+":"+str(tps.tm_sec)+"]["+title+"] "+msg+"\n")
        return tps

    def stop(self):
        self.file.close()
