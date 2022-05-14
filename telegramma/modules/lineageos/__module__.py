#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from telegramma.api import Module, assert_min_api_version

assert_min_api_version(1)

from telegram import BotCommand
from telegram.ext import CommandHandler

from telegramma.modules.lineageos.main import (
	lineageos,
)

class LineageOSModule(Module):
	NAME = "lineageos"
	VERSION = "1.0"
	HANDLERS = [
		CommandHandler(["lineageos"], lineageos),
	]
	COMMANDS = [
		BotCommand("lineageos", "LineageOS OTA and wiki utils"),
	]

module = LineageOSModule()
