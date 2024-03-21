#!usr/bin/env python3
#-*-coding:utf-8-*-

##    TtgcBot - a bot for discord
##    Copyright (C) 2017-2024  Thomas PIOT
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
from dices import Expression
from config import Log
from models import MemberDTO
from ...common import deffered_command


class Jdr(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.bot = client

    @deffered_command
    @commands.cooldown(10, 2, commands.BucketType.guild)
    @commands.cooldown(5, 2, commands.BucketType.member)
    @commands.hybrid_command(aliases=["rollindep", "r", "rolldice"], description="Roll dice and perform operations")
    async def roll(self, ctx: commands.Context, *, expression: str) -> None:
        """Roll dice and perform operations (supported symbols and operations : `*,+,-,/,()`) if given in the expression field.
        For rolling a dice, you have to use the litteral expression `xdy` where `x` is the number of dice rolled,  `d` the letter `d` and `y` the number of side of the dice (`1d100` will roll 1 dice with 100 sides for example).
        You can also roll special dice with your own values by writing them between brackets as following : `1d{red,blue,yellow,green}`.
        Full example : `/rollindep (10+1d100)*(2d10-5d8)` will return the result of the following expression : `(10+(1 dice with 100 sides))*((2 dice with 10 sides)-(5 dice with 8 sides))` <br/>
        Special dice example : `/rollindep 1d{1,2,3,4,5,6,7,8,9,10,Jack,Queen,King}+1d{Clubs,Diamonds,Hearts,Spades}` will return a single card with its value and its color (example : Queen of Spades)"""
        member = MemberDTO(ctx.author.id)
        fetch_task = member.fetch()
        parser = Expression(expression)
        result = parser()
        Log.info("rolled '%s' in channel %d of server %d", result, ctx.channel.id, ctx.guild.id) # pyright: ignore
        await fetch_task
        await ctx.send(member.lang['rollindep'].format(result))
