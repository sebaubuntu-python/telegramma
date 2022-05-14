#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from telegramma.api import Module, assert_min_api_version

assert_min_api_version(1)

from telegram import BotCommand
from telegram.ext import CommandHandler

from telegramma.modules.speedtest.main import (
	speedtest,
)

class SpeedtestModule(Module):
	NAME = "speedtest"
	VERSION = "1.0"
	HANDLERS = [
		CommandHandler(["speedtest"], speedtest),
	]
	COMMANDS = [
		BotCommand("speedtest", "Do a speedtest (will return the bot's machine Internet connection speed)"),
	]

module = SpeedtestModule()
