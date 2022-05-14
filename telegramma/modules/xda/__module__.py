#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from telegramma.api import Module, assert_min_api_version

assert_min_api_version(1)

from telegram import BotCommand
from telegram.ext import CommandHandler

from telegramma.modules.xda.main import (
	xda,
)

class XdaModule(Module):
	NAME = "xda"
	VERSION = "1.0"
	HANDLERS = [
		CommandHandler(["xda"], xda),
	]
	COMMANDS = [
		BotCommand("xda", "Let a general XDA user speak"),
	]

module = XdaModule()
