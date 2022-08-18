#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from telegramma.api import Module, assert_min_api_version

assert_min_api_version(1)

from telegram import BotCommand
from telegram.ext import CommandHandler

from telegramma.modules.lineageos_updates.main import (
	lineageos_updates,
)
from telegramma.modules.lineageos_updates.observer import (
	Observer,
)

class LineageOSUpdatesModule(Module):
	NAME = "lineageos_updates"
	VERSION = "1.0"
	HANDLERS = [
		CommandHandler(["lineageos_updates"], lineageos_updates),
	]
	COMMANDS = [
		BotCommand("lineageos_updates", "Get information about the LineageOS updates poster"),
	]
	TASKS = [
		Observer.task,
	]

module = LineageOSUpdatesModule()
