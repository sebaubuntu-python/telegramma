#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from telegramma.api import Module, assert_min_api_version

assert_min_api_version(1)

from telegram import BotCommand
from telegram.ext import CommandHandler

from telegramma.modules.twrpdtgen.main import (
	twrpdtgen,
)

class TwrpdtgenModule(Module):
	NAME = "twrpdtgen"
	VERSION = "1.0"
	HANDLERS = [
		CommandHandler(["twrpdtgen"], twrpdtgen),
	]
	COMMANDS = [
		BotCommand("twrpdtgen", "Generate a TWRP device tree from a recovery or boot image direct link"),
	]

module = TwrpdtgenModule()
