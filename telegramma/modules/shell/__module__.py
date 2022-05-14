#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from telegramma.api import Module, assert_min_api_version

assert_min_api_version(1)

from telegram import BotCommand
from telegram.ext import CommandHandler

from telegramma.modules.shell.main import (
	shell,
)

class ShellModule(Module):
	NAME = "shell"
	VERSION = "1.0"
	CORE: True
	HANDLERS = [
		CommandHandler(["shell"], shell),
	]
	COMMANDS = [
		BotCommand("shell", "Execute a command in the bot's environment"),
	]

module = ShellModule()
