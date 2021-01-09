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

from src.tools.datahandler.DatabaseManager import *
from random import *
from enum import Enum, unique
import src.tools.Character as char
import src.tools.CharacterUtils as chutil
from discord.ext import commands

@unique
class PiloteRollType(Enum):
    ASTRAL = "pilot_a"
    PLANET = "pilot_p"

    def translate(self, lang):
        return lang[self.value]

    def get_character_value(self, char):
        if self == PiloteRollType.ASTRAL:
            return char.astral_pilot
        elif self == PiloteRollType.PLANET:
            return char.planet_pilot
        return

@unique
class DiceType(Enum):
    D4 = 4
    D6 = 6
    D8 = 8
    D10 = 10
    D12 = 12
    D20 = 20
    D100 = 100

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
        return str(nbr[0])

class ParseCharacterRoll:
    def __init__(self,lang,char,stat,operator="+",expression=None):
        self.lang = lang
        self.char = char
        self.stat = stat.lower()
        self.op = operator
        self.expr = None if expression is None else ParseRoll(expression)

        self.msg = ""
        self.result = 50
        self.karma = 0
        self.statval = 50
        self.tts = False
        self.strstat = ""

    def resolv(self):
        if self.stat in ["force","str","strength"]:
            self.statval = self.char.force
            self.strstat = self.lang["force"]
            return self._resolv_force()
        if self.stat in ["esprit","spr","spirit"]:
            self.statval = self.char.esprit
            self.strstat = self.lang["esprit"]
            return self._resolv_esprit()
        if self.stat in ["charisme","cha","charisma"]:
            self.statval = self.char.charisme
            self.strstat = self.lang["charisme"]
            return self._resolv_charisme()
        if self.stat in ["agilite","agi","agility","furtivite","furtivity"]:
            self.statval = self.char.agilite
            self.strstat = self.lang["agilite"]
            return self._resolv_agilite()
        if self.stat in ["precision","prec"]:
            self.statval = self.char.precision
            self.strstat = self.lang["precision"]
            return self._resolv_precision()
        if self.stat in ["chance","luck"]:
            self.statval = self.char.luck
            self.strstat = self.lang["chance"]
            return self._resolv_luck()
        if self.stat in ["intuition","instinct","int"]:
            self.statval = self.char.intuition
            self.strstat = self.lang["instinct" if self.stat == "instinct" else "intuition"]
            return self._resolv_intuition()
        # if self.stat in ["opportunite","op","opportunity"]:
        #     return self._resolv_opportunity()
        raise discord.ext.BadArgument("Invalid stat {} in parsing roll".format(self.stat))

    def _resolv_force(self):
        self._roll()
        return self.msg

    _resolv_esprit = _resolv_force
    _resolv_charisme = _resolv_force
    _resolv_agilite = _resolv_force
    _resolv_precision = _resolv_force
    _resolv_luck = _resolv_force

    def _resolv_intuition(self):
        self.result = randint(1,6)
        self.msg = self.lang["result_test"].format(self.strstat,self.result,self.statval)
        self._check_karma()
        return self.msg

    # def _resolv_opportunity(self):
    #     self.result = (randint(1,6), randint(1,6))
    #     resultc, resultm = self.result
    #     msgc = self.lang["result_test_nomax"].format(self.lang["advantage"],str(resultc))+"\n"
    #     if resultc == 1: msgc += self.lang["chance_1"]
    #     elif resultc == 2: msgc += self.lang["chance_2"]
    #     elif resultc == 3: msgc += self.lang["chance_3"]
    #     elif resultc == 4: msgc += self.lang["chance_4"]
    #     elif resultc == 5: msgc += self.lang["chance_5"]
    #     elif resultc == 6: msgc += self.lang["chance_6"]
    #     msgm = self.lang["result_test_nomax"].format(self.lang["disadvantage"],str(resultm))
    #     if resultm == 1: msgm += self.lang["malchance_1"]
    #     elif resultm == 2: msgm += self.lang["malchance_2"]
    #     elif resultm == 3: msgm += self.lang["malchance_3"]
    #     elif resultm == 4: msgm += self.lang["malchance_4"]
    #     elif resultm == 5: msgm += self.lang["malchance_5"]
    #     elif resultm == 6: msgm += self.lang["malchance_6"]
    #     self.msg = "\n".join([msgc, msgm])
    #     if resultc < resultm: self.karma = 1
    #     else: self.karma = -1
    #     self._check_skills()
    #     self._check_karma()
    #     self._apply_karma()
    #     if resultc == resultm:
    #         if resultc == 1: msgsuper = self.lang["superchance_1"]
    #         elif resultc == 2: msgsuper = self.lang["superchance_2"]
    #         elif resultc == 3: msgsuper = self.lang["superchance_3"]
    #         elif resultc == 4: msgsuper = self.lang["superchance_4"]
    #         elif resultc == 5: msgsuper = self.lang["superchance_5"]
    #         elif resultc == 6: msgsuper = self.lang["superchance_6"]
    #         self.msg = "\n".join([msgc, msgm, self.lang["superchance"], msgsuper])
    #     return self.msg

    def _roll(self):
        dice = randint(1,100)
        kar = randint(1,10)
        if self.expr is not None:
            self.statval = self.statval + (self.expr.resolv()[0] * ((-1)**(self.op=="-")))
        if self.char.karma <= -5 and dice not in [42, 66]:
            self.result = dice + kar
            self.msg = self.lang["result_test_karma"].format(self.strstat,self.result,dice,"+",kar,self.statval)
        elif self.char.karma >= 5 and dice not in [42, 66]:
            self.result = dice - kar
            self.msg = self.lang["result_test_karma"].format(self.strstat,self.result,dice,"-",kar,self.statval)
        else:
            self.result = dice
            self.msg = self.lang["result_test"].format(self.strstat,self.result,self.statval)
        self._parse_result()

    def _check_skills(self):
        if chutil.Skill.isskillin(self.char.skills,7): #chanceux
            self.karma *= 2
        if chutil.Skill.isskillin(self.char.skills,84): #creature harmonieuse
            if self.char.karma == 0 and self.karma < 0:
                self.karma -= 5
            elif self.char.karma == 0 and self.karma > 0:
                self.karma +=5
            elif self.char.karma+self.karma > -5 and self.char.karma+self.karma < 5 and self.karma < 0:
                self.karma -= 9
            elif self.char.karma+self.karma > -5 and self.char.karma+self.karma < 5 and self.karma > 0:
                self.karma += 9

    def _check_karma(self):
        if self.char.karma+self.karma < -10:
            self.karma = -10-self.char.karma#char.karma = -10
        if self.char.karma+self.karma > 10:
            self.karma = 10-self.char.karma#char.karma = 10

    def _apply_karma(self):
        self.char.charset('kar',self.karma)
        self.char.karma += self.karma

    def _parse_result(self):
        if self.result == 66:
            self.char.stat[-1] += 1
            self.karma = 2
            self.msg = self.lang["66"]
            self.tts = True
        elif self.result == 42:
            self.char.stat[1] += 1
            self.karma = -2
            self.msg = self.lang["42"]
            self.tts = True
        elif self.result <= 10:
            self.char.stat[2] += 1
            self.karma = -1
        elif self.result >= 91:
            self.char.stat[-2] += 1
            self.karma = 1
        elif self.result <= self.statval:
            self.char.stat[3] += 1
        else:
            self.char.stat[-3] += 1
        self._check_skills()
        self._check_karma()
        self._apply_karma()
        self._hasroll()

    def _hasroll(self):
        db = Database()
        db.call("hasroll",dbkey=self.char.key,idserv=self.char.jdr.server,idchan=self.char.jdr.channel,valmax=self.statval,val=self.result)
        db.close()

