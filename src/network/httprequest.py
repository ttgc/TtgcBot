#!usr/bin/env python3
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

import aiohttp
from exceptions import HTTPException

class HTTP:
    def __init__(self, url, status, result=None, raiseClientException=False, raiseServerException=True):
        self.url = url
        self.status = status
        self.result = result
        if raiseServerException and self.status // 100 == 5:
            raise HTTPException(self.status, self.url)
        elif raiseClientException and self.status // 100 == 4:
            raise HTTPException(self.status, self.url)

    @classmethod
    async def _processResult(cl, r, hasResult=True, jsonResult=True):
        res = None
        if r.status == 200 and hasResult:
            if jsonResult:
                res = await r.json()
            else:
                res = await r.text()
        return cl(url, r.status, res)

    @classmethod
    async def get(cl, url, *, query={}, headers={}, jsonResult=True):
        async with aiohttp.ClientSession() as session:
            if len(headers) > 0:
                if len(query) > 0:
                    async with session.get(url, params=kwargs, headers=headers, ssl=False) as r:
                        res = await cl._processResult(r, jsonResult=jsonResult)
                        return res
                else:
                    async with session.get(url, headers=headers, ssl=False) as r:
                        res = await cl._processResult(r, jsonResult=jsonResult)
                        return res
            else:
                if len(query) > 0:
                    async with session.get(url, params=kwargs, ssl=False) as r:
                        res = await cl._processResult(r, jsonResult=jsonResult)
                        return res
                else:
                    async with session.get(url, ssl=False) as r:
                        res = await cl._processResult(r, jsonResult=jsonResult)
                        return res

    @classmethod
    async def post(cl, url, body, *, hasResult=False, headers={}, jsonResult=True):
        async with aiohttp.ClientSession() as session:
            if len(headers) > 0:
                async with session.post(url, json=body, headers=headers, ssl=False) as r:
                    res = await cl._processResult(r, hasResult, jsonResult)
                    return res
            else:
                async with session.post(url, json=body, ssl=False) as r:
                    res = await cl._processResult(r, hasResult, jsonResult)
                    return res

    @classmethod
    async def put(cl, url, body=None, *, hasResult=False, headers={}, jsonResult=True):
        async with aiohttp.ClientSession() as session:
            if len(headers) > 0:
                if body:
                    async with session.put(url, json=body, headers=headers, ssl=False) as r:
                        res = await cl._processResult(r, hasResult, jsonResult)
                        return res
                else:
                    async with session.put(url, headers=headers, ssl=False) as r:
                        res = await cl._processResult(r, hasResult, jsonResult)
                        return res
            else:
                if body:
                    async with session.put(url, json=body, ssl=False) as r:
                        res = await cl._processResult(r, hasResult, jsonResult)
                        return res
                else:
                    async with session.put(url, ssl=False) as r:
                        res = await cl._processResult(r, hasResult, jsonResult)
                        return res

    @classmethod
    async def delete(cl, url, body=None, *, hasResult=False, headers={}, jsonResult=True):
        async with aiohttp.ClientSession() as session:
            if len(headers) > 0:
                if body:
                    async with session.delete(url, json=body, headers=headers, ssl=False) as r:
                        res = await cl._processResult(r, hasResult, jsonResult)
                        return res
                else:
                    async with session.delete(url, headers=headers, ssl=False) as r:
                        res = await cl._processResult(r, hasResult, jsonResult)
                        return res
            else:
                if body:
                    async with session.delete(url, json=body, ssl=False) as r:
                        res = await cl._processResult(r, hasResult, jsonResult)
                        return res
                else:
                    async with session.delete(url, ssl=False) as r:
                        res = await cl._processResult(r, hasResult, jsonResult)
                        return res
