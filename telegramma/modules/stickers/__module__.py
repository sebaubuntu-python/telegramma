#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from telegramma.api import Module, assert_min_api_version

assert_min_api_version(1)

from telegram import BotCommand
from telegram.ext import CommandHandler

from telegramma.modules.stickers.main import (
	stickers,
)

class StickersModule(Module):
	NAME = "stickers"
	VERSION = "1.0"
	HANDLERS = [
		CommandHandler(["stickers"], stickers),
	]
	COMMANDS = [
		BotCommand("stickers", "Shared sticker sets management"),
	]

module = StickersModule()
