#!usr/bin/env python3
#-*-coding:utf-8-*-
#translator

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

import os

def get_lang(langcode="EN"):
    langcode = langcode.upper()
    f = open("Lang/"+langcode+".lang","r",encoding="utf-8")
    lines = f.readlines()
    f.close()
    lang = {}
    for i in lines:
        if i.startswith("#"): continue
        lang[i.split("=")[0]] = (i.split("=")[1]).replace("\n","").replace("\\n","\n")
    return lang

def lang_exist(langcode="EN"):
    langcode = langcode.upper()
    return os.access("Lang/"+langcode+".lang",os.R_OK)

if not os.access("Lang/",os.F_OK):
    os.mkdir("Lang")
