#!usr/bin/env python3.4
#-*-coding:utf-8-*-
#PythonBDD for discord bots

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

import time
import os
from random import *
from INIfiles import *

def singleton(classe_definie):
    instances = {} # Dictionnaire de nos instances singletons
    def get_instance():
        if classe_definie not in instances:
            # On crée notre premier objet de classe_definie
            instances[classe_definie] = classe_definie()
        return instances[classe_definie]
    return get_instance

@singleton
class _PythonBDDfiles:
    def __init__(self):
        #EDIT THE FILENAMES HERE
        self.location = "Data/"
        self.config = "configBDD"
        #END OF EDIT
        if not os.access(self.location,os.F_OK):
            os.mkdir(self.location)
        if not os.access(self.location+self.config+".ini",os.F_OK):
            cfg = INI()
            cfg.section_add("BDD")
            cfg.save(self.location+self.config)

    def clear_entry(self,name,erase_file=True):
        cfg = INI()
        cfg.load(self.location+self.config)
        ident = cfg.section["BDD"][name]
        cfg.key_delete("BDD",name)
        if erase_file:
            os.remove(self.location+self.name+"#"+ident)

class BDD:
    def __init__(self,name):
        self.name = name
        self.identifier = randint(10000,99999)
        self.file = INI()

    def __str__(self):
        return self.name+"#"+str(self.identifier)

    def __getitem__(self,it):
        sec,key = it
        return self.file.section[sec][key]

    def __setitem__(self,it,value):
        sec,key = it
        self.file.key_add(sec,key,value)

    def __delitem__(self,it):
        sec,key = it
        self.file.key_delete(sec,key)

    def create_group(self,gr_name):
        self.file.section_add(gr_name)

    def save(self):
        system = _PythonBDDfiles()
        self.file.save(system.location+str(self))
        config = INI()
        config.load(system.location+system.config)
        config.key_add("BDD",str(self.name),str(self.identifier))
        config.save(system.location+system.config)

    def load(self):
        system = _PythonBDDfiles()
        config = INI()
        config.load(system.location+system.config)
        self.identifier = int(config.section["BDD"][self.name])
        self.file.load(system.location+str(self))
