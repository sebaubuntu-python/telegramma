#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from telegramma.api import Module, assert_min_api_version

assert_min_api_version(1)

from telegram import BotCommand
from telegram.ext import CommandHandler

from telegramma.modules.fun.main import (
	roll,
	slap,
	whatis,
	xda,
)

class FunModule(Module):
	NAME = "fun"
	VERSION = "1.0"
	HANDLERS = [
		CommandHandler(["roll"], roll),
		CommandHandler(["slap"], slap),
		CommandHandler(["whatis"], whatis),
		CommandHandler(["xda"], xda),
	]
	COMMANDS = [
		BotCommand("roll", "Roll a magic ball"),
		BotCommand("slap", "Slap someone"),
		BotCommand("whatis", "Check the definition of something"),
		BotCommand("xda", "Let a general XDA user speak"),
	]

module = FunModule()
