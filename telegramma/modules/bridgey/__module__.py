#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from telegramma.api import Module, assert_min_api_version

assert_min_api_version(2)

from telegram import BotCommand
from telegram.ext import CommandHandler, MessageHandler
from telegram.ext.filters import UpdateType

from telegramma.modules.bridgey.main import (
	bridgey,
	handle_telegram_update,
)
from telegramma.modules.bridgey.task import bridgey_task
from telegramma.modules.bridgey.telegram_queue import to_telegram_task

class BridgeyModule(Module):
	NAME = "bridgey"
	VERSION = "1.0"
	HANDLERS = [
		CommandHandler(["bridgey"], bridgey),
		MessageHandler(UpdateType.MESSAGE, handle_telegram_update),
	]
	COMMANDS = [
		BotCommand("bridgey", "Get information about the status of the bridge"),
	]
	TASKS = [
		bridgey_task,
		to_telegram_task,
	]

module = BridgeyModule()
