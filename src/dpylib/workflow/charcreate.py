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


from typing import TYPE_CHECKING, Any, Optional, override
import discord
from lang import LocalizedStr, LocalizeStrCase
from utils.emojis import Emoji
from ..common.embed import DiscordEmbedMeta, EmbedAuthorMeta, EmbedFieldMeta
from ..common.threadholder import DiscordThreadHolder
from ..ui.components import Dropdown, DropdownOption, View, Button, Modal, TextInput, button, dropdown, modal
from ..ui import EmbedView
from .iworkflow import IWorkflow, setup_view

if TYPE_CHECKING:
    from ..common.contextext import ExtendedContext


class CharcreateWorkflow(IWorkflow[None]): # TODO: Change return type
    class CharcreateViewID(IWorkflow.ViewID):
        SELECT_EXT = 'select_ext'
        SELECT_RACE = 'select_race'
        SELECT_CLASS = 'select_class'
        SELECT_GMOD = 'select_gmod'
        SELECT_DKAR = 'select_dkar'
        VERIFY = 'verify'
        SET_VALUE = 'set_value'
        SET_PILOTING = 'set_piloting'
        SET_AFFILIATION = 'set_affiliation'
        SET_HYBRID = 'set_hybrid'
        SET_SYMBIONT = 'set_symbiont'

    def __init__(self, ctx: 'ExtendedContext', charkey: str) -> None:
        super().__init__()
        self.charkey = charkey
        self.owner = ctx.author
        self.ctx = ctx
        self.data: dict[str, Any] = {
            'name': self.charkey,
            'pv': 1,
            'pm': 0,
            'intuition': 3,
            'strength': 50,
            'spirit': 50,
            'charisma': 50,
            'agility': 50,
            'precision': 50,
            'luck': 50
        }
        self.ext = ''
        self.race = ''
        self.classe = ''
        self.field_map = ['name', 'hp', 'mp', 'str', 'spr', 'cha', 'agi', 'prec', 'luck', 'int', 'karma', 'gmod']
        self.thread: Optional[DiscordThreadHolder] = None

        self.view_select_ext()
        self.view_select_race()
        self.view_select_class()
        self.view_select_gmod()
        self.view_select_dkar()
        # self.view_set_stats_1()
        # self.view_set_stats_2()
        # self.view_set_stats_3()
        self.view_verify()
        self.view_set_value()

    @setup_view(CharcreateViewID.SELECT_EXT)
    def view_select_ext(self) -> View:
        view = View(timeout=300, owner=self.owner, on_timeout=self.on_timeout)
        dd = self.dropdown_ext()
        dd += [
            DropdownOption('ADTAF', 'adtaf'),
            DropdownOption('Cosmorigins Terae', 'terae'),
            DropdownOption('Cosmorings Orianis', 'orianis'),
            DropdownOption('Cosmorigins Xyord', 'xyord')
        ] # Hardcoded
        view += dd
        return view

    @setup_view(CharcreateViewID.SELECT_RACE)
    def view_select_race(self) -> View:
        view = View(timeout=300, owner=self.owner, on_timeout=self.on_timeout)
        dd = self.dropdown_race()
        dd += [
            DropdownOption('Humains', 'human'),
            DropdownOption('Descendant des anciens', 'ancient'),
        ] # Hardcoded
        view += dd
        return view

    @setup_view(CharcreateViewID.SELECT_CLASS)
    def view_select_class(self) -> View:
        view = View(timeout=300, owner=self.owner, on_timeout=self.on_timeout)
        dd = self.dropdown_class()
        dd += [
            DropdownOption('Standard', 'standard'),
            DropdownOption('Détenteur de mana', 'mana'),
        ] # Hardcoded
        view += dd
        return view

    @setup_view(CharcreateViewID.SELECT_GMOD)
    def view_select_gmod(self) -> View:
        view = View(timeout=300, owner=self.owner, on_timeout=self.on_timeout)
        view += self.btn_gmod_offensive()
        view += self.btn_gmod_defensive()
        return view

    @setup_view(CharcreateViewID.SELECT_DKAR)
    def view_select_dkar(self) -> View:
        view = View(timeout=300, owner=self.owner, on_timeout=self.on_timeout)
        view += self.btn_dkar_m5()
        view += self.btn_dkar_m4()
        view += self.btn_dkar_neutral()
        view += self.btn_dkar_4()
        view += self.btn_dkar_5()
        return view

    @setup_view(CharcreateViewID.SET_VALUE)
    def view_set_value(self) -> View:
        view = self.modal_set_value()
        view += TextInput(
            LocalizedStr('value', treatment=LocalizeStrCase.CAPITALIZED),
            placeholder=LocalizedStr('input_value_placeholder', treatment=LocalizeStrCase.CAPITALIZED),
            required=True,
            row=0,
            custom_id=''
        )
        return view

    @setup_view(CharcreateViewID.SET_PILOTING)
    def view_set_piloting(self) -> View:
        view = self.modal_set_piloting()
        view += TextInput(
            LocalizedStr('planet_piloting', treatment=LocalizeStrCase.CAPITALIZED),
            placeholder=LocalizedStr('input_value_placeholder', treatment=LocalizeStrCase.CAPITALIZED),
            required=False,
            max_length=2,
            row=0,
            cast=int,
            custom_id='planet'
        )
        view += TextInput(
            LocalizedStr('astral_piloting', treatment=LocalizeStrCase.CAPITALIZED),
            placeholder=LocalizedStr('input_value_placeholder', treatment=LocalizeStrCase.CAPITALIZED),
            required=False,
            max_length=2,
            row=1,
            cast=int,
            custom_id='astral'
        )
        return view

    # @setup_view(CharcreateViewID.SET_STATS_1)
    # def view_set_stats_1(self) -> View:
    #     def _check_values(view: View, interaction: discord.Interaction) -> bool:
    #         return input_hp.value and input_int.value and input_int.value <= 6 # type: ignore

    #     view = self.modal_set_stats_1()
    #     view += (input_hp := TextInput(
    #         LocalizedStr('hp', treatment=LocalizeStrCase.UPPER),
    #         default='1',
    #         required=True,
    #         min_length=1,
    #         max_length=5,
    #         row=0,
    #         cast=int,
    #         custom_id='hp'
    #     ))
    #     view += TextInput(
    #         LocalizedStr('mp', treatment=LocalizeStrCase.UPPER),
    #         placeholder='0',
    #         max_length=5,
    #         row=1,
    #         cast=int,
    #         custom_id='mp'
    #     )
    #     view += (input_int := TextInput(
    #         LocalizedStr('int', treatment=LocalizeStrCase.CAPITALIZED),
    #         default='3',
    #         required=True,
    #         min_length=1,
    #         max_length=1,
    #         row=2,
    #         cast=int,
    #         custom_id='int'
    #     ))
    #     view.checks.append(_check_values)
    #     return view

    # @setup_view(CharcreateViewID.SET_STATS_2)
    # def view_set_stats_2(self) -> View:
    #     def _check_values(view: View, interaction: discord.Interaction) -> bool:
    #         return input_str.value and input_spr.value and input_cha.value # type: ignore

    #     view = self.modal_set_stats_2()
    #     view += (input_str := TextInput(
    #         LocalizedStr('str', treatment=LocalizeStrCase.CAPITALIZED),
    #         default='50',
    #         required=True,
    #         min_length=2,
    #         max_length=2,
    #         row=0,
    #         cast=int,
    #         custom_id='str'
    #     ))
    #     view += (input_spr := TextInput(
    #         LocalizedStr('spr', treatment=LocalizeStrCase.CAPITALIZED),
    #         default='50',
    #         required=True,
    #         min_length=2,
    #         max_length=2,
    #         row=1,
    #         cast=int,
    #         custom_id='spr'
    #     ))
    #     view += (input_cha := TextInput(
    #         LocalizedStr('cha', treatment=LocalizeStrCase.CAPITALIZED),
    #         default='50',
    #         required=True,
    #         min_length=2,
    #         max_length=2,
    #         row=2,
    #         cast=int,
    #         custom_id='cha'
    #     ))
    #     view.checks.append(_check_values)
    #     return view

    # @setup_view(CharcreateViewID.SET_STATS_3)
    # def view_set_stats_3(self) -> View:
    #     def _check_values(view: View, interaction: discord.Interaction) -> bool:
    #         return input_agi.value and input_prec.value and input_luck.value # type: ignore

    #     view = self.modal_set_stats_3()
    #     view += (input_agi := TextInput(
    #         LocalizedStr('agi', treatment=LocalizeStrCase.CAPITALIZED),
    #         default='50',
    #         required=True,
    #         min_length=2,
    #         max_length=2,
    #         row=0,
    #         cast=int,
    #         custom_id='agi'
    #     ))
    #     view += (input_prec := TextInput(
    #         LocalizedStr('prec', treatment=LocalizeStrCase.CAPITALIZED),
    #         default='50',
    #         required=True,
    #         min_length=2,
    #         max_length=2,
    #         row=1,
    #         cast=int,
    #         custom_id='prec'
    #     ))
    #     view += (input_luck := TextInput(
    #         LocalizedStr('luck', treatment=LocalizeStrCase.CAPITALIZED),
    #         default='50',
    #         required=True,
    #         min_length=2,
    #         max_length=2,
    #         row=2,
    #         cast=int,
    #         custom_id='luck'
    #     ))
    #     view.checks.append(_check_values)
    #     return view

    @setup_view(CharcreateViewID.VERIFY)
    def view_verify(self) -> View:
        embed = DiscordEmbedMeta(
            title=LocalizedStr('charcreate_verify_title'),
            color='BF40BF',
            author=EmbedAuthorMeta(self.owner.name, icon_url=self.owner.display_avatar.url),
            footer=f'/char create {self.charkey}',
            fields=[EmbedFieldMeta(LocalizedStr(x, treatment=LocalizeStrCase.CAPITALIZED), '') for x in self.field_map]
        )
        view = EmbedView(timeout=None, owner=self.owner, embed=embed)
        view += self.btn_set_name()
        view += self.btn_set_hp()
        view += self.btn_set_mp()
        view += self.btn_set_str()
        view += self.btn_set_spr()
        view += self.btn_set_cha()
        view += self.btn_set_agi()
        view += self.btn_set_prec()
        view += self.btn_set_luck()
        view += self.btn_set_int()
        return view

    @override
    async def start(self, ctx: 'ExtendedContext') -> None:
        self.thread = DiscordThreadHolder(ctx.channel, private=False)
        content = f'Starting creation of character {self.charkey}...'
        msg = None

        if self.thread.needs_message:
            msg = await ctx.send(content)
            msg = await ctx.channel.fetch_message(msg.id)

        thread = await self.thread.spawn(f'/char create {self.charkey}', origin_msg=msg, post_content=content)
        await thread.send(view=self[self.CharcreateViewID.SELECT_EXT])
        # if isinstance(ctx.channel, discord.TextChannel):
        #     msg = await ctx.send(f'Starting creation of character {self.charkey}...')
        #     msg = await ctx.channel.fetch_message(msg.id)
        #     thread = await msg.create_thread(
        #         name=f'/char create {self.charkey}',
        #         auto_archive_duration=60
        #     )
        #     await thread.send(view=self[self.CharcreateViewID.SELECT_EXT])
        # elif isinstance(ctx.channel, discord.Thread):
        #     thread = ctx.channel
        #     await thread.edit(archived=False, locked=False, reason=f'/char create {self.charkey}')
        #     await self[self.CharcreateViewID.SELECT_EXT].send(ctx)
        # else:
        #     raise Exception('TEMP') # TODO: proper exception

    async def on_timeout(self, view: View) -> None:
        pass

    @dropdown(options=[], placeholder=LocalizedStr('charcreate_ext_dd'))
    async def dropdown_ext(self, dd: Dropdown, interaction: discord.Interaction) -> None:
        self[self.CharcreateViewID.SELECT_EXT].stop()
        self.ext = dd.value
        await interaction.response.send_message(view=self[self.CharcreateViewID.SELECT_RACE])

        if interaction.message:
            await interaction.followup.edit_message(interaction.message.id, view=None, content=f':white_check_mark: Selected extension: {self.ext}')

    @dropdown(options=[], placeholder=LocalizedStr('charcreate_race_dd'))
    async def dropdown_race(self, dd: Dropdown, interaction: discord.Interaction) -> None:
        self[self.CharcreateViewID.SELECT_RACE].stop()
        self.race = dd.value
        await interaction.response.send_message(view=self[self.CharcreateViewID.SELECT_CLASS])

        if interaction.message:
            await interaction.followup.edit_message(interaction.message.id, view=None, content=f':white_check_mark: Selected race: {self.race}')

    @dropdown(options=[], placeholder=LocalizedStr('charcreate_class_dd'))
    async def dropdown_class(self, dd: Dropdown, interaction: discord.Interaction) -> None:
        self[self.CharcreateViewID.SELECT_CLASS].stop()
        self.classe = dd.value
        await interaction.response.send_message(view=self[self.CharcreateViewID.SELECT_GMOD])

        if interaction.message:
            await interaction.followup.edit_message(interaction.message.id, view=None, content=f':white_check_mark: Selected class: {self.classe}')

    async def btn_gmod(self, interaction: discord.Interaction, value: str) -> None:
        self[self.CharcreateViewID.SELECT_GMOD].stop()
        self.data['gamemod'] = value
        await interaction.response.send_message(view=self[self.CharcreateViewID.SELECT_DKAR])

        if interaction.message:
            await interaction.followup.edit_message(interaction.message.id, view=self[self.CharcreateViewID.SELECT_GMOD])

    @button(style=discord.ButtonStyle.danger,
            label=LocalizedStr('gmod_offensive', treatment=LocalizeStrCase.CAPITALIZED),
            emoji=Emoji.CROSSED_SWORDS,
            row=0)
    async def btn_gmod_offensive(self, btn: Button, interaction: discord.Interaction) -> None:
        await self.btn_gmod(interaction, 'offensive')

    @button(style=discord.ButtonStyle.success,
            label=LocalizedStr('gmod_defensive', treatment=LocalizeStrCase.CAPITALIZED),
            emoji=Emoji.SHIELD,
            row=0)
    async def btn_gmod_defensive(self, btn: Button, interaction: discord.Interaction) -> None:
        await self.btn_gmod(interaction, 'defensive')

    async def btn_dkar(self, interaction: discord.Interaction, value: int) -> None:
        self[self.CharcreateViewID.SELECT_DKAR].stop()
        self.data['karma'] = value
        await self.send_verification(interaction)

        if interaction.message:
            await interaction.followup.edit_message(interaction.message.id, view=self[self.CharcreateViewID.SELECT_DKAR])

    @button(style=discord.ButtonStyle.danger, label='-5', row=0)
    async def btn_dkar_m5(self, btn: Button, interaction: discord.Interaction) -> None:
        await self.btn_dkar(interaction, -5)

    @button(style=discord.ButtonStyle.danger, label='-4', row=0)
    async def btn_dkar_m4(self, btn: Button, interaction: discord.Interaction) -> None:
        await self.btn_dkar(interaction, -4)

    @button(style=discord.ButtonStyle.primary, label='0', row=0)
    async def btn_dkar_neutral(self, btn: Button, interaction: discord.Interaction) -> None:
        await self.btn_dkar(interaction, 0)

    @button(style=discord.ButtonStyle.success, label='4', row=0)
    async def btn_dkar_4(self, btn: Button, interaction: discord.Interaction) -> None:
        await self.btn_dkar(interaction, 4)

    @button(style=discord.ButtonStyle.success, label='5', row=0)
    async def btn_dkar_5(self, btn: Button, interaction: discord.Interaction) -> None:
        await self.btn_dkar(interaction, 5)

    async def send_verification(self, interaction: discord.Interaction, edit: bool = False) -> None:
        view: EmbedView = self[self.CharcreateViewID.VERIFY] # type: ignore
        view.embed.descr = f'{self.ext}\n{self.race} {self.classe}'
        view.embed.fields[self.field_map.index('name')].content = self.data['name']
        view.embed.fields[self.field_map.index('hp')].content = str(self.data['pv'])
        view.embed.fields[self.field_map.index('mp')].content = str(self.data['pm'])
        view.embed.fields[self.field_map.index('str')].content = str(self.data['strength'])
        view.embed.fields[self.field_map.index('spr')].content = str(self.data['spirit'])
        view.embed.fields[self.field_map.index('cha')].content = str(self.data['charisma'])
        view.embed.fields[self.field_map.index('agi')].content = str(self.data['agility'])
        view.embed.fields[self.field_map.index('prec')].content = str(self.data['precision'])
        view.embed.fields[self.field_map.index('luck')].content = str(self.data['luck'])
        view.embed.fields[self.field_map.index('int')].content = str(self.data['intuition'])
        view.embed.fields[self.field_map.index('karma')].content = str(self.data['karma'])
        view.embed.fields[self.field_map.index('gmod')].content = self.data['gamemod']

        if edit:
            await interaction.response.edit_message(view=view, embed=view.embed.convert())
        else:
            await interaction.response.send_message(view=view, embed=view.embed.convert())

    async def btn_set(self, interaction: discord.Interaction, key: str, **params) -> None:
        view: Modal = self[self.CharcreateViewID.SET_VALUE] # type: ignore
        input_field = view.get_first_child(TextInput)
        input_field.custom_id = key
        input_field.min_length = params.get('min_length', 1)
        input_field.max_length = params.get('max_length', None)
        input_field.cast = params.get('cast', str)
        input_field.default = self.data.get(key, None)

        if 'check' in params:
            view.checks.append(params.get('check')) # type: ignore

        await interaction.response.send_modal(view)
        self.view_set_value()
        await self[self.CharcreateViewID.SET_VALUE].localize(self.ctx)

    @button(style=discord.ButtonStyle.primary, label=LocalizedStr('set_name'), emoji=Emoji.PASSPORT_CONTROL)
    async def btn_set_name(self, btn: Button, interaction: discord.Interaction) -> None:
        await self.btn_set(interaction, 'name', max_length=25)

    @button(style=discord.ButtonStyle.primary, label=LocalizedStr('set_hp'), emoji=Emoji.PILL)
    async def btn_set_hp(self, btn: Button, interaction: discord.Interaction) -> None:
        def _check_hp(self, modal: Modal, interaction: discord.Interaction) -> bool:
            child = modal.get_first_child(TextInput)
            return child.value and child.value > 0 # type: ignore

        await self.btn_set(interaction, 'pv', cast=int, check=_check_hp)

    @button(style=discord.ButtonStyle.primary, label=LocalizedStr('set_mp'), emoji=Emoji.MAGIC_WAND)
    async def btn_set_mp(self, btn: Button, interaction: discord.Interaction) -> None:
        def _check_mp(self, modal: Modal, interaction: discord.Interaction) -> bool:
            child = modal.get_first_child(TextInput)
            return child.value and child.value >= 0 # type: ignore

        await self.btn_set(interaction, 'pm', cast=int, check=_check_mp)

    def _check_stat(self, modal: Modal, interaction: discord.Interaction) -> bool:
        child = modal.get_first_child(TextInput)
        return child.value and child.value > 0 and child.value < 100 # type: ignore

    @button(style=discord.ButtonStyle.primary, label=LocalizedStr('set_str'), emoji=Emoji.MUSCLE)
    async def btn_set_str(self, btn: Button, interaction: discord.Interaction) -> None:
        await self.btn_set(interaction, 'strength', max_length=2, cast=int, check=self._check_stat)

    @button(style=discord.ButtonStyle.primary, label=LocalizedStr('set_spr'), emoji=Emoji.GHOST)
    async def btn_set_spr(self, btn: Button, interaction: discord.Interaction) -> None:
        await self.btn_set(interaction, 'spirit', max_length=2, cast=int, check=self._check_stat)

    @button(style=discord.ButtonStyle.primary, label=LocalizedStr('set_cha'), emoji=Emoji.HEART_EYES)
    async def btn_set_cha(self, btn: Button, interaction: discord.Interaction) -> None:
        await self.btn_set(interaction, 'charisma', max_length=2, cast=int, check=self._check_stat)

    @button(style=discord.ButtonStyle.primary, label=LocalizedStr('set_agi'), emoji=Emoji.CLOUD_TORNADO)
    async def btn_set_agi(self, btn: Button, interaction: discord.Interaction) -> None:
        await self.btn_set(interaction, 'agility', max_length=2, cast=int, check=self._check_stat)

    @button(style=discord.ButtonStyle.primary, label=LocalizedStr('set_prec'), emoji=Emoji.DART)
    async def btn_set_prec(self, btn: Button, interaction: discord.Interaction) -> None:
        await self.btn_set(interaction, 'precision', max_length=2, cast=int, check=self._check_stat)

    @button(style=discord.ButtonStyle.primary, label=LocalizedStr('set_luck'), emoji=Emoji.FOUR_LEAF_CLOVER)
    async def btn_set_luck(self, btn: Button, interaction: discord.Interaction) -> None:
        await self.btn_set(interaction, 'luck', max_length=2, cast=int, check=self._check_stat)

    @button(style=discord.ButtonStyle.primary, label=LocalizedStr('set_int'), emoji=Emoji.EYES)
    async def btn_set_int(self, btn: Button, interaction: discord.Interaction) -> None:
        def _check_int(self, modal: Modal, interaction: discord.Interaction) -> bool:
            child = modal.get_first_child(TextInput)
            return child.value and child.value > 0 and child.value <= 6 # type: ignore

        await self.btn_set(interaction, 'intuition', max_length=1, cast=int, check=_check_int)

    @modal(LocalizedStr('charcreate_setval_modal'))
    async def modal_set_value(self, modal: Modal, interaction: discord.Interaction) -> None:
        child = modal.get_first_child(TextInput)

        if child.custom_id and child.value:
            self.data[child.custom_id] = child.value

        await self.send_verification(interaction, True)

    @button(style=discord.ButtonStyle.primary, label=LocalizedStr('set_piloting'), emoji=Emoji.ROCKET)
    async def btn_set_piloting(self, btn: Button, interaction: discord.Interaction) -> None:
        view: Modal = self[self.CharcreateViewID.SET_PILOTING] # type: ignore
        await interaction.response.send_modal(view)
        self.view_set_piloting()
        await self[self.CharcreateViewID.SET_PILOTING].localize(self.ctx)

    @modal(LocalizedStr('charcreate_set_pilot'))
    async def modal_set_piloting(self, modal: Modal, interaction: discord.Interaction) -> None:
        planet_input = modal.find('planet', TextInput)
        astral_input = modal.find('astral', TextInput)
        self.data['pilot'] = {}

        if planet_input:
            self.data['pilot']['planet'] = planet_input.value
        if astral_input:
            self.data['pilot']['astral'] = planet_input.value

        await self.send_verification(interaction, True)

    # @modal(LocalizedStr('charcreate_setstat_modal'))
    # async def modal_set_stats_1(self, modal: Modal, interaction: discord.Interaction) -> None:
    #     self.data.update({
    #         'pv': modal.find('hp', TextInput).value,
    #         'pm': modal.find('mp', TextInput).value,
    #         'intuition': modal.find('int', TextInput).value
    #     })

    #     await interaction.response.send_modal(self[self.CharcreateViewID.SET_STATS_2]) # type: ignore

    # @modal(LocalizedStr('charcreate_setstat_modal'))
    # async def modal_set_stats_2(self, modal: Modal, interaction: discord.Interaction) -> None:
    #     self.data.update({
    #         'strength': modal.find('str', TextInput).value,
    #         'spirit': modal.find('spr', TextInput).value,
    #         'charisma': modal.find('cha', TextInput).value
    #     })

    #     await interaction.response.send_modal(self[self.CharcreateViewID.SET_STATS_3]) # type: ignore

    # @modal(LocalizedStr('charcreate_setstat_modal'))
    # async def modal_set_stats_3(self, modal: Modal, interaction: discord.Interaction) -> None:
    #     self.data.update({
    #         # TODO: temp, remove later
    #         'pv': 100,
    #         'pm': 0,
    #         'intuition': 2,
    #         'strength': 60,
    #         'spirit': 60,
    #         'charisma': 60,
    #         # END OF REMOVAL
    #         'agility': modal.find('agi', TextInput).value,
    #         'precision': modal.find('prec', TextInput).value,
    #         'luck': modal.find('luck', TextInput).value,
    #     })

    #     view: EmbedView = self[self.CharcreateViewID.VERIFY] # type: ignore
    #     view.embed.descr = f'{self.ext}\n{self.race} {self.classe}'
    #     view.embed.fields[self.field_map.index('name')].content = self.data['name']
    #     view.embed.fields[self.field_map.index('hp')].content = str(self.data['pv'])
    #     view.embed.fields[self.field_map.index('mp')].content = str(self.data['pm'])
    #     view.embed.fields[self.field_map.index('str')].content = str(self.data['strength'])
    #     view.embed.fields[self.field_map.index('spr')].content = str(self.data['spirit'])
    #     view.embed.fields[self.field_map.index('cha')].content = str(self.data['charisma'])
    #     view.embed.fields[self.field_map.index('agi')].content = str(self.data['agility'])
    #     view.embed.fields[self.field_map.index('prec')].content = str(self.data['precision'])
    #     view.embed.fields[self.field_map.index('luck')].content = str(self.data['luck'])
    #     view.embed.fields[self.field_map.index('int')].content = str(self.data['intuition'])
    #     view.embed.fields[self.field_map.index('karma')].content = str(self.data['karma'])
    #     view.embed.fields[self.field_map.index('gmod')].content = self.data['gamemod']
    #     await interaction.response.send_message(view=view, embed=view.embed.convert())

    @override
    async def finalize(self) -> None:
        pass
