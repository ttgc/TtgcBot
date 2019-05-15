#!usr/bin/env python3.7
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

import discord
from discord.ext import commands
from src.utils.checks import GenericCommandParameters

class Help(commands.HelpCommand):
    def __init__(self):
        commands.HelpCommand.__init__(self)
        self.data = None

    async def prepare_help_command(self,ctx,command=None):
        self.context = ctx
        self.cog = self.context.bot.get_cog("Other")
        self.data = GenericCommandParameters(self.context)

    async def command_not_found(self,string):
        return self.data.lang["error_help_notfound"].format(string)

    async def subcommand_not_found(self,command,string):
        if isinstance(command,commands.Group):
            return self.data.lang["error_help_subnotfound"].format(command.qualified_name,string)
        return self.data.lang["error_help_subnone"].format(command.qualified_name)

    async def send_bot_help(self,mapping):
        embd = discord.Embed(title="TtgcBot",description=self.data.lang["help"],colour=discord.Color(int('5B005B',16)),url="https://ttgc.github.io/TtgcBot/")
        embd.set_footer(text="Made by Ttgc")
        embd.set_author(name="TtgcBot",icon_url=self.context.bot.user.avatar_url)
        for i,k in mapping.items():
            k = await self.filter_commands(k,sort=True)
            ls = []
            for cmd in k:
                ls.append(cmd.qualified_name)
            if len(ls) == 0: ls = ["None"]
            if i is not None: embd.add_field(name=i.qualified_name,value="\n".join(ls),inline=True)
        await self.get_destination().send(embed=embd)

    async def send_cog_help(self,cog):
        embd = discord.Embed(title="TtgcBot",description=self.data.lang["help"]+" : "+cog.qualified_name,colour=discord.Color(int('5B005B',16)),url="https://ttgc.github.io/TtgcBot/")
        embd.set_footer(text="Made by Ttgc")
        embd.set_author(name="TtgcBot",icon_url=self.context.bot.user.avatar_url)
        ls = await self.filter_commands(cog.get_commands(),sort=True)
        for i in ls:
            embd.add_field(name=i.qualified_name,value=self.get_command_signature(i),inline=True)
        await self.get_destination().send(embed=embd)

    async def send_command_help(self,command):
        embd = discord.Embed(title="TtgcBot",description=self.data.lang["help"]+" : "+command.qualified_name,colour=discord.Color(int('5B005B',16)),url="https://ttgc.github.io/TtgcBot/")
        embd.set_footer(text="Made by Ttgc")
        embd.set_author(name="TtgcBot",icon_url=self.context.bot.user.avatar_url)
        embd.add_field(name=self.data.lang["help_proto"]+" :",value=self.get_command_signature(command),inline=False)
        embd.add_field(name=self.data.lang["help_descr"]+" :",value=command.help,inline=False)
        await self.get_destination().send(embed=embd)

    async def send_group_help(self,group):
        embd = discord.Embed(title="TtgcBot",description=self.data.lang["help"]+" : "+group.qualified_name,colour=discord.Color(int('5B005B',16)),url="https://ttgc.github.io/TtgcBot/")
        embd.set_footer(text="Made by Ttgc")
        embd.set_author(name="TtgcBot",icon_url=self.context.bot.user.avatar_url)
        for cmd in group.commands:
            embd.add_field(name=cmd.qualified_name,value=self.get_command_signature(cmd),inline=True)
        await self.get_destination().send(embed=embd)
