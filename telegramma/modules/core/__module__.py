#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from telegramma.api import Module, assert_min_api_version

assert_min_api_version(1)

from telegram import BotCommand
from telegram.ext import CommandHandler

from telegramma.modules.core.main import (
	start,
	modules,
	enable,
	disable,
	restart,
	shutdown,
)

class CoreModule(Module):
	NAME = "core"
	VERSION = "1.0"
	CORE: True
	HANDLERS = [
		CommandHandler(["start", "help"], start),
		CommandHandler(["modules"], modules),
		CommandHandler(["enable"], enable),
		CommandHandler(["disable"], disable),
		CommandHandler(["restart"], restart),
		CommandHandler(["shutdown"], shutdown),
	]
	COMMANDS = [
		BotCommand("start", "Bot start point"),
		BotCommand("help", "Get help about the bot"),
		BotCommand("modules", "List of modules"),
		BotCommand("enable", "Enable a module"),
		BotCommand("disable", "Disable a module"),
		BotCommand("restart", "Restart the bot"),
		BotCommand("shutdown", "Shutdown the bot"),
	]

module = CoreModule()
