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

import json, os, sys
from deepmerge import always_merger

class Config:
    instance = None

    def __new__(cl):
        if cl.instance is None: cl.instance = super().__new__(cl)
        return cl.instance

    def __init__(self):
        with open("config/config.json", "r") as f:
            self.base = json.load(f)
        self.dev, self.staging, self.prod = {}, {}, {}
        if os.access("config/config.development.json", os.R_OK):
            with open("config/config.development.json", "r") as f:
                self.dev = json.load(f)
        if os.access("config/config.staging.json", os.R_OK):
            with open("config/config.staging.json", "r") as f:
                self.staging = json.load(f)
        if os.access("config/config.production.json", os.R_OK):
            with open("config/config.production.json", "r") as f:
                self.prod = json.load(f)

        self.environment = None
        if len(sys.argv) > 1 and sys.argv in ["development", "staging", "production"]:
            self.environment = sys.argv[1]

        self.merged = dict(self.base)
        if self.environment is None or self.environment == "development":
            always_merger.merge(self.merged, self.dev)
        if self.environment is None or self.environment == "staging":
            always_merger.merge(self.merged, self.staging)
        if self.environment is None or self.environment == "production":
            always_merger.merge(self.merged, self.prod)

    def __getitem__(self, key):
        return self.merged[key]
