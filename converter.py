#!usr/bin/env python3.4
#-*-coding:utf-8-*-
#converter

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

def convert_str_into_dic(string):
    if string == "{}": return {}
    string = string.replace("{","")
    string = string.replace("}","")
    string = string.replace("'","")
    #string = string.replace(" ","")
    ls = string.split(", ")
    dic = {}
    for i in range(len(ls)):
        temp = ls[i].split(": ")
        dic[temp[0]] = temp[1]
    return dic

def convert_str_into_ls(string):
    if string == "[]": return []
    string = string.replace("[","")
    string = string.replace("]","")
    string = string.replace("'","")
    ls = string.split(", ")
    return ls

def convert_str_into_ls_spe(string):
    if string == "{}": return []
    string = string.replace("{","")
    string = string.replace("}","")
    string = string.replace("'","")
    ls = string.split(", ")
    return ls

def convert_string_into_tuple(string):
    string = string.replace("'","")
    string = string.replace("(","")
    string = string.replace(")","")
    ls = string.split(", ")
    return tuple(ls)
def convert_str_into_tuple(string):
    return convert_string_into_tuple(string)

def convert_ls_into_str_spe(ls):
    string = str(ls)
    string = string.replace("[","{")
    string = string.replace("]","}")
    return string

def convert_str_into_dict_with_ls_spe(string):
    if string == "{}": return {}
    ls = []
    while string.find("<") != -1 and string.find(">") != -1:
        start = string.find("<")
        end = string.find(">")+1
        extract = string[start:end]
        string = string.replace(string[start:end],"[]")
        extract = extract.replace("<","{")
        extract = extract.replace(">","}")
        ls.append(convert_str_into_ls_spe(extract))
    dic = convert_str_into_dic(string)
    pos = 0
    for i in dic.keys():
        if dic[i] == "[]":
            dic[i] = ls[pos]
            pos += 1
    return dic
