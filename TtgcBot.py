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

# import external and python libs
import discord
import traceback
import os
import sys

# set path
sys.path.append(os.path.abspath("src"))

# import custom libs
from setup.inits import init
from setup.logconfig import get_logger
from setup.loglevel import LogLevel
from setup.config import Config
from utils.translator import get_lang, lang_exist
# from src.utils.inits import *
# from src.utils.config import *
# from src.tools.BotTools import *
# from src.tools.Translator import *
# from src.utils.checks import *
# from src.exceptions.exceptions import *
# from src.help import *

# import Cogs
from cogs import jdr, BotManage
# from src.cogs.Moderation import *
# from src.cogs.Other import *
# from src.cogs.NSFW import *
# from src.cogs.Vocal import *
# from src.cogs.jdr.MainJDR import *
# from src.cogs.jdr.CharacterCog import *
# from src.cogs.jdr.SkillCog import *
# from src.cogs.jdr.MJ import *
# from src.cogs.jdr.PetCog import *
# from src.cogs.jdr.JDRGlobal import *
# from src.cogs.jdr.Finalize import *
# from src.cogs.jdr.Maps import *
# from src.cogs.jdr.InventoryCog import *

# Initialize bot status
global status
status = discord.Game(name=Config()["discord"]["default-game"])

# Get prefix function
# async def get_prefix(bot, message):
#     try:
#         srv = await DBServer(message.guild.id)
#         return srv.prefix
#     except (AttributeError, DatabaseException): return Config()["discord"]["default-prefix"]

# Initialize client
global client
client = discord.ext.commands.Bot(Config()["discord"]["default-prefix"], case_insensitive=True, activity=status, intents=discord.Intents.all())

# Global checks
@client.check
def no_pm(ctx):
    return ctx.message.guild is not None

@client.check
def isbot(ctx):
    return not ctx.message.author.bot

# @client.check
# async def blacklist(ctx):
#     srv = DBServer(str(ctx.message.guild.id))
#     blacklisted, reason = await is_blacklisted(ctx.message.author.id)
#     if blacklisted:
#         lgcode = await getuserlang(ctx.message.author.id)
#         if not lang_exist(lgcode): lgcode = "EN"
#         lang = get_lang(lgcode)
#         await ctx.message.channel.send(lang["blacklisted"].format(ctx.message.author.mention, reason))
#     return not blacklisted

# Client events
@client.event
async def on_command_error(ctx, error):
    logger = get_logger()
    lgcode = "EN" #getuserlang(str(ctx.message.author.id))
    if not lang_exist(lgcode): lgcode = "EN"
    lang = get_lang(lgcode)
    msg = lang["error"].format(error)

    # if isinstance(error, commands.CommandNotFound): msg = lang["error_notfound"]
    # elif isinstance(error, commands.MissingPermissions): msg = lang["error_selfperms"]
    # elif isinstance(error, commands.BotMissingPermissions): msg = lang["error_perms"]
    # elif isinstance(error, commands.NSFWChannelRequired): msg = lang["error_nsfw"]
    # elif isinstance(error, commands.DisabledCommand): msg = lang["error_disabled"]
    # elif isinstance(error, commands.CheckFailure): return
    # elif isinstance(error, commands.UserInputError): msg = lang["error_argument"]
    # elif isinstance(error, commands.CommandOnCooldown): msg = lang["error_cd"].format("{0:.2f}".format(error.retry_after))
    # elif isinstance(error, commands.APIException):
    #     logger.warning(error)
    #     msg = error.parse(lang)
    # elif isinstance(error, commands.HTTPException):
    #     logger.warning(error)
    #     msg = error.parse(lang)
    # else:

    logger.warning(error)
    await ctx.message.channel.send(msg)

# @client.event
# async def on_guild_join(guild):
#     logger = get_logger()
#     await DBServer.addserver(guild)
#     try: logger.info("Added server '%s' to the database : ID=%d", str(guild), guild.id)
#     except: logger.info("Added server to the database : ID=%d", guild.id)

# @client.event
# async def on_guild_remove(guild):
#     logger = get_logger()
#     srv = await DBServer(guild.id)
#     await srv.remove()
#     logger.info("Removed server from the database : ID=%d", guild.id)

@client.event
async def on_error(event, *args, **kwargs):
    global client
    logger = get_logger()
    logger.error(traceback.format_exc())
    # infos = await client.application_info()
    # await infos.owner.send(get_lang()["error"].format(traceback.format_exc(limit=100)))
    client.get_cog("Bot Management").handlederror += 1

@client.event
async def on_connect():
    if len(client.cogs) > 0: return

    logger = get_logger()
    await client.add_cog(BotManage(client, logger))
    await client.add_cog(jdr.CharacterCog(client, logger))

    test_guild = Config()['discord']['test-guild']
    if test_guild is not None:
        logger.log(LogLevel.BOT_V3.value, f"Test guild provided. Copying global command to test guild.")
        client.tree.copy_global_to(guild=discord.Object(id=test_guild))

    await client.tree.sync()
    # client.add_cog(Moderation(client, logger))
    # client.add_cog(Other(client, logger))
    # client.add_cog(NSFW(client, logger))
    # client.add_cog(Vocal(client, logger))
    # client.add_cog(MainJDR(client, logger))
    # client.add_cog(CharacterCog(client, logger))
    # client.add_cog(SkillCog(client, logger))
    # client.add_cog(PetCog(client, logger))
    # client.add_cog(JDRGlobal(client, logger))
    # client.add_cog(Finalize(client, logger))
    # client.add_cog(Maps(client, logger))
    # client.add_cog(InventoryCog(client, logger))
    # client.add_cog(MJ(client, logger))

@client.event
async def on_ready():
    logger = get_logger()
    logger.info("Successful connected. Initializing bot system")
    botaskperm = discord.Permissions().all()
    botaskperm.administrator = botaskperm.manage_channels = botaskperm.manage_guild = botaskperm.manage_webhooks = botaskperm.manage_emojis = botaskperm.manage_nicknames = botaskperm.move_members = False
    url = discord.utils.oauth_url(client.user.id, permissions=botaskperm)
    logger.info("Generated invite link : %s", url)
    # srvid, nbr = [], 0
    # srvlist = await DBServer.srvlist()
    # for i in client.guilds:
    #     srvid.append(i.id)
    #     if i.id not in srvlist:
    #         await DBServer.addserver(i)
    #         nbr += 1
    #         try: logger.info("This server has invited the bot during off period, adding it to the database : %s (ID=%d)", str(i), i.id)
    #         except: logger.info("Server added (ID=%d)", i.id)
    # logger.info("Added %d new servers to the database successful", nbr)
    # logger.info("Purged %d servers wich have kicked the bot at least one year ago successful", DBServer.purgeservers(365))
    # nbr = 0
    # for i in srvlist:
    #     if i not in srvid:
    #         srv = await DBServer(i)
    #         await srv.remove()
    #         nbr += 1
    #         logger.info("This server has kicked the bot during off period, removing it from the database : ID=%s", str(i))
    # logger.info("Removed %d old servers from the database successful", nbr)
    logger.info("Bot is now ready")

@client.event
async def on_resumed():
    # global status, client
    logger = get_logger()
    logger.info("Resumed session")
    # botmanagecog = client.get_cog("Bot Management")
    # if botmanagecog and botmanagecog.status:
    #     status = botmanagecog.status
    # await self.bot.change_presence(activity=self.status)

# ========== MAIN ========== #
def main():
    logger = init()
    logger.info("Starting TtgcBot 3.0")
    client.run(Config()["token"])

# Launch the bot
if __name__ == "__main__":
    main()
