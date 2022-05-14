#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from telegramma.api import Module, assert_min_api_version

assert_min_api_version(1)

from telegram import BotCommand
from telegram.ext import CommandHandler

from telegramma.modules.info.main import (
	info,
)

class InfoModule(Module):
	NAME = "info"
	VERSION = "1.0"
	HANDLERS = [
		CommandHandler(["info"], info),
	]
	COMMANDS = [
		BotCommand("info", "Get information about a message or a user or a chat"),
	]

module = InfoModule()
