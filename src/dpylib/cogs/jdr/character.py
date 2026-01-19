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


from typing import Optional
import discord
from discord.ext import commands
from dices import Expression
from config import Log
from lang import localize
from models import JdrDTO
from utils.aliases import JdrChannel
from ...common.contextext import ExtendedContext, prepare_ctx
from ...checks.jdr import check_jdr_channel, check_mj, check_has_character
from ...workflow import CharcreateWorkflow


class Character(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.bot = client

    @commands.hybrid_group(aliases=['char', 'perso', 'personnage'])
    async def character(self, ctx: ExtendedContext) -> None:
        pass

    @prepare_ctx
    # @commands.check(check_mj)
    @commands.cooldown(1, 10, commands.BucketType.member)
    @character.command(name='create', aliases=['new', '+'], description="Create a new character")
    async def character_create(self, ctx: ExtendedContext, charkey: str, pj: Optional[discord.Member]) -> None:
        workflow = CharcreateWorkflow(ctx, charkey, pj)
        await workflow(ctx)