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
from core.commandparameters import GenericCommandParameters
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
    @commands.hybrid_group(invoke_without_command=False, aliases=['char'], guild_only=True)
    async def character(self, ctx): pass

    #@commands.check(check_haschar)
    @commands.cooldown(1, 5, commands.BucketType.user)
    @character.command(name="select", aliases=["switch"])
    async def character_select(self, ctx): #(self, ctx, key)
        """**PC/PJ only**
        Select a character from all characters linked to you"""
        async def _on_select(dropdown, interaction):
            await interaction.response.edit_message(content=data.lang["charselect"].format("undefined", dropdown.value), view=None)
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
        dropdown = ui.StandaloneDropdown(ctx, placeholder=data.lang["charselect_placeholder"], timeout=60, options=chars, onselection=_on_select)
        await ctx.send(view=dropdown.view, reference=ctx.message)
        await dropdown.wait()
        self.logger.info(dropdown.value)
