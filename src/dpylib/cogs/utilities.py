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
from lang import LocalizedStr
from config import Config, Log
from ..common.contextext import ExtendedContext
from ..common.embed import DiscordEmbedMeta, EmbedAuthorMeta, EmbedFieldMeta, EmbedIconTextMeta
from ..common.invite import InviteLink


class Utilities(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.bot = client

    @commands.hybrid_command()
    async def invite(self, ctx: ExtendedContext) -> None:
        avatar = self.bot.user.avatar.url if self.bot.user and self.bot.user.avatar else None
        url = str(InviteLink(self.bot, dev_bypass=False))
        embed = DiscordEmbedMeta(
            title='TtgcBot',
            color='',
            descr=LocalizedStr('invite'),
            img=avatar,
            thumbnail='https://www.thetaleofgreatcosmos.fr/wp-content/uploads/2019/11/TTGC_Text.png',
            author=EmbedAuthorMeta('Ttgc', url, 'http://www.thetaleofgreatcosmos.fr/wp-content/uploads/2018/08/avatar-2-perso.png'),
            footer=EmbedIconTextMeta(LocalizedStr('invite_author'), avatar) if avatar else LocalizedStr('invite_author'),
            fields=[EmbedFieldMeta(LocalizedStr('invite_srv'), str(len(self.bot.guilds)))]
        )

        await embed.localize(ctx, Config()['version'])
        await ctx.send(embed=embed.convert())
        Log.info("Invite generated on channel %d from server %d by %d", ctx.channel.id, ctx.guild.id, ctx.author.id)

    @commands.hybrid_command()
    @commands.cooldown(1, 60, commands.BucketType.guild)
    async def ping(self, ctx: ExtendedContext) -> None:
        ping = await LocalizedStr('ping', round(self.bot.latency * 1000)).localize(ctx)
        await ctx.send(ping)
