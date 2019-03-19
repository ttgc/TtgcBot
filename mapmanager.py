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

from enum import Enum
from PIL import Image,ImageDraw,ImageFont
from DatabaseManager import *
import io,asyncio

class Shape(Enum):
    """
    Shape parameters avalaible
    CIRCLE : r
    SPHERE : r
    LINE : length, orientation=0, height=1, thickness=0
        orientation in (0,90,180,270) -> (RIGHT, UP, LEFT, DOWN)
    RECT : rx, ry
    CUBE : rx, ry, rz
    CONIC : lengths, orientation=0
        orientation in (0,90,180,270) -> (RIGHT, UP, LEFT, DOWN)
        lengths = list for each steps
        example: [1,3,5] -> length = 1 for dist = 0 / length = 3 for dist = 1
        lengths must be not divisible by 2 to avoid problems
    """
    CIRCLE = 0
    SPHERE = 1
    LINE = 2
    RECT = 3
    CUBE = 4
    CONIC = 5

class Token:
    def __init__(self,name,servid,chanid,x=0,y=0,z=0):
        self.name = name
        self.server = servid
        self.channel = chanid
        self.x = x
        self.y = y
        self.z = z

    def load(name,servid,chanid):
        db = Database()
        cur = db.call("getmaptoken",idserv=servid,idchan=chanid,tkname=name)
        if cur is None:
            db.close(True)
            raise DatabaseException("This token does not exist !")
        tk = cur.fetchone()
        db.close()
        return Token(tk[2],tk[0],tk[1],tk[3],tk[4],tk[5])
    load = staticmethod(load)

    def save(self):
        result = False
        try: Token.load(self.name)
        except:
            db = Database()
            db.call("addtoken",idserv=self.server,idchan=self.channel,tkname=self.name,tkx=self.x,tky=self.y,tkz=self.z)
            db.close()
            result = True
        return result

    def remove(self):
        db = Database()
        db.call("rmtoken",idserv=self.server,idchan=self.channel,tkname=self.name)
        db.close()

    def move(self,dx_,dy_,dz_=0):
        self.x += dx_
        self.y += dy_
        self.z += dz_
        db = Database()
        db.call("movetoken",idserv=self.server,idchan=self.channel,tkname=self.name,dx=dx_,dy=dy_,dz=dz_)
        db.close()
        return abs(dx_)+abs(dy_)+abs(dz_)

    def registerEffect(self,dx,dy,dz,shape,shapeParameter):
        db = Database()
        cur = db.call("addeffect",idserv=self.server,idchan=self.channel,tkname=self.name,effshape=shape,effdx=dx,effdy=dy,effdz=dz,effparameters=str(shapeParameter))
        if cur is None:
            db.close(True)
            raise DatabaseException("Cannot register the effect")
        result = cur.fetchone()
        db.close()
        return result

    def cleareffect(self):
        db = Database()
        db.call("cleareffect",idserv=self.server,idchan=self.channel,tkname=self.name)
        db.close()

    def spawnAreaEffect(self,dx,dy,dz,shape,shapeParameter):
        initpoint = (self.x+dx,self.y+dy,self.z+dz)
        area = []
        if shape == Shape.CIRCLE or shape == Shape.SPHERE:
            rz = shapeParameter['r']
            rxy = shapeParameter['r']
            if shape == Shape.CIRCLE: rz = 0
            cornerLD = (initpoint[0]-rxy,initpoint[1]-rxy,initpoint[2]-rz)
            cornerRU = (initpoint[0]+rxy,initpoint[1]+rxy,initpoint[2]+rz)
            for x in range(cornerLD[0],cornerRU[0]+1):
                for y in range(cornerLD[1],cornerRU[1]+1):
                    for z in range(cornerLD[2],cornerRU[2]+1):
                        dist = abs(x-initpoint[0])+abs(y-initpoint[1])+abs(z-initpoint[2])
                        if dist <= shapeParameter['r']:
                            area.append((x,y,z))
        elif shape == Shape.RECT or shape == Shape.CUBE:
            rx = shapeParameter['rx']
            ry = shapeParameter['ry']
            rz = shapeParameter.get('rz',0)
            cornerLD = (initpoint[0]-rxy,initpoint[1]-rxy,initpoint[2]-rz)
            cornerRU = (initpoint[0]+rxy,initpoint[1]+rxy,initpoint[2]+rz)
            for x in range(cornerLD[0],cornerRU[0]+1):
                for y in range(cornerLD[1],cornerRU[1]+1):
                    for z in range(cornerLD[2],cornerRU[2]+1):
                        area.append((x,y,z))
        elif shape == Shape.LINE:
            height = shapeParameter.get('height',1)
            thickness = shapeParameter.get('thickness',0)
            ori = shapeParameter.get('orientation',0)
            length = shapeParameter['length']
            if ori not in [0,90,180,270]: ori = 0
            if ori == 0:
                for x in range(initpoint[0],initpoint[0]+length):
                    for y in range(initpoint[1]-thickness,initpoint[1]+thickness+1):
                        for z in range(initpoint[2],initpoint[2]+height):
                            area.append((x,y,z))
            elif ori == 90:
                for x in range(initpoint[0]-thickness,initpoint[0]+thickness+1):
                    for y in range(initpoint[1]-length+1,initpoint[1]+1):
                        for z in range(initpoint[2],initpoint[2]+height):
                            area.append((x,y,z))
            elif ori == 180:
                for x in range(initpoint[0]-length+1,initpoint[0]+1):
                    for y in range(initpoint[1]-thickness,initpoint[1]+thickness+1):
                        for z in range(initpoint[2],initpoint[2]+height):
                            area.append((x,y,z))
            else:
                for x in range(initpoint[0]-thickness,initpoint[0]+thickness+1):
                    for y in range(initpoint[1],initpoint[1]+length):
                        for z in range(initpoint[2],initpoint[2]+height):
                            area.append((x,y,z))
        elif shape == Shape.CONIC:
            ori = shapeParameter.get('orientation',0)
            length = len(shapeParameter['lengths'])
            lines = shapeParameter['lengths']
            if ori not in [0,90,180,270]: ori = 0
            if ori == 0:
                curline = 0
                for x in range(initpoint[0],initpoint[0]+length):
                    r = lines[curline]//2
                    for y in range(initpoint[1]-r,initpoint[1]+r+1):
                        z = initpoint[2]
                        area.append((x,y,z))
                        curline += 1
            elif ori == 90:
                curline = length-1
                for y in range(initpoint[1]-length+1,initpoint[1]+1):
                    r = lines[curline]//2
                    for x in range(initpoint[0]-r,initpoint[0]+r+1):
                        z = initpoint[2]
                        area.append((x,y,z))
                        curline -= 1
            elif ori == 180:
                curline = length-1
                for x in range(initpoint[0]-length+1,initpoint[0]+1):
                    r = lines[curline]//2
                    for y in range(initpoint[1]-r,initpoint[1]+r+1):
                        z = initpoint[2]
                        area.append((x,y,z))
                        curline -= 1
            else:
                curline = 0
                for y in range(initpoint[1],initpoint[1]+length):
                    r = lines[curline]//2
                    for x in range(initpoint[0]-r,initpoint[0]+r+1):
                        z = initpoint[2]
                        area.append((x,y,z))
                        curline += 1
        return area