class ParsePetRoll(ParseCharacterRoll):
    def __init__(self,lang,char,pet,stat,operator="+",expression=None):
        ParseCharacterRoll.__init__(self,lang,char,stat,operator,expression)
        self.petowner = self.char
        self.char = pet

    def resolv(self):
        if self.stat in ["force","str","strength","esprit","spr","spirit","charisme","cha",
                            "charisma","agilite","agi","agility","furtivite","furtivity",
                            "precision","prec","chance","luck"]:
            return ParseCharacterRoll.resolv(self)
        if self.stat in ["instinct","int"]:
            self.statval = self.char.instinct
            self.strstat = self.lang["instinct"]
            return self._resolv_intuition()
        raise AttributeError("Invalid stat {} in parsing roll".format(self.stat))

##    def _resolv_opportunity(self):
##        raise NotImplementedError("unsuported operation for pet")

    def _check_skills(self): pass

    def _apply_karma(self):
        self.char.petset('kar',self.karma)
        self.char.karma += self.karma

    def _hasroll(self):
        db = Database()
        db.call("pethasroll",dbkey=self.char.key,charact=self.char.charkey,idserv=self.char.jdr.server,idchan=self.char.jdr.channel,valmax=self.statval,val=self.result)
        db.close()

class ParsePilotRoll:
    def __init__(self, lang, chars, ptype, dice, operator="+", expression=None):
        self.lang = lang
        self.chars = chars
        self.ptype = ptype
        self.dice = dice
        self.op = operator
        self.expr = None if expression is None else ParseRoll(expression)

        self.msg = ""
        self.result = 0
        self.statval = 0
        self.strstat = self.ptype.translate(self.lang)

        if self.expr is not None:
            self.statval += (self.expr.resolv()[0] * ((-1)**(self.op=="-")))

        for i in self.chars:
            charval = self.ptype.get_character_value(i)
            if charval is None or charval < 0:
                raise discord.ext.BadArgument("Invalid stat {} in parsing pilot roll, stat value is negative for character {}".format(self.ptype.value, self.char.key))
            self.statval += charval

    def resolv(self):
        self.result = randint(1, self.dice.value)
        self.msg = self.lang["result_test"].format(self.strstat,self.result,self.statval)
        return self.msg
