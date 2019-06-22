#!usr/bin/env python3.7
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

import latex
import os

class LatexBuilder:
    def __init__(self,file=None,autoinclude=True):
        self.remote = file
        self.content = ""
        if file is not None:
            with open(file,"r") as file:
                self.content = file.read()
        if autoinclude: self.include()

    def add_content(self,ct):
        self.content += ct

    def set_remote(self,newremote):
        self.remote = newremote

    def delete_remote(self):
        if self.remote is not None:
            os.remove(self.remote)
            self.remote = None

    def pull(self):
        with open(self.remote,"r") as file:
            self.content = file.read()

    def push(self):
        with open(self.remote,"w") as file:
            file.write(self.content)

    def include(self):
        self.content = self.content.replace(r"\include","\\newpage\n\\input")
        while r"\input{" in self.content:
            cmdsize = len(r"\input{")
            begin = self.content.find(r"\input{")+cmdsize
            end = self.content.find(r"}",begin)
            filename = "{}.tex".format(self.content[begin:end])
            with open(filename,"r") as file:
                included = file.read()
            self.content = self.content.replace(self.content[begin-cmdsize:end+1],included)

    def parse(self,**kwargs):
        for i,k in kwargs.items():
            tag = "<python.{}>".format(i)
            self.content = self.content.replace(tag,k)

    def compile(self,output=False):
        pdf = latex.build_pdf(self.content)
        if output:
            path = self.remote.replace(".tex","")
            path += ".pdf"
            pdf.save_to(path)
        return pdf
