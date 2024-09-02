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


from typing import TYPE_CHECKING, Optional, override
from enum import IntEnum, auto
import discord
from lang import LocalizedStr, LocalizeStrCase, localize
from utils.emojis import Emoji
from models import ServerDTO
from ..common.embed import DiscordEmbedMeta, EmbedAuthorMeta, EmbedFieldMeta, EmbedIconTextMeta
from ..ui.components import RoleDropdown, View, Button, Modal, TextInput, button, modal
from ..ui.embed import EmbedView
from .iworkflow import IWorkflow, setup_view

if TYPE_CHECKING:
    from ..common.contextext import ExtendedContext


class SettingsWorkflow(IWorkflow[bool]):
    class SettingsViewID(IWorkflow.ViewID):
        PANEL = 'panel'
        SET_PREFIX = 'set_prefix'
        SET_ROLE = 'set_role'

    class RoleID(IntEnum):
        ADMIN = auto()
        MJ = auto()

    def __init__(self, ctx: 'ExtendedContext', srv: ServerDTO, bot_avatar: str) -> None:
        super().__init__()
        self.srv = srv
        self.owner = ctx.author
        self.ctx = ctx
        avatar = ctx.author.avatar.url if ctx.author.avatar else None
        self.prefix = self.srv.prefix
        self.admin_role = ctx.guild.get_role(srv.admin_role) if srv and srv.admin_role else None
        self.mj_role = ctx.guild.get_role(srv.mj_role) if srv and srv.mj_role else None
        self._initial_admin_role = self.admin_role
        self._initial_mj_role = self.mj_role
        self.panel_msg: Optional[discord.Message] = None
        self.edit_role_msg: Optional[discord.WebhookMessage] = None
        self.buttons = [self.btn_set_prefix(), self.btn_set_admin_role(), self.btn_set_mj_role(), self.btn_close()]
        self._set_role = self.RoleID.ADMIN

        self.view_panel(DiscordEmbedMeta(
            title='TtgcBot',
            color='FF0000',
            descr=LocalizedStr('settings'),
            img=avatar,
            thumbnail='https://www.thetaleofgreatcosmos.fr/wp-content/uploads/2019/11/TTGC_Text.png',
            author=EmbedAuthorMeta(ctx.author.name, icon_url=avatar),
            footer=EmbedIconTextMeta(LocalizedStr('settings_footer'), bot_avatar),
            fields=[
                EmbedFieldMeta(LocalizedStr('prefix', treatment=LocalizeStrCase.CAPITALIZED), f'`/`'),
                EmbedFieldMeta(LocalizedStr('admin_role', treatment=LocalizeStrCase.CAPITALIZED), ':no_entry_sign:'),
                EmbedFieldMeta(LocalizedStr('mj_role', treatment=LocalizeStrCase.CAPITALIZED), ':no_entry_sign:')
            ]
        ))

        self.view_set_prefix()
        self.update_embed()

    @property
    def embed(self) -> DiscordEmbedMeta:
        view: EmbedView = self[self.SettingsViewID.PANEL] # type: ignore
        return view.embed

    @setup_view(SettingsViewID.PANEL)
    def view_panel(self, embed: DiscordEmbedMeta) -> View:
        view = EmbedView(embed, owner=self.owner)
        for btn in self.buttons:
            view += btn
        return view

    @setup_view(SettingsViewID.SET_PREFIX)
    def view_set_prefix(self) -> View:
        view = self.modal_set_prefix()
        view += TextInput(
            LocalizedStr('prefix', treatment=LocalizeStrCase.CAPITALIZED),
            placeholder=LocalizedStr('prefix', treatment=LocalizeStrCase.CAPITALIZED),
            default=self.srv.prefix,
            required=True,
            min_length=1,
            max_length=3,
            row=0
        )
        return view

    @setup_view(SettingsViewID.SET_ROLE)
    def view_set_role(self, cur_role: discord.Role) -> View:
        view = View(timeout=60, owner=self.owner, on_timeout=self.on_timeout)
        view += RoleDropdown(placeholder=LocalizedStr('role_select'), custom_id='role', row=0, default=cur_role, min_values=0)
        view += self.btn_validate_role()
        return view

    @override
    async def start(self, ctx: 'ExtendedContext') -> None:
        await self.localize(ctx)
        self.panel_msg = await self[self.SettingsViewID.PANEL].send(ctx)

    async def on_timeout(self, view: View) -> None:
        if self.edit_role_msg:
            await self.edit_role_msg.delete()
        if self.panel_msg:
            self.toggle_panel(True)
            await self.panel_msg.edit(view=self[self.SettingsViewID.PANEL])

    def toggle_panel(self, enabled: bool) -> None:
        for btn in self.buttons:
            btn.disabled = not enabled

    def update_embed(self) -> None:
        self.embed.fields[0].content = f'{self.prefix}'
        self.embed.fields[1].content = self.admin_role.mention if self.admin_role else ':no_entry_sign:'
        self.embed.fields[2].content = self.mj_role.mention if self.mj_role else ':no_entry_sign:'

    @button(style=discord.ButtonStyle.success, label=LocalizedStr('prefix', treatment=LocalizeStrCase.CAPITALIZED), row=0)
    async def btn_set_prefix(self, btn: Button, interaction: discord.Interaction) -> None:
        await interaction.response.send_modal(self[self.SettingsViewID.SET_PREFIX]) # type: ignore

    @button(style=discord.ButtonStyle.success, label=LocalizedStr('admin_role', treatment=LocalizeStrCase.CAPITALIZED), row=0)
    async def btn_set_admin_role(self, btn: Button, interaction: discord.Interaction) -> None:
        self.toggle_panel(False)
        await interaction.response.defer(ephemeral=True, thinking=True)

        self._set_role = self.RoleID.ADMIN
        view = self.view_set_role(self.admin_role)
        await view.localize(self.ctx)
        content = await localize(self.ctx, 'test')

        await interaction.followup.edit_message(self.panel_msg.id, view=self[self.SettingsViewID.PANEL]) # type: ignore
        self.edit_role_msg = await interaction.followup.send(content, view=view, wait=True)

    @button(style=discord.ButtonStyle.success, label=LocalizedStr('mj_role', treatment=LocalizeStrCase.CAPITALIZED), row=0)
    async def btn_set_mj_role(self, btn: Button, interaction: discord.Interaction) -> None:
        self.toggle_panel(False)
        await interaction.response.defer(ephemeral=True, thinking=True)

        self._set_role = self.RoleID.MJ
        view = self.view_set_role(self.mj_role)
        await view.localize(self.ctx)
        content = await localize(self.ctx, 'test')

        await interaction.followup.edit_message(self.panel_msg.id, view=self[self.SettingsViewID.PANEL]) # type: ignore
        self.edit_role_msg = await interaction.followup.send(content, view=view, ephemeral=True, wait=True)

    @button(style=discord.ButtonStyle.secondary,
            label=LocalizedStr('close', treatment=LocalizeStrCase.CAPITALIZED),
            row=0,
            emoji=Emoji.X)
    async def btn_close(self, btn: Button, interaction: discord.Interaction) -> None:
        self[self.SettingsViewID.PANEL].stop()
        await interaction.response.edit_message(view=None, delete_after=30)

        if not await self.finalize():
            await interaction.followup.send('ERROR')

    @modal(LocalizedStr(''))
    async def modal_set_prefix(self, modal: Modal, interaction: discord.Interaction) -> None:
        child = modal.get_first_child(TextInput)

        if prefix := child.value:
            self.prefix = prefix
            self.update_embed()

        await interaction.response.edit_message(embed=self.embed.convert(), view=self[self.SettingsViewID.PANEL])
        await self.view_set_prefix().localize(self.ctx)

    @button(style=discord.ButtonStyle.success,
            label=LocalizedStr('validate', treatment=LocalizeStrCase.CAPITALIZED),
            row=1,
            emoji=Emoji.HEAVY_CHECK_MARK)
    async def btn_validate_role(self, btn: Button, interaction: discord.Interaction) -> None:
        self.toggle_panel(True)
        await interaction.response.edit_message(content=':white_check_mark:', view=None, delete_after=5)
        role = self[self.SettingsViewID.SET_ROLE].find('role', RoleDropdown).value

        match self._set_role:
            case self.RoleID.ADMIN:
                self.admin_role = role
            case self.RoleID.MJ:
                self.mj_role = role

        self.update_embed()

        await interaction.followup.edit_message(
            self.panel_msg.id, # type: ignore
            embed=self.embed.convert(),
            view=self[self.SettingsViewID.PANEL]
        )

    @button(style=discord.ButtonStyle.danger,
            label=LocalizedStr('clear', treatment=LocalizeStrCase.CAPITALIZED),
            row=1,
            emoji=Emoji.WASTEBASKET)
    async def btn_clear_role(self, btn: Button, interaction: discord.Interaction) -> None:
        view = self[self.SettingsViewID.SET_ROLE]
        view.find('role', RoleDropdown).default_values = []
        await interaction.response.edit_message(view=view)

    @button(style=discord.ButtonStyle.secondary,
            label=LocalizedStr('cancel', treatment=LocalizeStrCase.CAPITALIZED),
            row=1,
            emoji=Emoji.X)
    async def btn_cancel_role(self, btn: Button, interaction: discord.Interaction) -> None:
        self.toggle_panel(True)
        await interaction.response.edit_message(content=':x:', view=None, delete_after=5)
        await interaction.followup.edit_message(
            self.panel_msg.id, # type: ignore
            view=self[self.SettingsViewID.PANEL]
        )

    @override
    async def finalize(self) -> bool:
        success = True
        owner_role = self.owner.get_role(self.srv.admin_role) # type: ignore

        if self.srv.admin_role != self.admin_role or self.srv.mj_role != self.mj_role:
            success = await self.srv.update_roles(
                self.owner.id,
                owner_role.id if owner_role else None,
                admin_role=self.admin_role.id, # type: ignore
                mj_role=self.mj_role.id # type: ignore
            )

        if self.srv.prefix != self.prefix:
            success = success and await self.srv.update_prefix(
                self.owner.id,
                owner_role.id if owner_role else None,
                self.prefix
            )

        return success