class Map:
    colorscale = [(255,0,0,128),(192,192,192,192),(255,255,0,128),(128,128,0,128),(0,128,0,128),
        (0,255,255,128),(0,0,255,128),(255,0,255,128),(128,0,128,128),(23,165,137,128),(211,84,0,128)]
    font = ImageFont.truetype("arial.ttf",20)

    def __init__(self,cols,rows,servid,chanid):
        self.cols = cols
        self.rows = rows
        self.scale = 64
        self.width = cols*self.scale
        self.height= rows*self.scale
        self.img = Image.new('RGBA',(self.width+1,self.height+1))
        self.server = servid
        self.channel = chanid

    def clear(servid,chanid):
        db = Database()
        db.call("clearmap",idserv=servid,idchan=chanid)
        db.close()
    clear = staticmethod(clear)

    @asyncio.coroutine
    def send(self,cli,chan):
        db = Database()
        cur = db.call("getmap",idserv=self.server,idchan=self.channel)
        if cur is None:
            db.close(True)
            raise DatabaseException("There is no JDR in this channel")
        token = []
        for i in cur:
            token.append(Token(i[2],i[0],i[1],i[3],i[4],i[5]))
        db.close()
        db = Database()
        cur = db.call("getmapeffect",idserv=self.server,idchan=self.channel)
        if cur is None:
            db.close(True)
            raise DatabaseException("There is no JDR in this channel")
        effect = []
        for i in cur:
            effect.append(i)
        db.close()

        drawer = ImageDraw.Draw(self.img)
        colorindex = 0
        for i in effect:
            tk = None
            for k in token:
                if k.name == i[3]:
                    tk = k
                    break
            color = Map.colorscale[colorindex]
            colorindex += 1
            for k in tk.spawnAreaEffect(i[5],i[6],i[7],i[4],reformatAreaParameters(i[8])):
                drawer.rectangle([k[0]*self.scale,k[1]*self.scale,(k[0]+1)*self.scale,(k[1]+1)*self.scale],fill=color,outline=color)
        for i in token:
            txt = i.name[:3]
            if i.z > 0: txt += "+{}".format(int(i.z))
            elif i.z < 0: txt += str(i.z)
            corrector = 0
            if i.z != 0: corrector = 5
            drawer.text([(i.x*self.scale)+((self.scale-drawer.textsize(txt)[0])//2)-corrector,(i.y*self.scale)+((self.scale-drawer.textsize(txt)[1])//2)],txt,fill="#000000",font=Map.font)
        for x in range(0,(self.cols+1)*self.scale,self.scale):
            for y in range(0,(self.rows+1)*self.scale,self.scale):
                drawer.line([x,0,x,self.rows*self.scale],fill="#000000")
                drawer.line([0,y,self.cols*self.scale,y],fill="#000000")
        bytes = io.BytesIO()
        self.img.save(bytes,'PNG')
        bytes.seek(0)
        yield from cli.send_file(chan,bytes,filename="map.png")
        bytes.close()

def reformatAreaParameters(src):
    dic = {}
    src = src.replace("{","")
    src = src.replace("}","")
    src = src.replace(" ","")
    if "lengths" in src:
        tmp = src[src.find("[")+1:src.find("]")]
        tmp = tmp.replace(",",";")
        src = src.replace(src[src.find("["):src.find("]")+1],tmp)
    ls = src.split(",")
    for i in ls:
        tags = i.split(":","")
        if tags[0] == "lengths":
            interntags = tags[1].split(";")
            internls = []
            for k in interntags: internls.append(int(k))
            dic[tags[0]] = internls
        else:
            dic[tags[0]] = int(tags[1])
    return dic
