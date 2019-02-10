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

from random import *

class ParseRoll:
    def __init__(self,expr):
        self.expr = expr.replace(" ","")

    def resolv(self):
        expr = self.expr
        expr = expr.replace("`","")
        raw = expr
        expr = "|{}|".format(expr)
        symbols = ["*","/","+","-","(",")","|"]
        while expr.find("d") != -1:
            values = []
            start = expr.find("d")
            end = expr.find("d")
            while expr[start] not in symbols: start -= 1
            while expr[end] not in symbols: end += 1
            dice = expr[start+1:end]
            nbr,faces = dice.split("d")[0],dice.split("d")[1]
            if "{" in faces:
                vals = faces.replace("{","")
                vals = vals.replace("}","")
                values = vals.split(",")
                faces = len(values)
            result = 0
            raw_result = ""
            for i in range(int(nbr)):
                generated = randint(1,int(faces))
                result += generated
                if len(values) == 0:
                    raw_result += "{}+".format(generated)
                else:
                    raw_result += "{}+".format(values[generated-1])
            expr = expr.replace(dice,str(result))
            raw = raw.replace(dice,"({})".format(raw_result[:-1]))

        operators = ["*","/","+","-"]
        expr = expr.replace("|","")
        expr = self._calc(expr,operators)
        value = float(expr)
        if int((value%1)*100) == 0: value = int(value)
        return value,raw

    def _calc(self,expr,op):
        while expr.find("(") != -1:
            expr = expr.replace(expr[expr.find("("):expr.find(")")+1],self._calc(expr[expr.find("(")+1:expr.find(")")],op))
            expr = expr.replace("+-","-")

        nbr,operation = [],[]
        start = 0
        for i in range(len(expr)):
            if expr[i] in op:
                nbr.append(float(expr[start:i]))
                operation.append(expr[i])
                start = i+1
        nbr.append(float(expr[start:]))
        for i in op:
            for k in range(len(operation)-1,-1,-1):
                if operation[k] == i:
                    exec("nbr[k]=nbr[k]{}nbr[k+1]".format(i))
                    nbr.pop(k+1)
                    operation.pop(k)
        print(nbr)
        return str(nbr[0])
