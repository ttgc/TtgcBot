#!usr/bin/env python3
#-*-coding:utf-8-*-

##    TtgcBot - a bot for discord
##    Copyright (C) 2017-2026  Thomas PIOT
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


from discord.ext import commands
from ..common.contextext import ExtendedContext
from ..ui.embed import EmbedBrowserView
from ..common.embed import DiscordEmbedMeta, EmbedFieldMeta
from ..workflow import CharcreateWorkflow


class TCog(commands.Cog, name="Test", command_attrs=dict(hidden=True)):
    def __init__(self, client: commands.Bot) -> None:
        self.bot = client

    @commands.hybrid_group()
    async def test(self, ctx: ExtendedContext) -> None:
        pass

    @commands.is_owner()
    @test.command(name='browser')
    async def test_browser(self, ctx: ExtendedContext) -> None:
        fields = [EmbedFieldMeta(f'item {x}', 'Lorem ipsum dolor sit amet') for x in range(156)]
        embed = DiscordEmbedMeta(title="Title", color="FF0000", descr="Lorem ipsum dolor sit amet", fields=fields)
        browser = EmbedBrowserView(embed, owner=ctx.author)
        await browser.send(ctx)

    @commands.is_owner()
    @test.command(name='charcreate')
    async def test_charcreate(self, ctx: ExtendedContext, charkey: str) -> None:
        flow = CharcreateWorkflow(ctx, charkey)
        await flow(ctx)
