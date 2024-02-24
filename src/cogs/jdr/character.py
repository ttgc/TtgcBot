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

# from src.utils.checks import *
# from src.tools.BotTools import *
from discord.ext import commands
# import logging,asyncio
# import functools
# import concurrent.futures
import discord
import asyncio
from core.commandparameters import GenericCommandParameters
from setup.loglevel import LogLevel
from utils import async_lambda, async_conditional_lambda, try_parse_int, get_color
from utils.checks import check_jdrchannel, check_haschar, check_chanmj
from utils.converters import CharacterConverter
from utils.emojis import Emoji
from models import Character
from models.enums import AutoPopulatedEnums, AttributeTag
from exceptions import HTTPErrorCode
from network import safe_request
# from src.tools.Translator import *
# from src.tools.Character import *
# from src.tools.CharacterUtils import *
# from src.utils.converters import *
# from src.tools.parsingdice import *
# from src.exceptions.exceptions import APIException
# import typing
# from random import randint
# import os
import discordui as ui

class CharacterCog(commands.Cog, name="Characters"):
    def __init__(self, bot, logger):
        self.bot = bot
        self.logger = logger

    @commands.check(check_jdrchannel)
    @commands.hybrid_group(invoke_without_command=False, aliases=['char'])
    async def character(self, ctx): pass

    @commands.check(check_haschar)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @character.command(name="select", aliases=["switch"])
    async def character_select(self, ctx): #(self, ctx, key)
        """**PC/PJ only**
        Select a character from all characters linked to you"""
        data = await GenericCommandParameters.get_from_context(ctx)
        current_char = await data.char
        chars = []

        async for i in data.charbase.get("linked", []):
            if i.get("member", -1) == ctx.author.id:
                chars.append(i.get("charkey"))

        success, selection = await ui.send_dropdown(ctx, placeholder=data.lang["dropdown_char_placeholder"], timeout=60, options=chars, select_msg=data.lang["charselect"], timeout_msg=data.lang["timeout"], format_args_before=[current_char.key])

        if success and selection != current_char.key:
            jdr = await data.jdr
            to_select = Character(charkey=selection, linked=ctx.author.id)
            to_select.bind(jdr)
            await to_select.select(ctx.author.id)
            self.logger.log(LogLevel.DEBUG.value, "/charselect (%s -> %s) in channel %d of server %d", current_char.key, selection, ctx.channel.id, ctx.guild.id)
            # await ctx.channel.send(data.lang["charselect"].format(data.char.key, i.key))

    @commands.check(check_chanmj)
    @character.command(name="link", aliases=["assign"])
    async def character_link(self, ctx):
        """**GM/MJ only**
        Link a character with a member of your RP/JDR. This member will be able to use all commands related to the character linked (command specified as 'PC/PJ only')"""
        data = await GenericCommandParameters.get_from_context(ctx)
        view = ui.views.View(ctx, timeout=60)
        chars = await data.charbase.get("characters", [])

        char_dd = ui.Dropdown(ctx, view, id="chars", placeholder=data.lang["dropdown_char_placeholder"], row=0, options=chars)
        user_dd = ui.Dropdown(ctx, view, id="users", placeholder=data.lang["dropdown_user_placeholder"], row=1)

        for i in ctx.channel.members:
            if not i.bot:
                user_dd.add_option(label=str(i), value=i.id)

        on_cancel = async_lambda(lambda b, i: i.response.edit_message(content=data.lang["canceled"], view=None))
        submit_check = lambda b, i: char_dd.value is not None and user_dd.value is not None
        on_submit = async_conditional_lambda(
            asyncio.coroutine(lambda b, i: b.final),
            lambda b, i: i.response.edit_message(content=Emoji.HOURGLASS, view=None),
            lambda b, i: i.response.edit_message(content=data.lang["submit_failed"], view=b.view)
        )

        ui.DefaultButtons.CANCEL.spawn(view, label=data.lang["btn_cancel"], row=2, onclick=on_cancel)
        ui.DefaultButtons.SUBMIT.spawn(view, label=data.lang["btn_submit"], row=2, onclick=on_submit, finalize_check=submit_check)
        msg = await ctx.send(view=view, reference=ctx.message)
        timeout = await view.wait()

        if timeout:
            await msg.edit(content=data.lang["timeout"], view=None)
        elif view.result.is_success:
            jdr = await data.jdr
            character = Character(charkey=char_dd.value)
            character.bind(jdr)
            error = await safe_request(character.link(user_dd.value, ctx.author.id), HTTPErrorCode.CONFLICT, HTTPErrorCode.FORBIDDEN)

            if error is None:
                await msg.edit(content=data.lang["charlink"].format(character.key, user_dd.value))
                self.logger.log(LogLevel.DEBUG.value, "/charlink in channel %d of server %d between %s and %d", ctx.channel.id, ctx.guild.id, character.key, user_dd.value)
            elif error == HTTPErrorCode.CONFLICT:
                await msg.edit(content=data.lang["charlink_conflict"].format(character.key))
            else:
                await msg.edit(content=data.lang["is_dead"].format(character.key))

    @commands.check(check_chanmj)
    @character.command(name="hybrid", aliases=["transgenic", "transgenique", "hybride"])
    async def character_hybrid(self, ctx, char: CharacterConverter): #, *, race: RaceConverter):
        """**GM/MJ only**
        Set a character as an hybrid, give him a second race and inherit all race's skills.
        This won't work if the character is already an hybrid"""
        data = await GenericCommandParameters.get_from_context(ctx)
        Races = await AutoPopulatedEnums().get_races(char.extension)
        filtered_races = Races.to_dict(lambda r: str(r) != str(char.race))
        success, selection = await ui.send_dropdown(ctx, placeholder=data.lang["dropdown_race_placeholder"], timeout=60, options=filtered_races, select_msg=data.lang["char_hybrid"], timeout_msg=data.lang["timeout"], format_args_before=[char, char.race])

        if success:
            char = await char.makehybrid(Races(selection), ctx.author.id)
            self.logger.log(LogLevel.DEBUG.value, "/charhybrid (%s) in channel %d of server %d", char.key, ctx.channel.id, ctx.guild.id)

    @commands.check(check_chanmj)
    @character.command(name="symbiont", aliases=["symbiote", "symb", "sb"])
    async def character_symbiont(self, ctx, char: CharacterConverter): #, *, symbiont: typing.Optional[SymbiontConverter] = None):
        """**GM/MJ only**
        Attach a symbiont to a character, if no symbiont is provided clear any symbiont from this character."""
        data = await GenericCommandParameters.get_from_context(ctx)
        Symbionts = await AutoPopulatedEnums().get_symbionts(char.extension)
        sb_dict = {None: data.lang["none_m"]}
        sb_dict.update({sb.name: sb.value for sb in Symbionts})
        submit_callback = async_conditional_lambda(
            asyncio.coroutine(lambda dd, i: dd.value is None),
            lambda dd, i: i.response.edit_message(content=data.lang["char_nosymbiont"].format(char.name), view=None),
            lambda dd, i: i.response.edit_message(content=data.lang["char_symbiont"].format(char.name, dd.value), view=None)
        )

        success, selection = await ui.send_dropdown_custom_submit(ctx, placeholder=data.lang["dropdown_symbiont_placeholder"], timeout=60, options=sb_dict, on_submit=submit_callback, timeout_msg=data.lang["timeout"])
        if success:
            char = await char.setsymbiont(Symbionts(selection) if selection is not None else None, ctx.author.id)
            self.logger.log(LogLevel.DEBUG.value, "/charsymbiont (%s) in channel %d of server %d", char.key, ctx.channel.id, ctx.guild.id)

    @commands.check(check_chanmj)
    @character.command(name="affiliation", aliases=["organization", "organisation", "org"])
    async def character_affiliation(self, ctx, char: CharacterConverter): #, affiliation: typing.Optional[AffiliationConverter] = None):
        """**GM/MJ only**
        Affiliate the character with the specified organization, the organization should exists.
        This will automatically include all skills related to the organization.
        If no organization is provided, then the current character's affiliation will be removed."""
        data = await GenericCommandParameters.get_from_context(ctx)
        Organizations = await AutoPopulatedEnums().get_orgs(char.extension)
        org_dict = {None: data.lang["none"]}
        org_dict.update({org.name: org.value for org in Organizations})
        submit_callback = async_conditional_lambda(
            asyncio.coroutine(lambda dd, i: dd.value is None),
            lambda dd, i: i.response.edit_message(content=data.lang["unaffiliate"].format(char.name), view=None),
            lambda dd, i: i.response.edit_message(data.lang["affiliate"].format(char.name, dd.value), view=None)
        )

        success, selection = await ui.send_dropdown_custom_submit(ctx, placeholder=data.lang["dropdown_org_placeholder"], timeout=60, options=org_dict, on_submit=submit_callback, timeout_msg=data.lang["timeout"])
        if success:
            char = await char.affiliate(Organizations(selection) if selection is not None else None, ctx.author.id)
            self.logger.log(LogLevel.DEBUG.value, "/char affiliate (%s with %s) in channel %d of server %d", char.key, selection, ctx.channel.id, ctx.guild.id)

    @commands.check(check_chanmj)
    @character.command(name="set")
    async def character_set(self, ctx, char: CharacterConverter): #(self, ctx, key)
        """**PC/PJ only**"""
        async def _send_modal(btn, interaction):
            if AttributeTag(set_dd.value).isnumeric():
                result = int(btns_view.result)
                if result > 0:
                    val_field.label = data.lang["value_input"].format(data.lang['add'])
                elif result < 0:
                    val_field.label = data.lang["value_input"].format(data.lang['remove'])

            interaction.response.send_modal(modal)

        data = await GenericCommandParameters.get_from_context(ctx)
        if char.dead:
            await ctx.channel.send(data.lang["is_dead"].format(char.name))

        modal = ui.views.Modal(ctx, "/character set", timeout=60)
        val_field = ui.TextInput(ctx, modal, data.lang["value_input"].format(data.lang['set']), placeholder=data.lang["value"], minlen=1, maxlen=4)

        btns_view = ui.views.ButtonGroup(ctx, 'operation', timeout=60)
        ui.DefaultButtons.REMOVE.spawn(btns_view, onclick=_send_modal)
        ui.DefaultButtons.SET.spawn(btns_view, onclick=_send_modal)
        ui.DefaultButtons.ADD.spawn(btns_view, onclick=_send_modal)

        settable = AttributeTag.get_charset(lang=data.lang)
        on_select = async_conditional_lambda(
            asyncio.coroutine(lambda dd, i: AttributeTag(dd.value).isnumeric()),
            lambda dd, i: i.response.edit_message(view=btns_view),
            _send_modal
        )
        set_dd = ui.StandaloneDropdown(ctx, placeholder=data.lang["dropdown_charset_placeholder"], timeout=60, options=[i.capitalize() for i in settable], onselection=on_select)

        msg = await ctx.send(view=set_dd.view, reference=ctx.message)
        timeout = await set_dd.wait()

        if not timeout:
            timeout = await btns_view.wait()
            if not timeout:
                await msg.edit(content=Emoji.HOURGLASS, view=None)
                timeout = await modal.wait()

        if timeout:
            await msg.edit(content=data.lang["timeout"], view=None)
        else:
            tag = AttributeTag(set_dd.value)
            value = val_field.value
            got = data.lang["new_value"]
            stat = tag.translate(data.lang)
            op = None

            if tag.isnumeric():
                value = try_parse_int(val_field.value, tag.get_attribute(char))
                res = int(btns_view.result)

                if res > 0:
                    value += tag.get_attribute_or_default(char, 0)
                    got = data.lang["recovered"]
                    op = '+'
                elif res < 0:
                    value = tag.get_attribute_or_default(char, 0) - value
                    got = data.lang["lost"]
                    op = '-'

            char.charrset(ctx.author.id, {tag: value})
            final_value = tag.get_attribute_or_default(char, value)
            embd = discord.Embed(title=char, description=data.lang["charset"].format(got, stat), colour=get_color('5B005B'))
            embd.set_footer(text="The Tale of Great Cosmos")
            embd.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
            embd.set_thumbnail(url="https://www.thetaleofgreatcosmos.fr/wp-content/uploads/2019/11/TTGC_Text.png")
            if op is not None:
                embd.add_field(name=data.lang["charset_amount"].format(stat, got), value=str(value), inline=True)
            embd.add_field(name=data.lang["charset_current"].format(stat), value=str(final_value), inline=True)

            await msg.edit(content=None, embed=embd, view=None)
            self.logger.info(f"set {set_dd.value} for {char} to {final_value} ({op if op is not None else '='}{value})")
