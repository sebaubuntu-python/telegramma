#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from telegramma.api import Module, assert_min_api_version

assert_min_api_version(1)

from telegram import BotCommand
from telegram.ext import CommandHandler

from telegramma.modules.translate.main import (
	translate,
)

class TranslateModule(Module):
	NAME = "translate"
	VERSION = "1.0"
	HANDLERS = [
		CommandHandler(["translate"], translate),
	]
	COMMANDS = [
		BotCommand("translate", "Reply to a message to translate it to another language"),
	]

module = TranslateModule()
