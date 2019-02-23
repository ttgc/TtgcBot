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
    def __init__(self,name,x=0,y=0,z=0):
        self.name = name
        self.x = x
        self.y = y
        self.z = z

    def move(self,dx,dy,dz=0):
        self.x += dx
        self.y += dy
        self.z += dz
        return abs(dx)+abs(dy)+abs(dz)

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
            #not finished
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
