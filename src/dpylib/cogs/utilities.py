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
from lang import LocalizedStr
from config import Config, Log
from ..common.contextext import ExtendedContext
from ..common.embed import DiscordEmbedMeta, EmbedAuthorMeta, EmbedFieldMeta, EmbedIconTextMeta
from ..common.invite import InviteLink
from ..checks.server import check_server_admin
from ..workflow import SettingsWorkflow


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

    @commands.check(check_server_admin)
    @commands.hybrid_command(aliases=['config', 'parameters', 'params'])
    async def settings(self, ctx: ExtendedContext) -> None:
        srv = await ctx.ext.server
        flow = SettingsWorkflow(ctx, srv, self.bot.user.avatar.url) # type: ignore
        await flow(ctx)

        prefix_input = TextInput(
            LocalizedStr('prefix'),
            default=srv.prefix, # type: ignore
            required=True,
            max_length=3,
            placeholder=LocalizedStr('prefix_placeholder'),
            row=1
        )
        admin_input = TextInput(LocalizedStr('admin_role'), )

        view = EmbedView(
            # embed: DiscordEmbedMeta,
            # timeout: Optional[float] = None,
            # owner: Optional[UserType] = None,
            # checks: list[Callable[[Self, discord.Interaction], bool]] = None, # type: ignore
            # on_timeout: Optional[Callable[[Self], Awaitable[None]]] = None,
            # on_error: Optional[Callable[[Self, discord.Interaction, Exception, ui.Item], Awaitable[None]]] = None
        )

        await view.localize(ctx)
        await view.send(ctx)
