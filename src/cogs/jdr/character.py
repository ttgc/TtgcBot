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
# import discord
import asyncio
from core.commandparameters import GenericCommandParameters
from utils import async_lambda, async_conditional_lambda
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

    #@commands.check(check_jdrchannel)
    @commands.hybrid_group(invoke_without_command=False, aliases=['char'])
    async def character(self, ctx): pass

    #@commands.check(check_haschar)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @character.command(name="select", aliases=["switch"])
    async def character_select(self, ctx): #(self, ctx, key)
        """**PC/PJ only**
        Select a character from all characters linked to you"""
        # data = await GenericCommandParameters(ctx)
        # for i in self.charbase.get("linked", []):
        #     if i.get("charkey") == key and i.get("member") == ctx.author.id:
        #         await i.select(ctx.author.id)
        #         self.logger.log(logging.DEBUG+1,"/charselect (%s -> %s) in channel %d of server %d", data.char.key, i.key, ctx.channel.id, ctx.guild.id)
        #         await ctx.channel.send(data.lang["charselect"].format(data.char.key, i.key))
        #         return
        # await ctx.channel.send(data.lang["charnotexist"].format(key))
        data = await GenericCommandParameters.get_from_context(ctx)
        chars = ["Sora", "Igor", "Akane"]### HARDCODED - TO BE REMOVED
        success, selection = await ui.send_dropdown(ctx, placeholder=data.lang["dropdown_char_placeholder"], timeout=60, options=chars, select_msg=data.lang["charselect"], timeout_msg=data.lang["timeout"], format_args_before=["undefined"])

        if success:
            self.logger.info(selection)

    #@commands.check(check_chanmj)
    @character.command(name="link", aliases=["assign"])
    async def character_link(self, ctx):
        """**GM/MJ only**
        Link a character with a member of your RP/JDR. This member will be able to use all commands related to the character linked (command specified as 'PC/PJ only')"""
        data = await GenericCommandParameters.get_from_context(ctx)
        view = ui.views.View(ctx, timeout=60)
        chars = ["Sora", "Igor", "Akane"]### HARDCODED - TO BE REMOVED
        char_dd = ui.Dropdown(ctx, view, id="chars", placeholder=data.lang["dropdown_char_placeholder"], row=0, options=chars)
        user_dd = ui.Dropdown(ctx, view, id="users", placeholder=data.lang["dropdown_user_placeholder"], row=1)

        for i in ctx.channel.members:
            if not i.bot:
                user_dd.add_option(label=str(i), value=i.id)

        on_cancel = async_lambda(lambda b, i: i.response.edit_message(content=data.lang["canceled"], view=None))
        submit_check = lambda b, i: char_dd.value is not None and user_dd.value is not None
        on_submit = async_conditional_lambda(
            asyncio.coroutine(lambda b, i: b.final),
            lambda b, i: i.response.edit_message(content=data.lang["charlink"].format(char_dd.value, user_dd.value), view=None),
            lambda b, i: i.response.edit_message(content=data.lang["submit_failed"], view=b.view)
        )

        ui.DefaultButtons.CANCEL.spawn(view, label=data.lang["btn_cancel"], row=2, onclick=on_cancel)
        ui.DefaultButtons.SUBMIT.spawn(view, label=data.lang["btn_submit"], row=2, onclick=on_submit, finalize_check=submit_check)
        msg = await ctx.send(view=view, reference=ctx.message)
        timeout = await view.wait()

        if timeout:
            await msg.delete()
            await ctx.send(data.lang["timeout"], reference=ctx.message)
        elif view.result.is_success:
            self.logger.info(f"linked {char_dd.value} to {user_dd.value}")

        # try:
        #     await character.link(player.id, ctx.author.id, override)
        # except APIException as e:
        #     if e["code"] == 409:
        #         await ctx.channel.send(data.lang["charlink_conflict"].format(character.name))
        #     elif e["code"] == 403:
        #         await ctx.channel.send(data.lang["is_dead"].format(character.name))
        #     else:
        #         raise e
        #     return
        # finally:
        #     self.logger.log(logging.DEBUG+1, "/charlink in channel %d of server %d between %s and %d", ctx.channel.id, ctx.guild.id, character.key, player.id)
        #
        # await ctx.channel.send(data.lang["charlink"].format(character.name, player.mention))

    #@commands.check(check_chanmj)
    @character.command(name="hybrid", aliases=["transgenic", "transgenique", "hybride"])
    async def character_hybrid(self, ctx, char):#: CharacterConverter, *, race: RaceConverter):
        """**GM/MJ only**
        Set a character as an hybrid, give him a second race and inherit all race's skills.
        This won't work if the character is already an hybrid"""
        data = await GenericCommandParameters.get_from_context(ctx)
        races = ["Grits", "Alfys", "Nyfis", "Zyrfis", "Darfys", "Idylis", "Alwenys", "Vampirys", "Lythis"]### HARDCODED - TO BE REMOVED
        success, selection = await ui.send_dropdown(ctx, placeholder=data.lang["dropdown_race_placeholder"], timeout=60, options=races, select_msg=data.lang["char_hybrid"], timeout_msg=data.lang["timeout"], format_args_before=[char, "Grits (fake)"])

        if success:
            self.logger.info(selection)
        # char = char.makehybrid(race)
        # self.logger.log(logging.DEBUG+1, "/charhybrid (%s) in channel %d of server %d", char.key, ctx.message.channel.id, ctx.message.guild.id)
        # await ctx.message.channel.send(data.lang["char_hybrid"].format(char.name, char.race, char.hybrid_race))

    #@commands.check(check_chanmj)
    @character.command(name="symbiont", aliases=["symbiote", "symb", "sb"])
    async def character_symbiont(self, ctx, char):#: CharacterConverter, *, symbiont: typing.Optional[SymbiontConverter] = None):
        """**GM/MJ only**
        Attach a symbiont to a character, if no symbiont is provided clear any symbiont from this character."""
        data = await GenericCommandParameters.get_from_context(ctx)
        symbionts = [data.lang["none_m"], "Azort", "Iridyanis", "Enairo", "Horya", "Manahil"]### HARDCODED - TO BE REMOVED
        success, selection = await ui.send_dropdown(ctx, placeholder=data.lang["dropdown_symbiont_placeholder"], timeout=60, options=symbionts, select_msg=data.lang["char_symbiont"], timeout_msg=data.lang["timeout"], format_args_before=[char])

        if success:
            self.logger.info(selection)
        # char = char.setsymbiont(symbiont)
        # self.logger.log(logging.DEBUG+1, "/charsymbiont (%s) in channel %d of server %d", char.key, ctx.message.channel.id, ctx.message.guild.id)
        # if char.symbiont is None:
        #     await ctx.message.channel.send(data.lang["char_nosymbiont"].format(char.name))
        # else:
        #     await ctx.message.channel.send(data.lang["char_symbiont"].format(char.name, char.symbiont))

    #@commands.check(check_chanmj)
    @character.command(name="affiliation", aliases=["organization", "organisation", "org"])
    async def character_affiliation(self, ctx, char):#: CharacterConverter, affiliation: typing.Optional[AffiliationConverter] = None):
        """**GM/MJ only**
        Affiliate the character with the specified organization, the organization should exists.
        This will automatically include all skills related to the organization.
        If no organization is provided, then the current character's affiliation will be removed."""
        data = await GenericCommandParameters.get_from_context(ctx)
        orgs = [data.lang["none"], "Espion", "Religieux", "Scientifique", "Contrebandier", "Bureaucrate", "Militaire", "Federation du commerce", "Adphyra-Core"]### HARDCODED - TO BE REMOVED
        success, selection = await ui.send_dropdown(ctx, placeholder=data.lang["dropdown_org_placeholder"], timeout=60, options=orgs, select_msg=data.lang["affiliate"], timeout_msg=data.lang["timeout"], format_args_before=[char])

        if success:
            self.logger.info(selection)
        # char.affiliate(affiliation)
        # self.logger.log(logging.DEBUG+1,"/char affiliate (%s with %s) in channel %d of server %d",char.key,affiliation,ctx.message.channel.id,ctx.message.guild.id)
        # if affiliation is None:
        #     await ctx.channel.send(data.lang["unaffiliate"].format(char.name))
        # else:
        #     await ctx.channel.send(data.lang["affiliate"].format(char.name,affiliation))
