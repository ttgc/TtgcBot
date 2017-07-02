#!usr/bin/env python3.4
#-*-coding:utf-8-*-
#INIfiles by Ttgc

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

class INI:
    """INI file object"""

    def __init__(self):
        self.section = {}

    def __str__(self):
        a = ""
        for name,i in (self.section).items():
            a += "["+str(name)+"]\n"
            for key,value in i.items():
                a += str(key)+"="+str(value)+"\n"
            a += "\n"
        return a

    def section_add(self,name):
        """Add an empty section to your ini file"""
        self.section[name] = {}

    def section_delete(self,section):
        """Delete a section from your file"""
        del(self.section[section])

    def key_add(self,section,name,value):
        """Add a new key or set an existing key in a section from your file"""
        a = self.section[section]
        a[name] = value

    def key_delete(self,section,key):
        """Delete a key"""
        a = self.section[section]
        del(a[key])

    def save(self,fname):
        """Save your inifile object into a true ini file
        The file is deleted before writing"""
        f = open(fname+".ini","w+")
        f.write(str(self))
        f.close()

    def load(self,fname):
        """Load an ini object from an ini file"""
        f = open(fname+".ini","r")
        a = f.readlines()
        f.close()
        for i in range(len(a)):
            if (a[i].find("[") != -1):
                b = a[i].replace("[","")
                b = b.replace("]\n","")
                self.section_add(b)
            elif (a[i].find("=") != -1):
                c = a[i].split("=")
                c[1] = c[1].replace("\n","")
                self.key_add(b,c[0],c[1])
